import ODBExtractor
from abaqus import session
from odbAccess import*

def extractor_function():
#     odb = openOdb('C:/tmp/Contact1-GC.odb')
# session.mdbData.summary()
# o1 = session.openOdb('C:/tmp/Contact1-GC.odb')
# session.viewports['Viewport: 1'].setValues(displayedObject=o1)
    odb_extr = ODBExtractor.ODBExtractor()
    odb_extr.run_extractor()

