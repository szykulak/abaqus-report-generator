# Do not edit this file or it may not load correctly
# if you try to open it with the RSG Dialog Builder.

# Note: thisDir is defined by the Activator class when
#       this file gets executed

from rsg.rsgGui import *
from abaqusConstants import INTEGER, FLOAT
execDir = os.path.split(thisDir)[1]
dialogBox = RsgDialog(title='Report generator', kernelModule='plugin', kernelFunction='extractor_function', includeApplyBtn=False, includeSeparator=True, okBtnText='OK', applyBtnText='Apply', execDir=execDir)
dialogBox.show()