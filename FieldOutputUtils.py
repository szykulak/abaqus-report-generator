from abaqusConstants import * # nie wiem czy to to 


class FieldOutputDisplay(object):
    def __init__(self, var_label, output_position, refinement):
        self.var_label = var_label
        self.output_position = output_position
        self.refinement = refinement #optional
         
def set_field_output_display_variables(): #nie mam pojecia czy powinnam to tak hardkodowae ale uzytkownik raczej tego nie bedzie znal
    field_output_display_var_list = []
    
    #active yielding cokolwiek to jest
    field_output_display_var_list.append(FieldOutputDisplay('AC YIELD', INTEGRATION_POINT,None))
    field_output_display_var_list.append(FieldOutputDisplay('AC YIELD1', INTEGRATION_POINT,None))
    field_output_display_var_list.append(FieldOutputDisplay('AC YIELD2', INTEGRATION_POINT,None))
    field_output_display_var_list.append(FieldOutputDisplay('AC YIELD3', INTEGRATION_POINT,None))
    field_output_display_var_list.append(FieldOutputDisplay('AC YIELD4', INTEGRATION_POINT,None))
    field_output_display_var_list.append(FieldOutputDisplay('AC YIELDT', INTEGRATION_POINT,None))

    #alpha - kinematic hardening shift - tensor umocnienia jakis chyba 
    #jak szukac po tych refinementach????
    field_output_display_var_list.append(FieldOutputDisplay('ALPHA', INTEGRATION_POINT, (COMPONENT, 'ALPHA11')))
    field_output_display_var_list.append(FieldOutputDisplay('ALPHA', INTEGRATION_POINT, (COMPONENT, 'ALPHA22')))
    field_output_display_var_list.append(FieldOutputDisplay('ALPHA', INTEGRATION_POINT, (COMPONENT, 'ALPHA33')))
    field_output_display_var_list.append(FieldOutputDisplay('ALPHA', INTEGRATION_POINT, (COMPONENT, 'ALPHA12')))
    field_output_display_var_list.append(FieldOutputDisplay('ALPHA', INTEGRATION_POINT, (COMPONENT, 'ALPHA13')))
    field_output_display_var_list.append(FieldOutputDisplay('ALPHA', INTEGRATION_POINT, (COMPONENT, 'ALPHA23')))
    
    #cener - energia rozproszona przez pelzanie np
    field_output_display_var_list.append(FieldOutputDisplay('CENER', INTEGRATION_POINT,None))

    #COORD  - wspolrzedne wezlow
    field_output_display_var_list.append(FieldOutputDisplay('COORD', NODAL,(INVARIANT, 'Magnitude')))
    field_output_display_var_list.append(FieldOutputDisplay('COORD', NODAL,(COMPONENT, 'COOR1')))
    field_output_display_var_list.append(FieldOutputDisplay('COORD', NODAL,(COMPONENT, 'COOR2')))
    field_output_display_var_list.append(FieldOutputDisplay('COORD', NODAL,(COMPONENT, 'COOR3')))

    #COORD - wspolrzedne punktow calkowania
    field_output_display_var_list.append(FieldOutputDisplay('COORD', INTEGRATION_POINT,(COMPONENT, 'COORD1')))
    field_output_display_var_list.append(FieldOutputDisplay('COORD', INTEGRATION_POINT,(COMPONENT, 'COORD2')))
    field_output_display_var_list.append(FieldOutputDisplay('COORD', INTEGRATION_POINT,(COMPONENT, 'COORD3')))

    #DMENER
    field_output_display_var_list.append(FieldOutputDisplay('DMENER', INTEGRATION_POINT,None))

    #E
    field_output_display_var_list.append(FieldOutputDisplay('E', INTEGRATION_POINT, (INVARIANT, 'Max. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('E', INTEGRATION_POINT, (INVARIANT, 'Max. Principal (Abs)')))
    field_output_display_var_list.append(FieldOutputDisplay('E', INTEGRATION_POINT, (INVARIANT, 'Mid. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('E', INTEGRATION_POINT, (INVARIANT, 'Min. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('E', INTEGRATION_POINT, (COMPONENT, 'E11')))
    field_output_display_var_list.append(FieldOutputDisplay('E', INTEGRATION_POINT, (COMPONENT, 'E22')))
    field_output_display_var_list.append(FieldOutputDisplay('E', INTEGRATION_POINT, (COMPONENT, 'E33')))
    field_output_display_var_list.append(FieldOutputDisplay('E', INTEGRATION_POINT, (COMPONENT, 'E12')))
    field_output_display_var_list.append(FieldOutputDisplay('E', INTEGRATION_POINT, (COMPONENT, 'E13')))
    field_output_display_var_list.append(FieldOutputDisplay('E', INTEGRATION_POINT, (COMPONENT, 'E23')))

    #EASEDEN
    field_output_display_var_list.append(FieldOutputDisplay('EASEDEN', WHOLE_ELEMENT,None))
    #ECDDEN
    field_output_display_var_list.append(FieldOutputDisplay('ECDDEN', WHOLE_ELEMENT,None))
    #ECTEDEN
    field_output_display_var_list.append(FieldOutputDisplay('ECTEDEN', WHOLE_ELEMENT,None))
    #EDMDDEN
    field_output_display_var_list.append(FieldOutputDisplay('EDMDDEN', WHOLE_ELEMENT,None))

    #EE
    field_output_display_var_list.append(FieldOutputDisplay('EE', INTEGRATION_POINT, (INVARIANT, 'Max. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('EE', INTEGRATION_POINT, (INVARIANT, 'Max. Principal (Abs)')))
    field_output_display_var_list.append(FieldOutputDisplay('EE', INTEGRATION_POINT, (INVARIANT, 'Mid. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('EE', INTEGRATION_POINT, (INVARIANT, 'Min. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('EE', INTEGRATION_POINT, (COMPONENT, 'EE11')))
    field_output_display_var_list.append(FieldOutputDisplay('EE', INTEGRATION_POINT, (COMPONENT, 'EE22')))
    field_output_display_var_list.append(FieldOutputDisplay('EE', INTEGRATION_POINT, (COMPONENT, 'EE33')))
    field_output_display_var_list.append(FieldOutputDisplay('EE', INTEGRATION_POINT, (COMPONENT, 'EE12')))
    field_output_display_var_list.append(FieldOutputDisplay('EE', INTEGRATION_POINT, (COMPONENT, 'EE13')))
    field_output_display_var_list.append(FieldOutputDisplay('EE', INTEGRATION_POINT, (COMPONENT, 'EE23')))

    #EENER
    field_output_display_var_list.append(FieldOutputDisplay('EENER', INTEGRATION_POINT,None))
    #EKEDEN
    field_output_display_var_list.append(FieldOutputDisplay('EKEDEN', WHOLE_ELEMENT,None))
    #ELASE
    field_output_display_var_list.append(FieldOutputDisplay('ELASE', WHOLE_ELEMENT,None))
    #ELCD
    field_output_display_var_list.append(FieldOutputDisplay('ELCD', WHOLE_ELEMENT,None))
    #ELCTE
    field_output_display_var_list.append(FieldOutputDisplay('ELCTE', WHOLE_ELEMENT,None))
    #ELDMD
    field_output_display_var_list.append(FieldOutputDisplay('ELDMD', WHOLE_ELEMENT,None))
    #ELJD
    field_output_display_var_list.append(FieldOutputDisplay('ELJD', WHOLE_ELEMENT,None))
    #ELKE
    field_output_display_var_list.append(FieldOutputDisplay('ELKE', WHOLE_ELEMENT,None))
    #ELPD
    field_output_display_var_list.append(FieldOutputDisplay('ELPD', WHOLE_ELEMENT,None))
    #ELSD
    field_output_display_var_list.append(FieldOutputDisplay('ELSD', WHOLE_ELEMENT,None))
    #ELSE
    field_output_display_var_list.append(FieldOutputDisplay('ELSE', WHOLE_ELEMENT,None))
    #ELVD
    field_output_display_var_list.append(FieldOutputDisplay('ELVD', WHOLE_ELEMENT,None))
    #EPDDEN
    field_output_display_var_list.append(FieldOutputDisplay('EPDDEN', WHOLE_ELEMENT,None))

    #ER
    field_output_display_var_list.append(FieldOutputDisplay('ER', INTEGRATION_POINT, (INVARIANT, 'Max. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('ER', INTEGRATION_POINT, (INVARIANT, 'Max. Principal (Abs)')))
    field_output_display_var_list.append(FieldOutputDisplay('ER', INTEGRATION_POINT, (INVARIANT, 'Mid. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('ER', INTEGRATION_POINT, (INVARIANT, 'Min. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('ER', INTEGRATION_POINT, (COMPONENT, 'ER11')))
    field_output_display_var_list.append(FieldOutputDisplay('ER', INTEGRATION_POINT, (COMPONENT, 'ER22')))
    field_output_display_var_list.append(FieldOutputDisplay('ER', INTEGRATION_POINT, (COMPONENT, 'ER33')))
    field_output_display_var_list.append(FieldOutputDisplay('ER', INTEGRATION_POINT, (COMPONENT, 'ER12')))
    field_output_display_var_list.append(FieldOutputDisplay('ER', INTEGRATION_POINT, (COMPONENT, 'ER13')))
    field_output_display_var_list.append(FieldOutputDisplay('ER', INTEGRATION_POINT, (COMPONENT, 'ER23')))

    #ESDDEN
    field_output_display_var_list.append(FieldOutputDisplay('ESDDEN', WHOLE_ELEMENT,None))
    #ESEDEN
    field_output_display_var_list.append(FieldOutputDisplay('ESEDEN', WHOLE_ELEMENT,None))
    #EVDDEN
    field_output_display_var_list.append(FieldOutputDisplay('EVDDEN', WHOLE_ELEMENT,None))
    #EVOL
    field_output_display_var_list.append(FieldOutputDisplay('EVOL', WHOLE_ELEMENT,None))

    #IE
    field_output_display_var_list.append(FieldOutputDisplay('IE', INTEGRATION_POINT, (INVARIANT, 'Max. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('IE', INTEGRATION_POINT, (INVARIANT, 'Max. Principal (Abs)')))
    field_output_display_var_list.append(FieldOutputDisplay('IE', INTEGRATION_POINT, (INVARIANT, 'Mid. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('IE', INTEGRATION_POINT, (INVARIANT, 'Min. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('IE', INTEGRATION_POINT, (COMPONENT, 'IE11')))
    field_output_display_var_list.append(FieldOutputDisplay('IE', INTEGRATION_POINT, (COMPONENT, 'IE22')))
    field_output_display_var_list.append(FieldOutputDisplay('IE', INTEGRATION_POINT, (COMPONENT, 'IE33')))
    field_output_display_var_list.append(FieldOutputDisplay('IE', INTEGRATION_POINT, (COMPONENT, 'IE12')))
    field_output_display_var_list.append(FieldOutputDisplay('IE', INTEGRATION_POINT, (COMPONENT, 'IE13')))
    field_output_display_var_list.append(FieldOutputDisplay('IE', INTEGRATION_POINT, (COMPONENT, 'IE23')))

    #IVOL
    field_output_display_var_list.append(FieldOutputDisplay('IVOL', INTEGRATION_POINT,None))
    #JENER
    field_output_display_var_list.append(FieldOutputDisplay('JENER', INTEGRATION_POINT,None))
    #MISESMAX
    field_output_display_var_list.append(FieldOutputDisplay('MISESMAX', INTEGRATION_POINT,None))

    #NFORC1
    field_output_display_var_list.append(FieldOutputDisplay('NFORC1', ELEMENT_NODAL,None))
    #NFORC2
    field_output_display_var_list.append(FieldOutputDisplay('NFORC2', ELEMENT_NODAL,None))
    #NFORC3
    field_output_display_var_list.append(FieldOutputDisplay('NFORC3', ELEMENT_NODAL,None))

    #PEEQ
    field_output_display_var_list.append(FieldOutputDisplay('PEEQ', INTEGRATION_POINT,None))
    #PEEQMAX
    field_output_display_var_list.append(FieldOutputDisplay('PEEQMAX', INTEGRATION_POINT,None))
    #PEEQT
    field_output_display_var_list.append(FieldOutputDisplay('PEEQT', INTEGRATION_POINT,None))
    #PENER
    field_output_display_var_list.append(FieldOutputDisplay('PENER', INTEGRATION_POINT,None))

    #PEQC1
    field_output_display_var_list.append(FieldOutputDisplay('PEQC1', INTEGRATION_POINT,None))
    #PEQC2
    field_output_display_var_list.append(FieldOutputDisplay('PEQC2', INTEGRATION_POINT,None))
    #PEQC3
    field_output_display_var_list.append(FieldOutputDisplay('PEQC3', INTEGRATION_POINT,None))
    #PEQC4
    field_output_display_var_list.append(FieldOutputDisplay('PEQC4', INTEGRATION_POINT,None))

    #PS
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (INVARIANT, 'Mises')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (INVARIANT, 'Max. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (INVARIANT, 'Max. Principal (Abs)')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (INVARIANT, 'Mid. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (INVARIANT, 'Min. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (INVARIANT, 'Tresca')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (INVARIANT, 'Pressure')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (INVARIANT, 'Third Invariant')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (COMPONENT, 'PSE11')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (COMPONENT, 'PS22')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (COMPONENT, 'PS33')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (COMPONENT, 'PS12')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (COMPONENT, 'PS13')))
    field_output_display_var_list.append(FieldOutputDisplay('PS', INTEGRATION_POINT, (COMPONENT, 'PS23')))

    #RD
    field_output_display_var_list.append(FieldOutputDisplay('RD', INTEGRATION_POINT,None))

    #RF
    field_output_display_var_list.append(FieldOutputDisplay('RF', NODAL, (INVARIANT, 'Magnitude')))
    field_output_display_var_list.append(FieldOutputDisplay('RF', NODAL, (COMPONENT, 'RF1')))
    field_output_display_var_list.append(FieldOutputDisplay('RF', NODAL, (COMPONENT, 'RF2')))
    field_output_display_var_list.append(FieldOutputDisplay('RF', NODAL, (COMPONENT, 'RF3')))

    #RM
    field_output_display_var_list.append(FieldOutputDisplay('RM', NODAL, (INVARIANT, 'Magnitude')))
    field_output_display_var_list.append(FieldOutputDisplay('RM', NODAL, (COMPONENT, 'RM1')))
    field_output_display_var_list.append(FieldOutputDisplay('RM', NODAL, (COMPONENT, 'RM2')))
    field_output_display_var_list.append(FieldOutputDisplay('RM', NODAL, (COMPONENT, 'RM3')))

    #SENER
    field_output_display_var_list.append(FieldOutputDisplay('SENER', INTEGRATION_POINT,None))

    #TEMP
    field_output_display_var_list.append(FieldOutputDisplay('TEMP', INTEGRATION_POINT,None))

    #TEMPR
    field_output_display_var_list.append(FieldOutputDisplay('TEMPR', INTEGRATION_POINT,None))

    #TF
    field_output_display_var_list.append(FieldOutputDisplay('TF', NODAL, (INVARIANT, 'Magnitude')))
    field_output_display_var_list.append(FieldOutputDisplay('TF', NODAL, (COMPONENT, 'TF1')))
    field_output_display_var_list.append(FieldOutputDisplay('TF', NODAL, (COMPONENT, 'TF2')))
    field_output_display_var_list.append(FieldOutputDisplay('TF', NODAL, (COMPONENT, 'TF3')))

    #THE
    field_output_display_var_list.append(FieldOutputDisplay('THE', INTEGRATION_POINT, (INVARIANT, 'Max. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('THE', INTEGRATION_POINT, (INVARIANT, 'Max. Principal (Abs)')))
    field_output_display_var_list.append(FieldOutputDisplay('THE', INTEGRATION_POINT, (INVARIANT, 'Mid. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('THE', INTEGRATION_POINT, (INVARIANT, 'Min. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('THE', INTEGRATION_POINT, (COMPONENT, 'THE11')))
    field_output_display_var_list.append(FieldOutputDisplay('THE', INTEGRATION_POINT, (COMPONENT, 'THE22')))
    field_output_display_var_list.append(FieldOutputDisplay('THE', INTEGRATION_POINT, (COMPONENT, 'THE33')))
    field_output_display_var_list.append(FieldOutputDisplay('THE', INTEGRATION_POINT, (COMPONENT, 'THE12')))
    field_output_display_var_list.append(FieldOutputDisplay('THE', INTEGRATION_POINT, (COMPONENT, 'THE13')))
    field_output_display_var_list.append(FieldOutputDisplay('THE', INTEGRATION_POINT, (COMPONENT, 'THE23')))

    #TRNOR
    field_output_display_var_list.append(FieldOutputDisplay('TRNOR', ELEMENT_FACE, (INVARIANT, 'Magnitude')))
    field_output_display_var_list.append(FieldOutputDisplay('TRNOR', ELEMENT_FACE, (COMPONENT, 'TRNOR1')))
    field_output_display_var_list.append(FieldOutputDisplay('TRNOR', ELEMENT_FACE, (COMPONENT, 'TRNOR1')))
    field_output_display_var_list.append(FieldOutputDisplay('TRNOR', ELEMENT_FACE, (COMPONENT, 'TRNOR2')))
    field_output_display_var_list.append(FieldOutputDisplay('TRNOR', ELEMENT_FACE, (COMPONENT, 'TRNOR3')))

    #TRSHR
    field_output_display_var_list.append(FieldOutputDisplay('TRSHR', ELEMENT_FACE, (INVARIANT, 'Magnitude')))
    field_output_display_var_list.append(FieldOutputDisplay('TRSHR', ELEMENT_FACE, (COMPONENT, 'TRSHR1')))
    field_output_display_var_list.append(FieldOutputDisplay('TRSHR', ELEMENT_FACE, (COMPONENT, 'TRSHR2')))
    field_output_display_var_list.append(FieldOutputDisplay('TRSHR', ELEMENT_FACE, (COMPONENT, 'TRSHR3')))

    #U
    field_output_display_var_list.append(FieldOutputDisplay('U', NODAL, (INVARIANT, 'Magnitude')))
    field_output_display_var_list.append(FieldOutputDisplay('U', NODAL, (COMPONENT, 'U1')))
    field_output_display_var_list.append(FieldOutputDisplay('U', NODAL, (COMPONENT, 'U2')))
    field_output_display_var_list.append(FieldOutputDisplay('U', NODAL, (COMPONENT, 'U3')))

    #UR
    field_output_display_var_list.append(FieldOutputDisplay('UR', NODAL, (INVARIANT, 'Magnitude')))
    field_output_display_var_list.append(FieldOutputDisplay('UR', NODAL, (COMPONENT, 'UR1')))
    field_output_display_var_list.append(FieldOutputDisplay('UR', NODAL, (COMPONENT, 'UR2')))
    field_output_display_var_list.append(FieldOutputDisplay('UR', NODAL, (COMPONENT, 'UR3')))

    #VENER
    field_output_display_var_list.append(FieldOutputDisplay('VENER', INTEGRATION_POINT,None))

    #VOIDR
    field_output_display_var_list.append(FieldOutputDisplay('VENER', INTEGRATION_POINT,None))

    #S
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (INVARIANT, 'Mises')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (INVARIANT, 'Max. In-Plane Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (INVARIANT, 'Max. In-Plane Principal (Abs)')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (INVARIANT, 'Min. In-Plane Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (INVARIANT, 'Out-of-Plane Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (INVARIANT, 'Max. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (INVARIANT, 'Mid. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (INVARIANT, 'Max. Principal (Abs)')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (INVARIANT, 'Min. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (INVARIANT, 'Tresca')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (INVARIANT, 'Pressure')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (COMPONENT, 'S11')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (COMPONENT, 'S22')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (COMPONENT, 'S33')))
    field_output_display_var_list.append(FieldOutputDisplay('S', INTEGRATION_POINT, (COMPONENT, 'S12')))

    #LE
    field_output_display_var_list.append(FieldOutputDisplay('LE', INTEGRATION_POINT, (INVARIANT, 'Max. In-Plane Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('LE', INTEGRATION_POINT, (INVARIANT, 'Max. In-Plane Principal (Abs)')))
    field_output_display_var_list.append(FieldOutputDisplay('LE', INTEGRATION_POINT, (INVARIANT, 'Min. In-Plane Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('LE', INTEGRATION_POINT, (INVARIANT, 'Out-of-Plane Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('LE', INTEGRATION_POINT, (INVARIANT, 'Max. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('LE', INTEGRATION_POINT, (INVARIANT, 'Mid. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('LE', INTEGRATION_POINT, (INVARIANT, 'Max. Principal (Abs)')))
    field_output_display_var_list.append(FieldOutputDisplay('LE', INTEGRATION_POINT, (INVARIANT, 'Min. Principal')))
    field_output_display_var_list.append(FieldOutputDisplay('LE', INTEGRATION_POINT, (COMPONENT, 'LE11')))
    field_output_display_var_list.append(FieldOutputDisplay('LE', INTEGRATION_POINT, (COMPONENT, 'LE22')))
    field_output_display_var_list.append(FieldOutputDisplay('LE', INTEGRATION_POINT, (COMPONENT, 'LE33')))
    field_output_display_var_list.append(FieldOutputDisplay('LE', INTEGRATION_POINT, (COMPONENT, 'LE12')))


    #CHYBA NIE MA WSZYSTKICH
    return field_output_display_var_list










    
