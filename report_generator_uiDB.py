# Do not edit this file or it may not load correctly
# if you try to open it with the RSG Dialog Builder.

# Note: thisDir is defined by the Activator class when
#       this file gets executed

from rsg.rsgGui import *
from abaqusConstants import INTEGER, FLOAT
execDir = os.path.split(thisDir)[1]
dialogBox = RsgDialog(title='Report generator', kernelModule='', kernelFunction='', includeApplyBtn=False, includeSeparator=True, okBtnText='Generate', applyBtnText='Apply', execDir=execDir)
RsgTabBook(name='TabBook_1', p='DialogBox', layout='0')
RsgTabItem(name='TabItem_1', p='TabBook_1', text='Basics')
RsgTextField(p='TabItem_1', fieldType='String', ncols=12, labelText='ODB directory path:', keyword='keyword01', default='')
RsgTextField(p='TabItem_1', fieldType='String', ncols=12, labelText='Step:', keyword='keyword02', default='')
RsgTextField(p='TabItem_1', fieldType='String', ncols=12, labelText='Frames:', keyword='keyword03', default='')
RsgTextField(p='TabItem_1', fieldType='String', ncols=12, labelText='Path to save results:', keyword='keyword04', default='')
RsgTextField(p='TabItem_1', fieldType='String', ncols=12, labelText='Results directory name:', keyword='keyword05', default='')
RsgCheckButton(p='TabItem_1', text='Include mesh data', keyword='keyword06', default=False)
RsgTabItem(name='TabItem_3', p='TabBook_1', text='CSV Export')
RsgGroupBox(name='GroupBox_2', p='TabItem_3', text='I', layout='0')
RsgTextField(p='GroupBox_2', fieldType='String', ncols=12, labelText='Field output names:', keyword='keyword14', default='')
RsgTextField(p='GroupBox_2', fieldType='String', ncols=12, labelText='Set name:', keyword='keyword15', default='')
RsgTextField(p='GroupBox_2', fieldType='String', ncols=12, labelText='Instance name:', keyword='keyword16', default='')
RsgTextField(p='GroupBox_2', fieldType='String', ncols=12, labelText='Instance set name:', keyword='keyword17', default='')
RsgGroupBox(name='GroupBox_1', p='TabItem_3', text='II', layout='0')
RsgTextField(p='GroupBox_1', fieldType='String', ncols=12, labelText='Field output:', keyword='keyword13', default='')
RsgTextField(p='GroupBox_1', fieldType='String', ncols=12, labelText='Value:', keyword='keyword18', default='')
RsgTextField(p='GroupBox_1', fieldType='String', ncols=12, labelText='Minimum:', keyword='keyword19', default='')
RsgTextField(p='GroupBox_1', fieldType='String', ncols=12, labelText='Maximum:', keyword='keyword20', default='')
RsgTabItem(name='TabItem_2', p='TabBook_1', text='Screenshots')
RsgTextField(p='TabItem_2', fieldType='String', ncols=12, labelText='Views', keyword='keyword07', default='')
RsgTextField(p='TabItem_2', fieldType='String', ncols=12, labelText='Field output display variables:', keyword='keyword08', default='')
RsgComboBox(name='ComboBox_1', p='TabItem_2', text='Items to display:', keyword='keyword09', default='', comboType='STANDARD', repository='', rootText='', rootKeyword=None, layout='')
RsgListItem(p='ComboBox_1', text='Parts')
RsgListItem(p='ComboBox_1', text='Elements')
RsgListItem(p='ComboBox_1', text='Nodes?')
RsgListItem(p='ComboBox_1', text='Surfaces')
RsgTextField(p='TabItem_2', fieldType='String', ncols=12, labelText='Names of items to display:', keyword='keyword11', default='')
RsgTextField(p='TabItem_2', fieldType='String', ncols=12, labelText='Contour plot limits?:', keyword='keyword12', default='')
dialogBox.show()