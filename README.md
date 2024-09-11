# Molecular Dynamics simulations

This repo is the result of effords to facilitate simulations of proteins and protein/ligand complexes using OpenMM. Additionally, the contents are optimized to run on the Flemish high performace computing infractstructure (VSC-HPC) at the UGent.
This repo includes:
1. A script to simulate proteins *
2. A script to simulate protein/ligand complexes **
3. A script to align and renumber the output **
4. A GUI interface to facilitate parameter input

\* Code based on output from [OpenMM-setup](https://github.com/openmm/openmm-setup.git)

** Code based on scripts from @tdudgeon's ['simple simulate complex'](https://github.com/tdudgeon/simple-simulate-complex.git)

## MDsim.py and utils.py

All inputs are handeled by the MDsim.py scrip, while utils.py handels the simulation operations. All possible simulations are handeled by MDsim.py

MDsim.py and untils.py are depended on:
* [openmm](https://openmm.org)
* [openmmforcefields](https://github.com/openmm/openmmforcefields/tree/main)
* [openfftoolkit](https://github.com/openforcefield/openff-toolkit/tree/main)

The simulation parameter (-a) differentiates between proteins and protein ligand complexes. Below shows the essential parameter for each case, observe the capital in **P**rotein and **C**omplex! The protein must be written in pdb format, while the ligand must be in MOL or SDF fomat. Output (-o) is used to name the outputted files.
```
$ python MDsim.py -a Protein -p protein.pdb -o output 
```
```
$ python MDsim.py -a Complex -p protein.pdb -l ligand.mol -o output 
```
Additional parameters can be assignt according to your specific simulation run. All parameters can be displayed by the help function (-h).
```
$ python MDsim -h
usage: MDsim.py [-h] -a {Protein,Complex} [-p PROTEIN] [-l LIGAND] [-c COMPLEX] [-s SYSTEM] -o OUTPUT [-e STEPS] [-z STEP_SIZE] [-f FRICTION_COEFF] [-i INTERVAL] [-t TEMPERATURE] [--cleanup-protein] [--solvate] [--padding PADDING]
                [--water-model {tip3p,spce,tip4pew,tip5p,swm4ndp}] [--positive-ion POSITIVE_ION] [--negative-ion NEGATIVE_ION] [--ionic-strength IONIC_STRENGTH] [--pH PH] [--no-neutralize]
                [--equilibration-steps EQUILIBRATION_STEPS] [-pf PROTEIN_FORCE_FIELD] [-lf LIGAND_FORCE_FIELD] [-wf WATER_FORCE_FIELD] [--restrain RESTRAIN] [--restrain-strength RESTRAIN_STRENGTH] [--custom-bond CUSTOM_BOND]        
                [--bond-strength BOND_STRENGTH]

Handeling of parameter input

optional arguments:
  -h, --help            show this help message and exit
  -a {Protein,Complex}, --simulation {Protein,Complex}
                        What simulation do you want to run.
  -p PROTEIN, --protein PROTEIN
                        Protein PDB file
  -l LIGAND, --ligand LIGAND
                        Ligand mol file
  -c COMPLEX, --complex COMPLEX
                        Load a previous assembled complex
  -s SYSTEM, --system SYSTEM
                        Load a previous configured system
  -o OUTPUT, --output OUTPUT
                        Base name for output files
  -e STEPS, --steps STEPS
                        Number of steps
  -z STEP_SIZE, --step-size STEP_SIZE
                        Step size (ps
  -f FRICTION_COEFF, --friction-coeff FRICTION_COEFF
                        Friction coefficient (ps)
  -i INTERVAL, --interval INTERVAL
                        Reporting interval
  -t TEMPERATURE, --temperature TEMPERATURE
                        Temperature (K)
  --cleanup-protein     Clean-up the simulation protein
  --solvate             Add solvent box
  --padding PADDING     Padding for solvent box (A)
  --water-model {tip3p,spce,tip4pew,tip5p,swm4ndp}
                        Water model for solvation
  --positive-ion POSITIVE_ION
                        Positive ion for solvation
  --negative-ion NEGATIVE_ION
                        Negative ion for solvation
  --ionic-strength IONIC_STRENGTH
                        Ionic strength for solvation
  --pH PH               pH of simulation environment when adding H-atoms
  --no-neutralize       Don't add ions to neutralize
  --equilibration-steps EQUILIBRATION_STEPS
                        Number of equilibration steps
  -pf PROTEIN_FORCE_FIELD, --protein-force-field PROTEIN_FORCE_FIELD
                        Protein force field
  -lf LIGAND_FORCE_FIELD, --ligand-force-field LIGAND_FORCE_FIELD
                        Ligand force field
  -wf WATER_FORCE_FIELD, --water-force-field WATER_FORCE_FIELD
                        water force field
  --restrain RESTRAIN   Restrain atoms using a harmonic force
  --restrain-strength RESTRAIN_STRENGTH
                        Strength of the harmonic force
  --custom-bond CUSTOM_BOND
                        Create a bond between given atoms
  --bond-strength BOND_STRENGTH
                        Strength of the created bond
```

## Analysis

The MD trajectories are analysed using the script analyse.py which uses [MDTraj](http://mdtraj.org/).

Usage:
```
$ python analyse.py -h
usage: analyse.py [-h] -p PROTEIN -t TRAJECTORY -o OUTPUT [-r] [-n RENUMBER]

analyse

optional arguments:
  -h, --help            show this help message and exit
  -p PROTEIN, --protein PROTEIN
                        Protein PDB file
  -t TRAJECTORY, --trajectory TRAJECTORY
                        Trajectory DCD file
  -o OUTPUT, --output OUTPUT
                        Output base name
  -r, --remove-waters   Remove waters, salts etc.
  -n RENUMBER, --renumber RENUMBER
                        Renumber the protein (provide desired first number)
```
This requires the trajectory to be written out using the DCD reporter. The topology can be read from the minimised
starting point of the MD run.

The trajectory is  re-imaged so that the ligand and protein are in the correct location with respect to eachother (the periodic
box can cause some wierd visual aberations), and the waters, ions etc. removed if required (-r).

The RMSD of the ligand and the protein C-alpha atoms compared to the start of the trajectory are displayed in a chart
that is generated using [Plotly](https://plotly.com/graphing-libraries/) with the name output.svg/output.html.

For complexes that are stable the RMSDs should not change dramatically. For a complex that is unstable the ligand may 
detach from the protein and the RMSD will increase dramatically. Relatively long simulations will be needed, maybe in the 
order of 100s of ns.

## Graphical user interface (GUI)

The GUI can make it a lot easier to input all the needed parameters, espesically for new users.
It can be run from the source, needs [wxPython](https://wxpython.org/index.html) installed. Alternatively, Windows users can use the .exe file.

The GUI contains 4 tabs:
1. Input: contains the input files and simulatins time
2. Restrain: contains restrain and custom bond options
3. Additonal parameters: contains the remaining parameters, like temp, forcefields, ect
4. Output: shows a preview the produced file

The programs will produce a .txt file, which can be directly inputed in MDsim.py. The txt file can dircetl be parsed to MDsim.py by using the *@* pre-position.
```
$ python MDsim.py @output_config.txt
```
