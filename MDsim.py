"""
Run molecular dynamics simulations of protein or protein/ligand complex with openmm and openff force fields.
"""

import argparse, time, sys
from openmm import unit

def bond(s):
    a,b = map(int,s.split(','))
    return (a,b)

t0 = time.time()
sys_setup = 0
disclaimer = \
"***********************************************************************************************************\n\
* Script made by Stijn De Schepper, as part of the master thesis 2024 at the UGent-PRU research group     *\n\
* and available at https://github.com/stdschep/MD-simulation-of-protein-ligand-complexes-with-OpenMM.git. *\n\
*                                                                                                         *\n\
* Please cite following papers:                                                                           *\n\
* 1. Dudgeon, T. & Chodera, J.                                                                            *\n\
* tdudgeon/simple-simulate-complex. (2024)                                                                *\n\
* https://github.com/tdudgeon/simple-simulate-complex                                                     *\n\
* 2. Eastman, P. et al.                                                                                   *\n\
* OpenMM 8: Molecular Dynamics Simulation with Machine Learning Potentials.                               *\n\
* ArXiv arXiv:2310.03121v2 (2023).                                                                        *\n\
* 3. Wagner, J. et al.                                                                                    *\n\
* openforcefield/openff-toolkit: 0.15.2 Minor feature release.                                            *\n\
* Zenodo https://doi.org/10.5281/zenodo.10613658 (2024).                                                  *\n\
* 4. McGibbon, R. T. et al.                                                                               *\n\
* MDTraj: A Modern Open Library for the Analysis of Molecular Dynamics Trajectories.                      *\n\
* Biophysical Journal 109, 1528–1532 (2015).                                                              *\n\
***********************************************************************************************************\n"

parser = argparse.ArgumentParser(description=disclaimer, fromfile_prefix_chars='@')


parser.add_argument("-a", "--simulation", required=True,
                    choices=["Protein", "Complex"],
                    help="What simulation do you want to run.")
parser.add_argument("-p", "--protein", help="Protein PDB file")
parser.add_argument("-l", "--ligand", required='--simulation' == 'Complex', help="Ligand mol file")
parser.add_argument("-c", "--complex", help='Load a previous assembled complex')
parser.add_argument("-s", "--system", default=None, help='Load a previous configured system')
parser.add_argument("-o", "--output", required=True, help="Base name for output files")
parser.add_argument("-e", "--steps", type=int, default=5000, help="Number of steps")
parser.add_argument("-z", "--step-size", type=float, default=0.002, help="Step size (ps")
parser.add_argument("-f", "--friction-coeff", type=float, default=1, help="Friction coefficient (ps)")
parser.add_argument("-i", "--interval", type=int, default=1000, help="Reporting interval")
parser.add_argument("-t", "--temperature", type=int, default=300, help="Temperature (K)")
parser.add_argument("--cleanup-protein", action='store_true', help='Clean-up the simulation protein')
parser.add_argument("--solvate", action='store_true', help="Add solvent box")
parser.add_argument("--padding", type=float, default=10, help="Padding for solvent box (A)")
parser.add_argument("--water-model", default="tip3p",
                    choices=["tip3p", "spce", "tip4pew", "tip5p", "swm4ndp"],
                    help="Water model for solvation")
parser.add_argument("--positive-ion", default="Na+", help="Positive ion for solvation")
parser.add_argument("--negative-ion", default="Cl-", help="Negative ion for solvation")
parser.add_argument("--ionic-strength", type=float, default="0", help="Ionic strength for solvation")
parser.add_argument("--pH", type=float, default=3.5, help='pH of simulation environment when adding H-atoms')
parser.add_argument("--no-neutralize", action='store_true', help="Don't add ions to neutralize")
parser.add_argument("--equilibration-steps", type=int, default=200, help="Number of equilibration steps")
parser.add_argument("-pf", "--protein-force-field", default='amber/ff14SB.xml', help="Protein force field")
parser.add_argument("-lf", "--ligand-force-field", default='gaff-2.11', help="Ligand force field")
parser.add_argument("-wf", "--water-force-field", default='amber/tip3p_standard.xml', help="water force field")

parser.add_argument("--restrain", help="Restrain atoms using a harmonic force")
parser.add_argument("--restrain-strength", type=int,default=200, help='Strength of the harmonic force')
parser.add_argument("--custom-bond", type=bond, help="Create a bond between given atoms")
parser.add_argument("--bond-strength", type=int,default=259407, help='Strength of the created bond')


# write the output to a log text file
args = parser.parse_args()
logfile = args.output + '_log.txt'
sys.stdout = open(logfile, 'w')

# docstring
print(disclaimer)

# print the simulations parameters
print("Run MD simulation with: ", args)
print("*"*107)

restrain = args.restrain.split(',')
bounding = args.custom_bond
num_steps = args.steps
step_size = args.step_size * unit.picoseconds
duration = (step_size * num_steps).value_in_unit(unit.nanoseconds)
import utils

# simulate protein
if args.simulation == 'Protein':
    t1 = time.time()
    print('Simulating protein ', args.protein, 'for ', duration)
    utils.run_protein(
        protein=args.protein,
        output=args.output,
        system=args.system,
        steps=args.steps,
        step_size=args.step_size,
        friction_coeff=args.friction_coeff,
        interval=args.interval,
        temperature=args.temperature,
        solvate=args.solvate,
        padding=args.padding,
        water_model=args.water_model,
        ion_p=args.positive_ion,
        ion_n=args.negative_ion,
        ion_s=args.ionic_strength,
        neutralize=args.no_neutralize,
        equilibration_steps=args.equilibration_steps,
        protein_force_field=args.protein_force_field,
        water_force_field=args.water_force_field,
        cleanup=args.cleanup_protein,
        pH=args.pH,
        restrain=restrain,
        restrain_strength=args.restrain_strength
        )
# simulate protein/ligand
elif args.simulation == 'Complex':
    ## configure new system
    if args.system is None:
        print('Prepearing simulation system for complex of ', args.protein, 'and ', args.ligand)
        t1 = time.time()
        system = utils.config_sys(
            protein=args.protein,
            ligand=args.ligand,
            output=args.output,
            temperature=args.temperature,
            solvate=args.solvate,
            padding=args.padding,
            water_model=args.water_model,
            ion_p=args.positive_ion,
            ion_n=args.negative_ion,
            ion_s=args.ionic_strength,
            neutralize=args.no_neutralize,
            protein_force_field=args.protein_force_field,
            ligand_force_field=args.ligand_force_field,
            water_force_field=args.water_force_field,
            restrain=restrain,
            bounding=bounding,
            restrain_strength=args.restrain_strength,
            bond_strength=args.bond_strength
        )
        #system = args.output + '_system.xml'
        complex = args.output + '_complex.pdb'
        t2 = time.time()
        sys_setup = round((t1-t2)/60, 3)
    # load system
    else:
        system = args.system
        print('Simulating complex using ', args.complex, 'and ', args.system, 'for ', duration)
        sys_setup = 0
    t1 = time.time()
    # run simulation
    utils.run_complex(
        system=system,
        complex=args.complex,
        output=args.output,
        friction_coeff=args.friction_coeff,
        steps=args.steps,
        step_size=args.step_size,
        equilibration_steps=args.equilibration_steps,
        temperature=args.temperature,
        interval=args.interval
    )
t2 = time.time()
# Report times
print('System configuration complete in {} mins. Simulation complete in {} mins.'.format(
    sys_setup, round((t2 - t1) / 60, 3)))
print('Total wall clock time was {} mins'.format(round((t2 - t0) / 60, 3)))
print('Simulation time was', round(duration, 3), 'ns')
