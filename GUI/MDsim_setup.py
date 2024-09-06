'''
Set up a configuration file for MDsim.py.
'''
import wx
import math, site, os
from wx.lib.embeddedimage import PyEmbeddedImage


def RelativePath(Dialoge):
    dir = Dialoge.GetDirectory()
    file = Dialoge.GetPath()
    return file.replace(dir,'.')
def filepath():
    # Get the curent working directory
    cdw = os.getcwd()
    # Find the user ID 
    id = re.search(r'/[0-9]*/vsc[0-9]*/',cwd)
    # insert user ID in path
    path = 'data/gent'+id.group()+'python_lib/lib/python3.10/site-packages/openmmforcefields/ffxml/amber'
    return os.listdir(path)
class PageOne(wx.Panel):
    def __init__(self, parent):
        super(PageOne, self).__init__(parent)
        # Creat sizer
        sizer = wx.GridBagSizer(5,10)

        # Input choise
        files = ['Protein + ligand', 'Complex + system']
        self.inputfiles = wx.RadioBox(self, label='Input Files', pos=(20, 20), choices=files,
                                majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.inputfiles.Bind(wx.EVT_RADIOBOX, self.RadioInputFiles)
        sizer.Add(self.inputfiles, pos=(0,0), span=(1,4), flag=wx.EXPAND)

        # Simulations choice
        lblList = ['Protein', 'Complex']
        self.sim = wx.RadioBox(self, label='Simulation', pos=(20, 90), choices=lblList,
                                majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.sim.Bind(wx.EVT_RADIOBOX, self.RadioSim)
        sizer.Add(self.sim, pos=(1, 0), span=(1, 2), flag=wx.EXPAND)

        # Protein file input
        l1 = wx.StaticText(self,-1, "Input protein (pdb-file)", (20,150))
        self.pro = wx.StaticText(self, -1, 'No file selected', (110,175))
        self.protein = wx.Button(self, -1, 'Choose file', (20,170))
        self.protein.Bind(wx.EVT_BUTTON,self.FileInput)
        sizer.Add(l1, pos=(2, 0))
        sizer.Add(self.pro,pos=(4,0))
        sizer.Add(self.protein, pos=(3, 0))

        # Ligand file input
        l2 = wx.StaticText(self,-1, "Input ligand (MOL/SDF-file)", (20,200))
        self.lig = wx.StaticText(self, -1, 'No file selected', (110, 225))
        self.ligand = wx.Button(self, -1, 'Choose file', (20,220))
        self.ligand.Bind(wx.EVT_BUTTON,self.FileInput)
        self.ligand.Disable()
        sizer.Add(l2, pos=(5, 0))
        sizer.Add(self.lig,pos=(7,0))
        sizer.Add(self.ligand, pos=(6, 0))

        # Complex file input
        l3 = wx.StaticText(self,-1, "Input complex (pdb-file)", (300,150))
        self.comp = wx.StaticText(self, -1, 'No File selected', (390,175))
        self.complex = wx.Button(self, -1, 'Choose file', (300,170))
        self.complex.Bind(wx.EVT_BUTTON,self.FileInput)
        sizer.Add(l3, pos=(2, 4))
        sizer.Add(self.comp,pos=(4,4))
        sizer.Add(self.complex, pos=(3, 4))

        # System file input
        l4 = wx.StaticText(self,-1, "Input system (xml-file)", (300,200))
        self.sys = wx.StaticText(self, -1, 'No file selected', (390, 225))
        self.system = wx.Button(self, -1, 'Choose file', (300,220))
        self.system.Bind(wx.EVT_BUTTON,self.FileInput)
        sizer.Add(l4, pos=(5, 4))
        sizer.Add(self.sys,pos=(7,4))
        sizer.Add(self.system, pos=(6, 4))

        # Solvate
        self.solvate = wx.CheckBox(self, label='Solvate', pos=(20, 250))
        self.solvate.SetValue(True)
        self.solvate.Bind(wx.EVT_CHECKBOX, self.Checkbox)
        sizer.Add(self.solvate, pos=(8, 0))
        # Padding
        l5 = wx.StaticText(self, -1, "Padding (Å):", (130, 250))
        self.padding = wx.TextCtrl(self, -1, pos=(180,248), size=(20,20), value='10', style=wx.TE_CENTRE)
        self.padding.Bind(wx.EVT_TEXT, self.TextBox)
        sizer.Add(l5, pos=(8, 1))
        sizer.Add(self.padding, pos=(8, 2))
        # Cleanup protein
        self.cleanup = wx.CheckBox(self, label='clean-up protein', pos=(20, 270))
        self.cleanup.Bind(wx.EVT_CHECKBOX, self.Checkbox)
        sizer.Add(self.cleanup, pos=(9, 0))
        # pH
        l6 = wx.StaticText(self, -1, "pH:", (130, 270))
        self.pH = wx.TextCtrl(self, -1, pos=(180, 268), size=(20, 20), value='7', style=wx.TE_CENTRE)
        self.pH.Bind(wx.EVT_TEXT, self.TextBox)
        self.pH.SetEditable(self.cleanup.GetValue())
        sizer.Add(l6, pos=(9, 1))
        sizer.Add(self.pH, pos=(9, 2))

        # Interval
        l7 = wx.StaticText(self, -1, "Time interval (ps)", (20, 300))
        self.step_size = wx.TextCtrl(self, -1, pos=(30,320), size=(50, 20), style=wx.TE_CENTRE | wx.TE_READONLY)
        self.step_size.SetValue('0.001')
        ## create +/- buttons
        self.down_time = wx.Button(self, -1, '-', (30 - 20, 320), size=(20, 20))
        self.up_time = wx.Button(self, -1, '+', (30 + 50, 320), size=(20, 20))
        self.up_time.Bind(wx.EVT_BUTTON, self.UpClick)
        self.down_time.Bind(wx.EVT_BUTTON, self.DownClick)
        box_time = wx.BoxSizer(wx.HORIZONTAL)
        box_time.Add(self.down_time,0,0)
        box_time.Add(self.step_size,0,0)
        box_time.Add(self.up_time,0,0)
        sizer.Add(l7, pos=(10, 0))
        sizer.Add(box_time,pos=(11,0))


        # Duration
        l8 = wx.StaticText(self, -1, "Simulation time (ns)", (130, 300))
        self.duration = wx.TextCtrl(self, -1, pos=(130,320), size=(60, 20), style=wx.TE_CENTRE)
        self.duration.SetValue('2')
        self.duration.Bind(wx.EVT_TEXT, self.DurationInput)
        sizer.Add(l8, pos=(10, 1))
        sizer.Add(self.duration, pos=(11, 1))

        # Reporting interval
        l9 = wx.StaticText(self, -1, "Report interval", (20, 350))
        self.report = wx.TextCtrl(self, -1, pos=(30, 370), size=(50, 20), style=wx.TE_CENTRE | wx.TE_READONLY)
        self.report.SetValue('100')
        ## create +/- buttons
        self.down_report = wx.Button(self, -1, '-', (30 - 20, 370), size=(20, 20))
        self.up_report = wx.Button(self, -1, '+', (30 + 50, 370), size=(20, 20))
        self.up_report.Bind(wx.EVT_BUTTON, self.UpClick)
        self.down_report.Bind(wx.EVT_BUTTON, self.DownClick)
        box_report = wx.BoxSizer(wx.HORIZONTAL)
        box_report.Add(self.down_report,0,0)
        box_report.Add(self.report,0,0)
        box_report.Add(self.up_report,0,0)
        sizer.Add(l9, pos=(12, 0))
        sizer.Add(box_report,pos=(13,0))

        # Nr of frames
        l10 = wx.StaticText(self, -1, "Nr of frames", (130, 350))
        self.frames = wx.TextCtrl(self, -1, pos=(130, 370), size=(60, 20), value='50',
                                  style=wx.TE_CENTRE|wx.TE_READONLY)
        sizer.Add(l10, pos=(12, 1))
        sizer.Add(self.frames, pos=(13, 1))

        self.RadioInputFiles(wx.EVT_RADIOBOX) # set enable/disable of button at the start

        # Help buttons
        img = wx.Image(img_help.GetImage()) # load the encoded image
        bmp = wx.Bitmap(img.ConvertToBitmap()) # convert to bitmap
        self.help1 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp,
                                      size=(bmp.GetWidth(), bmp.GetHeight()),
                                      pos=(170,100))
        self.Bind(wx.EVT_BUTTON,self.Help)
        self.help2 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp,
                               size=(bmp.GetWidth(), bmp.GetHeight()),
                               pos=(220, 250))
        self.Bind(wx.EVT_BUTTON,self.Help)
        self.help3 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp,
                                     size=(bmp.GetWidth(), bmp.GetHeight()),
                                     pos=(220, 270))
        self.Bind(wx.EVT_BUTTON, self.Help)
        sizer.Add(self.help1, pos=(1, 2))
        sizer.Add(self.help2, pos=(8, 3),flag=wx.CENTER)
        sizer.Add(self.help3, pos=(9, 3),flag=wx.CENTER)
        self.SetSizer(sizer)
    def Help(self,e):
        event = e.GetEventObject().GetId()
        message = {self.help1.GetId():'Simulations can be run for either a standalone protein or a protein/ligand '
                'complex. The ligand must be positioned at the desired location in advance (eg. using docking software '
                'like AutoDock).',
                   self.help2.GetId():'The diameter of a sphere containing the model will be determined, and the '
                                      'specified padding will be added to it. The final solvation box is cubical.',
                   self.help3.GetId():'PDB files often do not include hydrogen atoms. You need to add the missing '
                                      'hydrogens. The set of hydrogens that gets added will depend on what pH you want '
                                      'to simulate the system at.'}
        dlg = wx.MessageDialog(self,
                               message[event],
                               "Help", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    def RadioSim(self, e):
        output.update({'simulation': self.sim.GetStringSelection()})
        if output['simulation'] == 'Protein':
            self.ligand.Disable()
            output.pop('ligand')
        elif output['simulation'] == 'Complex':
            self.ligand.Enable()

    def RadioInputFiles(self,e):
        selection = self.inputfiles.GetStringSelection()
        id1 = [self.protein,self.sim,self.solvate, self.padding,self.cleanup, self.pH]
        id2 = [self.system,self.complex]
        if selection == 'Protein + ligand':
            for i in id1:
                i.Enable()
            for ii in id2:
                ii.Disable()
            if output['simulation'] == 'Complex':
                self.ligand.Enable()
        elif selection == 'Complex + system':
            for i in id1:
                i.Disable()
            self.ligand.Disable()
            for ii in id2:
                ii.Enable()

    def FileInput(self,e):
        event = e.GetEventObject().GetId()
        choise = {self.protein.GetId():('protein','pdb files (*.pdb)|*.pdb',self.pro),
                  self.ligand.GetId():('ligand','MOL and SDF files (*.mol;*.sdf)|*.mol;*.sdf',self.lig),
                  self.complex.GetId():('complex','pdb files (*.pdb)|*.pdb',self.comp),
                  self.system.GetId():('system','xml files (*.xml)|*.xml',self.sys)}
        OpenFile = wx.FileDialog(self, f'Select {choise[event][0]} file', "",
                                 wildcard=choise[event][1], style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        OpenFile.ShowModal()
        output.update({choise[event][0]: RelativePath(OpenFile)})
        choise[event][2].SetLabel(output.get(choise[event][0]))
    def Checkbox(self,e):
        event = e.GetEventObject().GetId()
        if event == self.solvate.GetId():
            output.update({'solvate': self.solvate.GetValue()})
            self.padding.SetEditable(self.solvate.GetValue())
        elif event == self.cleanup.GetId():
            output.update({'cleanup': self.cleanup.GetValue()})
            self.pH.SetEditable(self.cleanup.GetValue())
    def TextBox(self,e):
        output.update({'padding':self.padding.GetValue()})
        output.update({'pH': self.pH.GetValue()})

    def UpClick(self,e):
        event = e.GetEventObject()
        if event.GetId() == self.up_time.GetId():
            self.step_size.SetValue(str(float(self.step_size.GetValue())+0.001))
        elif event.GetId() == self.up_report.GetId():
            self.report.SetValue(str(int(self.report.GetValue())+100))
        steps = math.trunc((int(self.duration.GetValue()) / float(self.step_size.GetValue())) * 1000)
        frames = math.trunc(output['steps']/float(self.report.GetValue()))
        self.frames.SetValue(str(frames))
        output.update({'steps':steps, 'step_size': self.step_size.GetValue(), 'interval':self.report.GetValue()})

    def DownClick(self,e):
        event = e.GetEventObject()
        if event.GetId() == self.down_time.GetId() and self.step_size.GetValue() != '0.001':
            self.step_size.SetValue(str(float(self.step_size.GetValue())-0.001))
        elif event.GetId() == self.down_report.GetId() and self.report.GetValue() != '100':
            self.report.SetValue(str(int(self.report.GetValue())-100))
        steps = math.trunc((int(self.duration.GetValue())/float(self.step_size.GetValue()))*1000)
        interval = math.trunc(output['steps']/float(self.report.GetValue()))
        self.frames.SetValue(str(interval))
        output.update({'steps': steps, 'step_size': self.step_size.GetValue(), 'interval': interval})
    def DurationInput(self,e):
        steps = math.trunc((int(self.duration.GetValue()) / float(self.step_size.GetValue())) * 1000)
        interval = math.trunc(output['steps'] / float(self.report.GetValue()))
        self.frames.SetValue(str(interval))
        output.update({'steps': steps, 'interval': interval})


class PageTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # Create sizer
        sizer = wx.GridBagSizer(5,10)
        # Restraint
        self.restraint = wx.CheckBox(self, label='RESTRAIN RESIDUES', pos=(20, 20))
        self.restraint.SetValue(False)
        self.restraint.Bind(wx.EVT_CHECKBOX, self.RestraintCheck)
        # CA
        lblList = ['No', 'Yes']
        self.rbox = wx.RadioBox(self, label='Restrain Cα', pos=(20, 40), choices=lblList,
                                majorDimension=1, style=wx.RA_SPECIFY_COLS)
        self.rbox.Bind(wx.EVT_RADIOBOX, self.onRadioBox)
        # AA input
        AA = ['ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS','MET','PHE','PRO',
                            'SER','THR','TRP','TYR','VAL', 'UNK']
        l1 = wx.StaticText(self, -1, 'Amino acid', (20, 100))
        self.aa = wx.Choice(self, pos=(20, 120), choices=AA)
        l2 = wx.StaticText(self, -1, 'nr', (90, 100))
        self.aa_nr = wx.TextCtrl(self,-1,'',(80,120), size=(40,20))
        # Add enter & reset buttons
        self.aa_enter = wx.Button(self,-1,'Enter', (120,100))
        self.aa_enter.Bind(wx.EVT_BUTTON, self.ButEnter)
        self.aa_reset = wx.Button(self, -1, 'Reset', (120, 120))
        self.aa_reset.Bind(wx.EVT_BUTTON, self.ButReset)
        # Strength
        l3 = wx.StaticText(self, -1, 'Strength:', (20, 150))
        self.aa_strength = wx.TextCtrl(self, -1, '200', pos=(80, 150), size=(40, 20), style=wx.TE_CENTRE)
        self.aa_strength.Bind(wx.EVT_TEXT, self.Strength)
        # Selected AA
        l4 = wx.StaticText(self, -1, 'Selected amino acids:', (200, 20))
        self.aa_list = wx.TextCtrl(self, -1, pos=(200, 40), size=(100, 150),
                                   style=wx.TE_CENTRE|wx.TE_READONLY| wx.TE_MULTILINE)
        # Assign to sizer
        sizer.Add(self.restraint, pos=(0, 0), span=(1,2))
        sizer.Add(self.rbox, pos=(1, 0))
        sizer.Add(l1, pos=(2, 0))
        sizer.Add(self.aa, pos=(3, 0))
        sizer.Add(l2, pos=(2, 1))
        sizer.Add(self.aa_nr, pos=(3, 1))
        sizer.Add(self.aa_enter, pos=(2, 2))
        sizer.Add(self.aa_reset, pos=(3, 2))
        sizer.Add(l3, pos=(4, 0))
        sizer.Add(self.aa_strength, pos=(4, 1))
        sizer.Add(l4, pos=(0, 4))
        sizer.Add(self.aa_list, pos=(1, 4), span=(4,1))


        # Custom bond
        self.cb = wx.CheckBox(self, label='CUSTOM BONDS', pos=(20, 200))
        self.cb.SetValue(False)
        self.cb.Bind(wx.EVT_CHECKBOX, self.CbCheck)
        # Input atoms
        l5 = wx.StaticText(self, -1, 'Atom 1:', (20, 220))
        self.atom1 = wx.TextCtrl(self, -1, pos=(70,220), size=(40, 20), style=wx.TE_CENTRE)
        l6 = wx.StaticText(self, -1, 'Atom 2:', (20, 240))
        self.atom2 = wx.TextCtrl(self, -1, pos=(70, 240), size=(40, 20), style=wx.TE_CENTRE)
        # enter & reset buttons
        self.enter = wx.Button(self,-1,'Enter',(120,220))
        self.enter.Bind(wx.EVT_BUTTON, self.ButEnter)
        self.reset = wx.Button(self,-1,'Reset', (120,240))
        self.reset.Bind(wx.EVT_BUTTON, self.ButReset)
        # Strength
        l7 = wx.StaticText(self, -1, 'Strength:', (20, 280))
        self.strength = wx.TextCtrl(self, -1, '259407',pos=(70, 280), size=(40, 20), style=wx.TE_CENTRE)
        self.strength.Bind(wx.EVT_TEXT, self.Strength)
        # Selected atoms
        l8 = wx.StaticText(self, -1, 'Selected amino acids:', (200, 200))
        self.atom_list = wx.TextCtrl(self, -1, pos=(200, 220), size=(100, 150),
                                   style=wx.TE_CENTRE | wx.TE_READONLY | wx.TE_MULTILINE)
        # Assign to sizer
        sizer.Add(self.cb, pos=(6, 0), span=(1, 2))
        sizer.Add(l5, pos=(7, 0))
        sizer.Add(self.atom1, pos=(7, 1))
        sizer.Add(l6, pos=(8, 0))
        sizer.Add(self.atom2, pos=(8, 1))
        sizer.Add(self.enter, pos=(7, 2))
        sizer.Add(self.reset, pos=(8, 2))
        sizer.Add(l7, pos=(9, 0))
        sizer.Add(self.strength, pos=(9, 1))
        sizer.Add(l8, pos=(6, 4))
        sizer.Add(self.atom_list, pos=(7, 4), span=(4, 1))

        # Set enable/disable in starting positions
        self.CbCheck(wx.EVT_CHECKBOX)
        self.RestraintCheck(wx.EVT_CHECKBOX)
        # Help buttons
        img = wx.Image(img_help.GetImage())  # load the encoded image
        bmp = wx.Bitmap(img.ConvertToBitmap())  # convert to bitmap
        self.help1 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp,
                                     size=(bmp.GetWidth(), bmp.GetHeight()),
                                     pos=(150, 20))
        self.Bind(wx.EVT_BUTTON, self.Help)
        self.help2 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp,
                                     size=(bmp.GetWidth(), bmp.GetHeight()),
                                     pos=(130, 150))
        self.Bind(wx.EVT_BUTTON, self.Help)
        self.help3 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp,
                                     size=(bmp.GetWidth(), bmp.GetHeight()),
                                     pos=(150, 200))
        self.Bind(wx.EVT_BUTTON, self.Help)
        self.help4 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp,
                                     size=(bmp.GetWidth(), bmp.GetHeight()),
                                     pos=(120, 280))
        self.Bind(wx.EVT_BUTTON, self.Help)
        # Assign to sizer
        sizer.Add(self.help1, pos=(0, 2),flag=wx.CENTER)
        sizer.Add(self.help2, pos=(4, 2),flag=wx.CENTER)
        sizer.Add(self.help3, pos=(6, 2),flag=wx.CENTER)
        sizer.Add(self.help4, pos=(9, 2),flag=wx.CENTER)
        self.SetSizer(sizer)

    def Help(self, e):
        event = e.GetEventObject().GetId()
        message = {self.help1.GetId(): 'Sometimes you want to run a simulation in which certain particles have their '
                                       'motion restricted, unable to move too far from where they started. Position '
                                       'restraints are typically implemented by adding a harmonic force that binds each '
                                       'particle to its initial position.\n'
                                       'Below you can restrain all Cα and/or a specific'
                                       'amino acids. UNK represent atoms of the ligand, if present.',
                   self.help2.GetId(): 'The strength of the harmonic force is represented by\n'
                                       '    k*periodicdistance(x, y, z, x0, y0, z0)^2\n'
                                       'with k equal to the strength provided',
                   self.help3.GetId(): 'While simulating enzymes, it may be of interest to mimic a transition state '
                                       'by introducing a custom (covelent) bond.\n'
                                       'Below you can provide the index of two atoms to create a new bond between.',
                   self.help4.GetId(): 'The strength of the bond force is represented by\n'
                                       '    0.5*k*(r-r0)^2\n'
                                       'with k equal to the strength provided'
                   }
        dlg = wx.MessageDialog(self,
                               message[event],
                               "Help", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    def onRadioBox(self, e):
        aa_list = self.aa_list.GetValue().split(',')
        if self.rbox.GetStringSelection() == 'Yes':
            aa_list.insert(0,'CA')
        elif self.rbox.GetStringSelection() == 'No':
            aa_list.remove('CA')
        self.aa_list.SetValue(','.join(aa_list))
        output.update({'restrain': self.aa_list.GetValue()})
    def ButEnter(self,e):
        event = e.GetEventObject() # identify the clicked button
        if event.GetId() == self.aa_enter.GetId():
            a1 = self.aa.GetStringSelection()
            a2 = self.aa_nr.GetValue()
            atomlist = self.aa_list
            para = 'restrain'
        elif event.GetId() == self.enter.GetId():
            a1 = self.atom1.GetValue()
            a2 = self.atom2.GetValue()
            atomlist = self.atom_list
            para = 'custom_bond'
        else:
            e.Skip()
        list = atomlist.GetValue() + f'{a1}-{a2}\n'
        atomlist.SetValue(list)
        output.update({para:list.rstrip('\n').replace('\n',',')})
        print(output)

    def ButReset(self,e):
        event = e.GetEventObject() # identify the clicked button
        # setup confirmation window
        dlg = wx.MessageDialog(self,
                               "Reset current selection?",
                               "Confirm Reset", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()    # show window
        dlg.Destroy()               # close window
        if result == wx.ID_OK:
            if event.GetId() == self.aa_reset.GetId():
                atomlist = self.aa_list
                para = 'restrain'
                self.rbox.SetStringSelection('No')
            elif event.GetId() == self.reset.GetId():
                atomlist = self.atom_list
                para = 'custom_bond'
            atomlist.SetValue('')
            output.pop(para)

    def RestraintCheck(self, e):
        self.aa_nr.SetEditable(self.restraint.GetValue())
        self.aa_strength.SetEditable(self.restraint.GetValue())
        if self.restraint.GetValue():
            self.rbox.Enable()
            self.aa.Enable()
            self.aa_enter.Enable()
            self.aa_reset.Enable()
        elif not self.restraint.GetValue():
            self.rbox.Disable()
            self.aa.Disable()
            self.aa_enter.Disable()
            self.aa_reset.Disable()
            self.aa_list.SetValue('')
            output.pop('restrain')

    def CbCheck(self, e):
        self.atom1.SetEditable(self.cb.GetValue())
        self.atom2.SetEditable(self.cb.GetValue())
        self.strength.SetEditable(self.cb.GetValue())
        if self.cb.GetValue():
            self.enter.Enable()
            self.reset.Enable()
        elif not self.cb.GetValue():
            self.enter.Disable()
            self.reset.Disable()
            self.atom_list.SetValue('')
            output.pop('custom_bond')
    def Strength(self,e):
        event = e.GetEventObject()
        if event.GetId() == self.aa_strength.GetId():
            output.update({'restrain_strength': self.aa_strength.GetValue()})
        elif event.GetId() == self.strength.GetId():
            output.update({'bond_strength':self.strength.GetValue()})
class PageThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Friction coeff
        l1 = wx.StaticText(self,-1,'Friction coefficient',(20,20))
        self.fric = wx.TextCtrl(self,-1,'1',(20,40))
        self.fric.Bind(wx.EVT_TEXT, self.TextInput)
        # temp
        l2 = wx.StaticText(self, -1, 'Temperature (K)', (20, 70))
        self.temp = wx.TextCtrl(self, -1, '300', (20, 90))
        self.temp.Bind(wx.EVT_TEXT, self.TextInput)
        # pos ion
        l3 = wx.StaticText(self, -1, 'Positive ion', (20, 110))
        self.pos = wx.TextCtrl(self, -1, 'Na+', (20, 130))
        self.pos.Bind(wx.EVT_TEXT, self.TextInput)
        # neg ion
        l4 = wx.StaticText(self, -1, 'Negative ion', (160, 110))
        self.neg = wx.TextCtrl(self, -1, 'Cl-', (160, 130))
        self.neg.Bind(wx.EVT_TEXT, self.TextInput)
        # ion strength
        l5 = wx.StaticText(self, -1, 'Ionic strength', (20, 160))
        self.strenght = wx.TextCtrl(self, -1, '0', (20, 180))
        self.strenght.Bind(wx.EVT_TEXT, self.TextInput)
        # no neutralize
        self.neutr = wx.CheckBox(self, label='Neutralize', pos=(20, 170))
        self.neutr.Bind(wx.EVT_CHECKBOX, self.neutrCheck)
        # equilibration steps
        l6 = wx.StaticText(self, -1, 'Equilibration steps', (20, 220))
        self.equ = wx.TextCtrl(self, -1, '200', (20, 240))
        self.equ.Bind(wx.EVT_TEXT, self.TextInput)

        # construct force field lists
        ## protein
        pff = ['amber/ff14SB.redq.xml', 'amber/GLYCAM_06j-1.xml', 'amber/ffPM3.xml', 'amber/ff99SBnmr.xml',
               'amber/ff96.xml', 'amber/protein.ff03ua.xml', 'amber/RNA.OL3.xml', 'amber/ff99.xml', 'amber/gaff',
               'amber/protein.ff15ipq-vac.xml', 'amber/ff10.xml', 'amber/RNA.ROC.xml', 'amber/ff14SB.xml',
               'amber/protein.ff14SB.xml', 'amber/protein.ff14SBonlysc.xml', 'amber/ff94.xml', 'amber/protein.ff15ipq.xml',
               'amber/ff99bsc0.xml', 'amber/lipid17_merged.xml', 'amber/DNA.bsc0.xml', 'amber/protein.fb15.xml',
               'amber/lipid17.xml', 'amber/protein.ff03.r1.xml', 'amber/ff98.xml', 'amber/ffAM1.xml', 'amber/ff99SB.xml',
               'amber/ff99SBildn.xml', 'amber/DNA.bsc1.xml', 'amber/ff03.xml', 'amber/DNA.OL15.xml', 'amber/phosaa14SB.xml',
               'amber/RNA.YIL.xml', 'amber/phosaa10.xml']

        ## ligand
        lff =['gaff-1.4', 'gaff-1.8', 'gaff-1.81', 'gaff-2.1', 'gaff-2.11', 'openff-1.3.1', 'openff-2.0.0-rc.2',
              'openff-1.0.1', 'openff-1.0.0', 'openff-2.1.1', 'openff-1.3.0', 'openff-1.2.1', 'openff-1.0.0-RC1',
              'openff-2.0.0', 'openff-2.1.0-rc.1', 'openff-1.2.0', 'openff-2.1.0', 'openff-1.1.1', 'openff-1.0.0-RC2',
              'openff-1.1.0', 'openff-2.0.0-rc.1', 'openff-1.3.1-alpha.1', 'smirnoff99Frosst-1.0.0', 'smirnoff99Frosst-1.1.0',
              'smirnoff99Frosst-1.0.7', 'smirnoff99Frosst-1.0.2', 'smirnoff99Frosst-1.0.6', 'smirnoff99Frosst-1.0.8',
              'smirnoff99Frosst-1.0.9', 'smirnoff99Frosst-1.0.4', 'smirnoff99Frosst-1.0.5', 'smirnoff99Frosst-1.0.3',
              'smirnoff99Frosst-1.0.1', 'ff14sb_off_impropers_0.0.2', 'ff14sb_off_impropers_0.0.1', 'ff14sb_off_impropers_0.0.4',
              'ff14sb_off_impropers_0.0.3', 'espaloma-0.2.2']
        ## water
        wff = ['amber/tip4pew_HFE_multivalent.xml', 'amber/spce_standard.xml', 'amber/tip4pfb_standard.xml',
               'amber/tip3pfb_HFE_multivalent.xml', 'amber/tip4pfb_IOD_multivalent.xml', 'amber/tip3p_HFE_multivalent.xml',
               'amber/tip3pfb_IOD_multivalent.xml', 'amber/tip4pew_standard.xml', 'amber/tip4pfb_HFE_multivalent.xml',
               'amber/tip3p_IOD_multivalent.xml', 'amber/spce_IOD_multivalent.xml', 'amber/spce_HFE_multivalent.xml',
               'amber/tip4pew_IOD_multivalent.xml', 'amber/tip3pfb_standard.xml', 'amber/tip3p_standard.xml']
        # water model
        models=["tip3p", "spce", "tip4pew", "tip5p", "swm4ndp"]
        l7 = wx.StaticText(self, -1, 'Water model', (20, 250))
        self.watermodel = wx.Choice(self, pos=(20, 270), choices =models)
        self.watermodel.SetStringSelection('tip3p')
        self.watermodel.Bind(wx.EVT_CHOICE, self.Checkboxes)
        # protein force field
        l8 = wx.StaticText(self, -1, 'Protein force field', (20, 300))
        self.pro_ff = wx.Choice(self, pos=(20, 320), choices=pff)
        self.pro_ff.SetStringSelection('amber/ff14SB.xml')
        self.pro_ff.Bind(wx.EVT_CHOICE, self.Checkboxes)
        # ligand force field
        l9 = wx.StaticText(self, -1, 'Ligand force field', (20, 350))
        self.lig_ff = wx.Choice(self, pos=(20, 370), choices=lff)
        self.lig_ff.SetStringSelection('gaff-2.11')
        self.lig_ff.Bind(wx.EVT_CHOICE, self.Checkboxes)
        # water force field
        l10 = wx.StaticText(self, -1, 'Water force field', (20, 400))
        self.water_ff = wx.Choice(self, pos=(20, 420), choices=wff)
        self.water_ff.SetStringSelection('amber/tip3p_standard.xml')
        self.water_ff.Bind(wx.EVT_CHOICE, self.Checkboxes)

        topsizer = wx.BoxSizer(wx.HORIZONTAL)
        para_sizer = wx.BoxSizer(wx.VERTICAL)
        para = [[l1, self.fric],
                [l2, self.temp],
                [l6, self.equ],
                [l3, self.pos],
                [l4, self.neg],
                [l5, self.strenght]]
        for l,p in para:
            para_sizer.Add(l,0,10)
            para_sizer.Add(p, 0, 10)
            para_sizer.AddSpacer(10)
        para_sizer.Add(self.neutr, 0, 10)
        model_sizer = wx.BoxSizer(wx.VERTICAL)
        para = [[l7, self.watermodel],
                [l8, self.pro_ff],
                [l9, self.lig_ff],
                [l10, self.water_ff]]
        for l,p in para:
            model_sizer.Add(l, 0, 10)
            model_sizer.Add(p, 0, 10)
            model_sizer.AddSpacer(10)
        topsizer.Add(para_sizer,0,wx.LEFT,10)
        topsizer.AddSpacer(50)
        topsizer.Add(model_sizer,1,wx.LEFT,10)
        self.SetSizer(topsizer)
    def TextInput(self,e):
        para = {self.fric.GetId():'friction_coeff',
                self.temp.GetId():'temperature',
                self.pos.GetId():'positive_ion',
                self.neg.GetId():'negative_ion',
                self.strenght.GetId():'ionic_strength',
                self.equ.GetId():'equilibration_steps'}
        widget = e.GetEventObject()
        output.update({para[widget.GetId()]:widget.GetValue()})
    def neutrCheck(self,e):
        output.update({'no_neutralize':self.neutr.GetValue()})
    def Checkboxes(self,e):
        para = {self.watermodel.GetId():'water_model',
                self.pro_ff.GetId():'protein_force_field',
                self.lig_ff.GetId():'ligand_force_field',
                self.water_ff.GetId():'water_force_field',}
        widget = e.GetEventObject()
        output.update({para[widget.GetId()]: widget.GetStringSelection()})
class PageFour(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # boxsize
        topsizer = wx.BoxSizer(wx.HORIZONTAL)
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.text = wx.TextCtrl(self,-1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.btn_update = wx.Button(self,-1, 'Update')
        self.btn_update.Bind(wx.EVT_BUTTON, self.Btn)
        self.Btn(wx.EVT_BUTTON)

        topsizer.Add(self.text, 1, wx.CENTER | wx.EXPAND, 10)
        btnsizer.Add(self.btn_update, 0, wx.CENTER | wx.EXPAND, 5)

        topsizer.Add(btnsizer, 0, wx.CENTER | wx.BOTTOM, 10)

        self.SetSizer(topsizer)
    def Btn(self, e):
        out = ''
        for parameter in output:
            if parameter in ('solvate','cleanup_protein', 'no_neutralize'):
                if output[parameter]:
                    out += (f'--{parameter}\n')
            else:
                out += (f'--{parameter}={output.get(parameter)}\n')
        self.text.SetValue(out)

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="MDsim Set-up", size=(600,500))

        # Here we create a panel and a notebook on the panel
        p = wx.Panel(self)
        self.nb = wx.Notebook(p)

        # create the page windows as children of the notebook
        page1 = PageOne(self.nb)
        page2 = PageTwo(self.nb)
        page3 = PageThree(self.nb)
        page4 = PageFour(self.nb)

        # add the pages to the notebook with the label to show on the tab
        self.nb.AddPage(page1, "Input")
        self.nb.AddPage(page2, "Restraint")
        self.nb.AddPage(page3, "Additional Parameters")
        self.nb.AddPage(page4, "Output")

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.nb, 1, wx.EXPAND)

        #self.statusbar = self.CreateStatusBar()
        # add ok & cancel buttons at the bottom of the window
        box = wx.BoxSizer(wx.HORIZONTAL)
        m_close = wx.Button(p, wx.ID_CLOSE, "Close")
        m_close.Bind(wx.EVT_BUTTON, self.OnClose)
        m_ok = wx.Button(p, wx.ID_OK, "OK")
        m_ok.Bind(wx.EVT_BUTTON, self.OnOk)
        box.Add(m_close, 0, 10)
        box.Add(m_ok, 0, 10)

        sizer.Add(box)
        p.SetSizer(sizer)
        p.Layout()

    def OnClose(self, event):
        # ask confirmation before closing
        mdlg = wx.MessageDialog(self,
                               "Do you really want to close this application?",
                               "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = mdlg.ShowModal()
        mdlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()
    def OnOk(self, e):
        # Display pop-up window
        tdlg = wx.TextEntryDialog(self, 'Give a name for the output files', 'Output name',
                        value='', style=wx.TextEntryDialogStyle)
        result = tdlg.ShowModal()
        tdlg.Destroy()
        if result == wx.ID_OK:
            # add name to output
            name = tdlg.GetValue()
            output.update({'output':name})
            # write the output to a file
            f = open(name+'_config.txt', "w")
            for parameter in output:
                if parameter in ('solvate','cleanup_protein','no_neutrelize'):
                    if output[parameter]:
                        f.write(f'--{parameter}')
                else:
                    f.write(f'--{parameter}={output.get(parameter)}\n')
            f.close()
            self.Destroy()

output = dict({'simulation':'Protein',
            'steps':5000,
            'step_size':0.002,
            'friction_coeff':1,
            'interval':1000,
            'temperature':300,
            'cleanup_protein':False,
            'solvate':True,
            'padding':10,
            'water_model':'tip3p',
            'positive_ion':'Na+',
            'negative_ion':'Cl-',
            'ionic_strenght':0,
            'no_neutralize':False,
            'equilibration_steps':200,
            'protein_force_field':'amber/ff14SB.xml',
            'ligand_force_field':'gaff-2.11',
            'water_force_field':'amber/tip3p_standard.xml',
            'restrain':'',
            'custom_bond':''})
img_help = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAYAAAA71pVKAAAFFGlUWHRYTUw6Y29tLmFkb2Jl'
    b'LnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRj'
    b'emtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0i'
    b'WE1QIENvcmUgNS41LjAiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9y'
    b'Zy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjph'
    b'Ym91dD0iIgogICAgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIgog'
    b'ICAgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAv'
    b'IgogICAgeG1sbnM6ZXhpZj0iaHR0cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iCiAgICB4'
    b'bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnht'
    b'cE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9'
    b'Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAg'
    b'eG1wOkNyZWF0ZURhdGU9IjIwMjQtMDgtMjhUMTg6NTA6NDIrMDIwMCIKICAgeG1wOk1vZGlm'
    b'eURhdGU9IjIwMjQtMDgtMjhUMjE6NDk6MDIrMDI6MDAiCiAgIHhtcDpNZXRhZGF0YURhdGU9'
    b'IjIwMjQtMDgtMjhUMjE6NDk6MDIrMDI6MDAiCiAgIHBob3Rvc2hvcDpEYXRlQ3JlYXRlZD0i'
    b'MjAyNC0wOC0yOFQxODo1MDo0MiswMjAwIgogICBwaG90b3Nob3A6Q29sb3JNb2RlPSIzIgog'
    b'ICBwaG90b3Nob3A6SUNDUHJvZmlsZT0ic1JHQiBJRUM2MTk2Ni0yLjEiCiAgIGV4aWY6UGl4'
    b'ZWxYRGltZW5zaW9uPSIxNSIKICAgZXhpZjpQaXhlbFlEaW1lbnNpb249IjE1IgogICBleGlm'
    b'OkNvbG9yU3BhY2U9IjEiCiAgIHRpZmY6SW1hZ2VXaWR0aD0iMTUiCiAgIHRpZmY6SW1hZ2VM'
    b'ZW5ndGg9IjE1IgogICB0aWZmOlJlc29sdXRpb25Vbml0PSIyIgogICB0aWZmOlhSZXNvbHV0'
    b'aW9uPSIzMDAvMSIKICAgdGlmZjpZUmVzb2x1dGlvbj0iMzAwLzEiPgogICA8eG1wTU06SGlz'
    b'dG9yeT4KICAgIDxyZGY6U2VxPgogICAgIDxyZGY6bGkKICAgICAgc3RFdnQ6YWN0aW9uPSJw'
    b'cm9kdWNlZCIKICAgICAgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWZmaW5pdHkgUGhvdG8gMiAy'
    b'LjUuMyIKICAgICAgc3RFdnQ6d2hlbj0iMjAyNC0wOC0yOFQyMTo0OTowMiswMjowMCIvPgog'
    b'ICAgPC9yZGY6U2VxPgogICA8L3htcE1NOkhpc3Rvcnk+CiAgPC9yZGY6RGVzY3JpcHRpb24+'
    b'CiA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgo8P3hwYWNrZXQgZW5kPSJyIj8+iU9MQwAAAYFp'
    b'Q0NQc1JHQiBJRUM2MTk2Ni0yLjEAACiRdZG7SwNBEIc/E8XgAwNaWKQIEq2i+ADRxiLiC9Qi'
    b'nmDU5nLeJUIex11Egq1gKyiINr4K/Qu0FawFQVEEsbZWtNFwzplAgphZZufb3+4Mu7PgUVJa'
    b'2q7thXQmZ0UnIsGF2GKw/hUfAfz00alqtjkzN65Q1T4fqHHjXbdbq/q5f61xRbc1qPEJj2im'
    b'lROeFJ5ez5ku7wq3aUl1RfhcOGzJBYXvXT1e5FeXE0X+dtlSoqPg8QsHExUcr2AtaaWF5eWE'
    b'0qk1rXQf9yVNemZ+TmKHeACbKBNECDLFGKMMSleGZR6km356ZEWV/N7f/FmykqvJbJLHYpUE'
    b'SXKERV2T6rpEQ3RdRoq82/+/fbWNgf5i9aYI1L04znsn1O9AYdtxvo4dp3AC3me4ypTzs0cw'
    b'9CH6dlkLHULLJlxcl7X4HlxuQfuTqVrqr+QV9xgGvJ1Bcwxab6Fhqdiz0j6nj6BsyFfdwP4B'
    b'dMn5luUfyEVoEv+c5uYAAAAJcEhZcwAALiMAAC4jAXilP3YAAAIPSURBVCiRdZLda5JhGIcv'
    b'39evUBcz92FMZn7U5rQJ0WjBGmtBWwc7Ktda7LQ/IFgU9AdEsKNOIuqgdRLFqLOKWkv6ILYG'
    b'NVMoTJOmU7BNXeLL1LeDl5bmuk9+N8/9u7if+3luFf+GN3AGs2MAXVM3an0nZSmOlIuQjb7k'
    b'84NHtVbVdrb3kBXn8HVsRyfYTAmsLkExCwYLtPvBZK2QeHePb/PTpJYzAOI22Ds5T0ffcRKv'
    b'VTy7DMhgOQCri7B8B4xtAvtH/Bgso5Q2HlJIFhXYP3WTjr4hpDw8vQTukzB4BVq6wTkMsgwf'
    b'boPrBJhdrchVC4m3jwV8Z8ex9U8AsJkGswPcIzUTqcAxpKT5pKK2/il6To+pMTuPodErzj1u'
    b'GJ1peEN+ZRQ1tSuqNYiYXYMCOqOn0V0TG9/hzQwcPAcm699zvckjIOrs/wcT8Pwq2I5A72Td'
    b'56DW7xOoSPEdQbkK729AmxcOXwBBrK+XpbiAVIjsCBezsPYJusZA1DbWS7mwwHosSLkkN3au'
    b'gC8AxtZGcKtYYT32SiQdCtFs76LZ7q0zaA3KZml21c8KEA/OsnTrmgBAbOEimciXOkPqI9w9'
    b'BelQPbi2Eib6Yhr+rGf+RwEpN4csWzFavYhqFeUSaPTQ0gP63bBVrBIPzvL1yXmSixka7wP4'
    b'xgOYnQPomjyIuk4qUhwpH+ZndIGV+3O11t8qTqZc7Opp0QAAAABJRU5ErkJggg==')

if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()
