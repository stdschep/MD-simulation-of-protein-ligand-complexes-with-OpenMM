import sys, argparse
import mdtraj as md
import plotly.graph_objects as go


# Typical usage:
# python analyse.py -p output_minimised.pdb -t output_traj.dcd -o output_reimaged -r -n 4

parser = argparse.ArgumentParser(description="analyse")

parser.add_argument("-p", "--protein", required=True, help="Protein PDB file")
parser.add_argument("-t", "--trajectory", required=True, help="Trajectory DCD file")
parser.add_argument("-o", "--output", required=True, help="Output base name")
parser.add_argument("-r", "--remove-waters", action='store_true', help="Remove waters, salts etc.")
parser.add_argument("-n", "--renumber", type=int, help='Renumber the protein (provide desired first number)')


args = parser.parse_args()
print("analyse: ", args)

traj_in = args.trajectory
topol_in = args.protein
out_base = args.output

print('Reading trajectory', traj_in)
t = md.load(traj_in, top=topol_in)
t.image_molecules(inplace=True)

if args.remove_waters:
    print('Removing waters')
    t = t.atom_slice(t.top.select('not resname HOH POPC CL NA'))

print('Realigning')
prot = t.top.select('protein')
t.superpose(t[0], atom_indices=prot)

print('Writing re-imaged PDB', out_base + '.pdb')
t[0].save(out_base + '.pdb')

print('Writing re-imaged trajectory', out_base + '.dcd')
t.save(out_base + '.dcd')

topology = t.topology
# print(topology)
print('Number of frames:', t.n_frames)

# print('All residues: %s' % [residue for residue in t.topology.residues])

atoms = t.topology.select("chainid 1")
print(len(atoms), 'ligand atoms')
rmsds_lig = md.rmsd(t, t, frame=0, atom_indices=atoms, parallel=True, precentered=False)
# print(rmsds_lig)

atoms = t.topology.select("chainid 0 and backbone")
print(len(atoms), 'backbone atoms')
rmsds_bck = md.rmsd(t, t, frame=0, atom_indices=atoms, parallel=True, precentered=False)

fig = go.Figure()
fig.add_trace(go.Scatter(x=t.time, y=rmsds_bck, mode='lines', name='Backbone'))
fig.add_trace(go.Scatter(x=t.time, y=rmsds_lig, mode='lines', name='Ligand'))


fig.update_layout(title='Trajectory for ' + traj_in, xaxis_title='Frame', yaxis_title='RMSD')

file = out_base + '.svg'
print('Writing RMSD output graph to', out_base)
try:
    fig.write_image(file)  # Save static svg-file
    fig.show()  # Show interactive HTML format
except:
    fig.write_html(out_base + '.html')  # save interactive HTML-file (large file)

# fig.write_html(out_base + '.html')       # save interactive HTML-file (large file)

print("Done re-aligning")


# Sebastian Raschka 2014
# Python 3 script to atoms and residues in a PDB file.

class Pdb(object):
    """ Object that allows operations with protein files in PDB format. """

    def __init__(self, file_cont=[], pdb_code=""):
        self.cont = []
        self.atom = []
        self.hetatm = []
        self.fileloc = ""
        if isinstance(file_cont, list):
            self.cont = file_cont[:]
        elif isinstance(file_cont, str):
            try:
                with open(file_cont, 'r') as pdb_file:
                    self.cont = [row.strip() for row in pdb_file.read().split('\n') if row.strip()]
            except FileNotFoundError as err:
                print(err)

        if self.cont:
            self.atom = [row for row in self.cont if row.startswith('ATOM')]
            self.hetatm = [row for row in self.cont if row.startswith('HETATM')]
            self.conect = [row for row in self.cont if row.startswith('CONECT')]

    def renumber_atoms(self, start=1):
        """ Renumbers atoms in a PDB file. """
        out = list()
        count = start
        for row in self.cont:
            if len(row) > 5:
                if row.startswith(('ATOM', 'HETATM', 'TER', 'ANISOU')):
                    num = str(count)
                    while len(num) < 5:
                        num = ' ' + num
                    row = '%s%s%s' % (row[:6], num, row[11:])
                    count += 1
            out.append(row)
        return out

    def renumber_residues(self, start=1, reset=False):
        """ Renumbers residues in a PDB file. """
        out = list()
        count = start - 1
        cur_res = ''
        for row in self.cont:
            if len(row) > 25:
                if row.startswith(('ATOM', 'HETATM', 'TER', 'ANISOU')):
                    next_res = row[22:27].strip()  # account for letters in res., e.g., '1A'

                    if next_res != cur_res:
                        count += 1
                        cur_res = next_res
                    num = str(count)
                    while len(num) < 3:
                        num = ' ' + num
                    new_row = '%s%s' % (row[:23], num)
                    while len(new_row) < 29:
                        new_row += ' '
                    xcoord = row[30:38].strip()
                    while len(xcoord) < 9:
                        xcoord = ' ' + xcoord
                    row = '%s%s%s' % (new_row, xcoord, row[38:])
                    if row.startswith('TER') and reset:
                        count = start - 1
            out.append(row)
        return out


if __name__ == '__main__':

    if args.renumber is not None:
        print('Renumbering...')
        protein = (out_base+'.pdb')
        pdb1 = Pdb(protein)
        pdb1.cont = pdb1.renumber_residues(start=args.renumber)
        print('Writing renumbered file ', out_base, '.pdb')
        f = open(out_base+'.pdb', 'w')
        for line in pdb1.cont:
            f.write(str(line) + '\n')
        f.close()
        print('Done renumbering')
