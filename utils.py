
import os, sys, time
sys.path.append('/data/gent/473/vsc47370/python_lib/lib/python3.10/site-packages')

from openff.toolkit import Molecule
from openmmforcefields.generators import SystemGenerator
import openmm
from openmm import app, unit, LangevinIntegrator, Vec3, Platform, LangevinMiddleIntegrator, MonteCarloBarostat
from openmm.app import PDBFile, Simulation, Modeller, PDBReporter, StateDataReporter, DCDReporter, ForceField


def get_platform():
    os_platform = os.getenv('PLATFORM')
    if os_platform:
        platform = Platform.getPlatformByName(os_platform)
    else:
        # work out the fastest platform
        speed = 0
        for i in range(Platform.getNumPlatforms()):
            p = Platform.getPlatform(i)
            # print(p.getName(), p.getSpeed())
            if p.getSpeed() > speed:
                platform = p
                speed = p.getSpeed()

    print('Using platform', platform.getName())

    # if it's GPU platform set the precision to mixed
    if platform.getName() == 'CUDA' or platform.getName() == 'OpenCL':
        platform.setPropertyDefaultValue('Precision', 'mixed')
        print('Set precision for platform', platform.getName(), 'to mixed')

    return platform

def restraining(pdb, target):
    residue_atoms = list()
    for i in target:
        try:
            residue, nr = i.split('-')
        except:
            for atom in pdb.topology.atoms():
                if atom.name == i:
                    residue_atoms.append(atom.index)
                    print(f'restraining {atom}')
        else:
            if residue in ('ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS','MET','PHE','PRO',
                            'SER','THR','TRP','TYR','VAL'):
                for atom in pdb.topology.atoms():
                    if atom.residue.name == residue.upper() and atom.residue.index == int(nr):
                        residue_atoms.append(atom.index)
                        print(f'restraining {atom}')
            elif residue == 'UNK':
                for atom in pdb.topology.atoms():
                    if atom.index == int(nr):
                        residue_atoms.append(atom.index)
                        print(f'restraining {atom}.')
            else:
                print('Residue is not present in protein or ligand. Make sure you use the 3-letter amino acid codes. \
                Ligand positions must be precede by "UNK"')
    return residue_atoms

def atom_index(pdb,id):
    for atom in pdb.topology.atoms():
        if atom.id == str(id):
            return atom.index

def cleanup_protein(pdb,
                    pH):
    from pdbfixer import PDBFixer
    print('Cleaning protein...')
    fixer = PDBFixer(filename=pdb)
    fixer.findMissingResidues()
    fixer.findMissingAtoms()
    fixer.findNonstandardResidues()
    print('Residues:', fixer.missingResidues)
    print('Atoms:', fixer.missingAtoms)
    print('Terminals:', fixer.missingTerminals)
    print('Non-standard:', fixer.nonstandardResidues)

    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(pH)
    fixer.removeHeterogens(False)
    return fixer
def config_sys(
    protein, ligand, output, 
    temperature,
    solvate,
    padding,
    water_model,
    ion_p, ion_n, ion_s,
    neutralize,
    ligand_force_field,
    protein_force_field,
    water_force_field,
    restrain,
    bounding,
    restrain_strength,
    bond_strength
    ):
    """
    Configure the openmm system for a protein/ligand complex.
    """
    # get the chosen or fastest platform
    platform = get_platform()
    output_system = output + '_system.xml'
    output_complex = output + '_complex.pdb'
    
    print('Reading ligand')
    ligand_mol = Molecule.from_file(ligand)

    print('Preparing system...')
    # Initialize a SystemGenerator using the GAFF for the ligand and tip3p for the water.
    forcefield_kwargs = {'constraints': app.HBonds, 'rigidWater': True, 'removeCMMotion': False, 'hydrogenMass': 4*unit.amu }
    system_generator = SystemGenerator(
        forcefields=[protein_force_field, water_force_field],
        small_molecule_forcefield=ligand_force_field,
        molecules=[ligand_mol],
        forcefield_kwargs=forcefield_kwargs)

    # Use Modeller to combine the protein and ligand into a complex
    print('Reading protein')
    protein_pdb = PDBFile(protein)

    print('Preparing complex...')
    # The topology is described in the openforcefield API

    modeller = Modeller(protein_pdb.topology, protein_pdb.positions)
    print('System has %d atoms' % modeller.topology.getNumAtoms())

    # The topology is described in the openforcefield API
    print('Adding ligand...')
    lig_top = ligand_mol.to_topology()
    modeller.add(lig_top.to_openmm(), lig_top.get_positions().to_openmm())
    print('System has %d atoms' % modeller.topology.getNumAtoms())

    # Solvate
    if solvate:
        print('Adding solvent...')
        # we use the 'padding' option to define the periodic box.
        # we just create a box that has a 10A (default) padding around the complex.
        modeller.addSolvent(system_generator.forcefield, model=water_model, padding=padding * unit.angstroms,
                            positiveIon=ion_p, negativeIon=ion_n,
                            ionicStrength=ion_s * unit.molar, neutralize=not neutralize)
        print('System has %d atoms' % modeller.topology.getNumAtoms())

    with open(output_complex, 'w') as outfile:
        PDBFile.writeFile(modeller.topology, modeller.positions, outfile)

    # Create the system using the SystemGenerator
    print("Generating system...")
    system = system_generator.create_system(modeller.topology, molecules=ligand_mol)
    if restrain:
        # add a restraining force to prevent atoms moving too far from their starting positions
        print('setting up restraintment')
        formula = 'k*periodicdistance(x, y, z, x0, y0, z0)^2'
        k = restrain_strength
        print(f'using "{formula}" as harmonic force, with "k" = {k} kJ/mol/nm')
        restraint = openmm.CustomExternalForce(formula)
        system.addForce(restraint)
        restraint.addGlobalParameter('k', k * unit.kilojoules_per_mole / unit.nanometer)
        restraint.addPerParticleParameter('x0')
        restraint.addPerParticleParameter('y0')
        restraint.addPerParticleParameter('z0')

        print("applying forces to atoms...")
        target = restrain
        atom_index = restraining(modeller, target)
        for index in atom_index:
            restraint.addParticle(index, modeller.positions[index])
    if bounding:
        # Adding custom bonds between 2 atoms
        print("setting up bonding...")
        formula = '0.5*k*(r-r0)^2'
        k = bond_strength
        print(f'using "{formula}" as harmonic force, with "k" = {k} kJ mol^(-1) nm^(-1)')
        force = openmm.CustomBondForce(formula)
        force.addGlobalParameter("k", k * unit.kilojoules_per_mole / unit.nanometer)
        force.addPerBondParameter("r0")

        print("assigning bonds between atoms...")
        target = bounding
        for p1, p2 in target:
            force.addBond(int(p1), int(p2))
            print(f'bond added between atom {p1} and atom {p2}')

    if solvate:
        system.addForce(openmm.MonteCarloBarostat(1 * unit.atmospheres, temperature, 25))

    if system.usesPeriodicBoundaryConditions():
        print('Default Periodic box: {}'.format(system.getDefaultPeriodicBoxVectors()))
    else:
        print('No Periodic Box')

    print('Writing system to', output_system)
    with open(output_system, 'w') as output:
        output.write(openmm.XmlSerializer.serialize(system))
    
    return openmm.XmlSerializer.serialize(system)

def run_complex(
    system,
    complex,
    output,
    friction_coeff,
    steps,
    step_size,
    equilibration_steps,
    temperature,
    interval
    ):
    """
    Run openmm simulation of a protein/ligand complex
    """
    # get the chosen or fastest platform
    platform = get_platform()
    output_min = output + '_minimized.pdb'
    output_traj_dcd = output + '_traj.dcd'

    temperature = temperature * unit.kelvin
    num_steps = steps
    reporting_interval = interval
    # load the system
    print("Loading system...")
    with open(system) as input:
        system = openmm.XmlSerializer.deserialize(input.read())
    friction_coeff = friction_coeff / unit.picoseconds
    step_size = step_size * unit.picoseconds
    duration = (step_size * num_steps).value_in_unit(unit.nanoseconds)
    print('Simulating for {} ns'.format(duration))

    integrator = LangevinIntegrator(temperature, friction_coeff, step_size)
    complex_pdb = PDBFile(complex)
    modeller = Modeller(complex_pdb.topology, complex_pdb.positions)

    simulation = Simulation(modeller.topology, system, integrator, platform=platform)
    context = simulation.context
    context.setPositions(modeller.positions)

    print('Minimising ...')
    simulation.minimizeEnergy()

    # Write out the minimised PDB.
    with open(output_min, 'w') as outfile:
        PDBFile.writeFile(modeller.topology, context.getState(getPositions=True, enforcePeriodicBox=True).getPositions(), file=outfile, keepIds=True)

    # equilibrate
    simulation.context.setVelocitiesToTemperature(temperature)
    print('Equilibrating ...')
    simulation.step(equilibration_steps)

    # Run the simulation.
    simulation.reporters.append(DCDReporter(output_traj_dcd, reporting_interval, enforcePeriodicBox=True))
    simulation.reporters.append(StateDataReporter(sys.stdout, reporting_interval * 5, step=True, potentialEnergy=True,
                                                  kineticEnergy=True, totalEnergy=True, temperature=True))
    print('Starting simulation with', num_steps, 'steps ...')
    simulation.step(num_steps)
    return

def run_protein(
    protein, output, system,
    steps,
    step_size,
    friction_coeff,
    interval,
    temperature,
    solvate,
    padding,
    water_model,
    ion_p, ion_n, ion_s,
    neutralize,
    equilibration_steps,
    protein_force_field,
    water_force_field,
    cleanup,
    pH,
    restrain,
    restrain_strength
    ):
    """
    Run openmm simulations of a protein
    """
    # get the chosen or fastest platform
    platform = get_platform()

    # Input Files
    input_system = system
    pdb = PDBFile(protein)
    forcefield = ForceField(protein_force_field, water_force_field)

    # Output files
    output_system = output +'_system.dcd'
    output_protein = output +'_protein.pdb'

    # System Configuration

    nonbondedMethod = app.PME
    nonbondedCutoff = 1.0*unit.nanometers
    ewaldErrorTolerance = 0.0005
    constraints = app.HBonds
    rigidWater = True
    constraintTolerance = 0.000001
    hydrogenMass = 1.5*unit.amu

    # Integration Options

    dt = step_size*unit.picoseconds
    temperature = temperature*unit.kelvin
    friction = friction_coeff/unit.picosecond
    pressure = 1.0*unit.atmospheres
    barostatInterval = 25

    # Simulation Options

    dcdReporter = DCDReporter(output_system, interval)
    dataReporter = StateDataReporter(sys.stdout, interval * 5, totalSteps=steps,
        step=True, progress=True, potentialEnergy=True, kineticEnergy=True, totalEnergy=True, temperature=True, separator='\t')
    modeller = Modeller(pdb.topology, pdb.positions)
    if cleanup:
        clean_protein = cleanup_protein(pdb,pH)
        modeller = Modeller(clean_protein.topology, clean_protein.positions)
    if solvate:
        print('Adding solvent...')
        # we use the 'padding' option to define the periodic box.
        # we just create a box that has a 10A (default) padding around the complex.
        modeller.addSolvent(forcefield, model=water_model, padding=padding * unit.angstroms,
                            positiveIon=ion_p, negativeIon=ion_n,
                            ionicStrength=ion_s * unit.molar, neutralize=not neutralize)
        print('System has %d atoms' % modeller.topology.getNumAtoms())
    if cleanup or solvate:
        with open(protein[:-4]+'_clean.pdb', 'w') as outfile:
            PDBFile.writeFile(modeller.topology, modeller.positions, file=outfile, keepIds=True)

    # Prepare the Simulation
    if input_system:
        print('Loading system...')
        with open(input_system) as input:
            system = openmm.XmlSerializer.deserialize(input.read())
    else:
        print('Building system...')
        system = forcefield.createSystem(modeller.topology, nonbondedMethod=nonbondedMethod, nonbondedCutoff=nonbondedCutoff,
            constraints=constraints, rigidWater=rigidWater, ewaldErrorTolerance=ewaldErrorTolerance, hydrogenMass=hydrogenMass)
    if restrain:
        # add a restraining force to prevent atoms moving too far from their starting positions
        print('setting up restraintment')
        formula = 'k*periodicdistance(x, y, z, x0, y0, z0)^2'
        k = restrain_strength
        print(f'using "{formula}" as harmonic force, with "k" = {k} kJ/mol/nm')
        restraint = openmm.CustomExternalForce(formula)
        system.addForce(restraint)
        restraint.addGlobalParameter('k', k * unit.kilojoules_per_mole / unit.nanometer)
        restraint.addPerParticleParameter('x0')
        restraint.addPerParticleParameter('y0')
        restraint.addPerParticleParameter('z0')

        print("applying forces to atoms...")
        target = restrain
        atom_index = restraining(modeller, target)
        for index in atom_index:
            restraint.addParticle(index, modeller.positions[index])

    system.addForce(MonteCarloBarostat(pressure, temperature, barostatInterval))
    integrator = LangevinMiddleIntegrator(temperature, friction, dt)
    integrator.setConstraintTolerance(constraintTolerance)
    simulation = Simulation(modeller.topology, system, integrator, platform)
    simulation.context.setPositions(modeller.positions)
    with open(output_system, 'w') as output:
        output.write(openmm.XmlSerializer.serialize(system))

    # Minimize and Equilibrate

    print('Performing energy minimization...')
    simulation.minimizeEnergy()
    print('Equilibrating...')
    simulation.context.setVelocitiesToTemperature(temperature)
    simulation.step(equilibration_steps)

    # Simulate

    print('Simulating...')
    simulation.reporters.append(dcdReporter)
    simulation.reporters.append(dataReporter)
    simulation.currentStep = 0
    simulation.step(steps)

    # Write file with final simulation state
    state = simulation.context.getState(getPositions=True, enforcePeriodicBox=system.usesPeriodicBoundaryConditions())
    with open(output_protein, mode="w") as file:
        PDBFile.writeFile(simulation.topology, state.getPositions(), file)
    return
