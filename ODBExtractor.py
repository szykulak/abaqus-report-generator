import os
import sys
from odbAccess import*
from textRepr import*
from abaqusConstants import *
import time
import visualization
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
from abaqus import session
import json 


class ODBExtractor(object):

    def __init__(self): 
        # self.odbs = []
        pass 

    def run_extractor(self):
        self.open_odbs()

    def open_odbs(self):
        config = open("C:\\tmp\\abaqus_plugins\\report_generator_plugin\\UserData.json") #TODO zeby nie byla zahardkodowana 

        data = json.load(config)
        odb_dir_path = data["ODB directory path"]

        for odb_file in os.listdir(odb_dir_path):
            odb = os.path.join(odb_dir_path, odb_file)

            if os.path.isfile(odb) and odb_file.endswith('.odb'):
                temp = openOdb(path=str(odb))
                name = str(odb).split("\\")[-1].split(".")[0]
                self.execute_without_ui(temp, name)
            else:
                continue
        

    def execute_without_ui(self, odb_object, name):
        file = open('C:\\tmp\\abaqus_plugins\\report_generator_plugin\\UserData.json')

        data = json.load(file)
        step_name = str(data["Step name"])
        frames = str(data["Frames"])
        field_output_names=str(data["Field output names"])
        set_name=str(data["Set name"])
        instance_name=str(data["Instance name"])
        instance_set_name=str(data["Instance set name"])
        folder_path=str(data["Folder path"])
        folder_name=str(data["Folder name"])
        file_name = name #nazwa uzywana jako nazwa folderu dla konkretnego odb 
        field_output=str(data["Field output"])
        value=str(data["Value"])
        minimum=data["Minimum"]
        maximum=data["Maximum"]
        views=data["Views"].split(",")

        self.export_to_csv(odb_object, step_name,frames,set_name,field_output_names,instance_name,instance_set_name,folder_path,folder_name,file_name,field_output,value,minimum,maximum)
        self.take_model_screenshots(odb_object, step_name,frames,set_name,field_output_names,instance_name,instance_set_name,folder_path,folder_name,file_name,field_output,value,minimum,maximum,views)
        #tu tez bd reszta wywolywana 
        #tu tez bd reszta wywolywana 

    def export_to_csv(self, odb_object, step_name,frames,set_name,field_output_names,instance_name,instance_set_name,folder_path,folder_name,file_name,field_output,value,minimum,maximum):

        print "executing export_to_csv "
        folder_path += "\\exported\\"
        folder_path += folder_name 
        folder_path += "\\"
        folder_path += file_name 
        folder_path += "\\"
        try:  
                os.makedirs(folder_path)
        except OSError as error:
            error

        framesList = self.parse_to_frames(frames)
        print "frames list " + str(framesList)
        for frame in framesList:
            
            file_name = folder_path
            file_name += "\\"
            file_name += str(frame)
            file_name += "\\"
           
            print("STARTING EXPORTING")

            modelPath = file_name + "\\model\\"

            try:  
                os.makedirs(modelPath)
            except OSError as error:
                print " " + str(error)

            fieldoutpuNamesTab = self.parse_to_field_output(field_output_names)
            print "field output names list " + str(fieldoutpuNamesTab)
            elementsInstancesNames = []
            elementsOffsetTable = {}
            nodesInstancesNames = []
            nodesOffsetTable = {}
            self.initiateFunction(odb_object, step_name, frame, elementsInstancesNames, elementsOffsetTable, nodesInstancesNames, nodesOffsetTable)

            # exportScaleFactor(modelPath)
            # exportCOORD(odb, modelPath, nodesInstancesNames, step, frame) # to dac jak bezie mes zaznaczony 
            # exportU(odb, modelPath, step, frame)

            if field_output != "":
                nodesElementsTab = self.exportFieldoutputFromRange(odb_object, modelPath, elementsInstancesNames, elementsOffsetTable, nodesOffsetTable, field_output, value, minimum, maximum, step_name, frame)
                self.exportSet(odb_object, step_name, frame, file_name, elementsInstancesNames, elementsOffsetTable, nodesElementsTab, fieldoutpuNamesTab)
            elif instance_name != "":
                nodesElementsTab = self.exportInstanceSetElements(odb_object, modelPath, elementsInstancesNames, nodesOffsetTable, instance_name, instance_set_name, elementsOffsetTable, step_name, frame)
                self.exportSet(odb_object, step_name, frame, file_name, elementsInstancesNames, elementsOffsetTable, nodesElementsTab, fieldoutpuNamesTab)
            elif set_name != "":
                nodesElementsTab = self.exportSetElements(odb_object, modelPath, elementsInstancesNames, nodesOffsetTable, set_name, elementsOffsetTable, step_name, frame)
                self.exportSet(odb_object, step_name, frame, file_name, elementsInstancesNames, elementsOffsetTable, nodesElementsTab, fieldoutpuNamesTab)
            else:
                self.exportElements(odb_object, modelPath, elementsInstancesNames, nodesOffsetTable)
                self.exportValues(odb_object, step_name, frame, file_name, elementsInstancesNames, elementsOffsetTable, fieldoutpuNamesTab)
        

    def initiateFunction(self, odb, step, frame, elementsInstancesNames, elementsOffsetTable, nodesInstancesNames, nodesOffsetTable):
     
        values = odb.steps[step].frames[frame].fieldOutputs["S"].values
        for i in range(len(odb.steps[step].frames[frame].fieldOutputs["S"].values)):
            if values[i].elementLabel == 1 and values[i].integrationPoint == 1:
                if str(values[i].instance) != "None":
                    elementsOffsetTable[values[i].instance.name] = i-1
                    elementsInstancesNames.append(values[i].instance.name)

        values = odb.steps[step].frames[frame].fieldOutputs["U"].values
        for i in range(len(odb.steps[step].frames[frame].fieldOutputs["U"].values)):
            if values[i].nodeLabel == 1:
                if str(values[i].instance) != "None":
                    nodesOffsetTable[values[i].instance.name] = i-1
                    nodesInstancesNames.append(values[i].instance.name)
                else:
                    nodesOffsetTable[""] = i-1
                    nodesInstancesNames.append("") 

    def exportFieldoutputFromRange(self, odb, modelPath, elementsInstancesNames, elementsOffsetTable, nodesOffsetTable, fieldOutput, valueName, minimum, maximum, step, frame):
        tab = []
        tab.append([])
        tab.append([])
        if valueName == "value":
            index = -1
        elif valueName == "inv3":
            index = -2
        elif valueName == "magnitude":
            index = -3
        elif valueName == "maxInPlanePrincipal":
            index = -4
        elif valueName == "maxPrincipal":
            index = -5
        elif valueName == "midPrincipal":
            index = -6
        elif valueName == "minInPlanePrincipal":
            index = -7
        elif valueName == "minPrincipal":
            index = -8
        elif valueName == "mises":
            index = -9
        elif valueName == "outOfPlanePrincipal":
            index = -10
        elif valueName == "press":
            index = -11
        elif valueName == "tresca":
            index = -12
        else:
            index = odb.steps[step].frames[frame].fieldOutputs[fieldOutput].componentLabels.index(valueName)
        value = odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values
        if len(odb.steps[step].frames[frame].fieldOutputs["U"].values[0].data) == 3:
            dimension = 3
        else:
            dimension = 2
        myFile = open(modelPath+'ELEMENTS.csv','w')
        if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutput].values[0].elementLabel) != "None":
            for i in range(len(elementsInstancesNames)):
                elementOffset = elementsOffsetTable[elementsInstancesNames[i]]
                for j in range(len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements)):
                    if odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j][0].instanceNames[0] == elementsInstancesNames[i]:
                        indexOfElement = 1 + elementsOffsetTable[elementsInstancesNames[i]]
                        elements = odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j]
                        for k in range(len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j])):
                            if dimension == 2 and len(elements[k].connectivity) == 6:
                                amountCounter = 3
                            elif dimension == 2 and len(elements[k].connectivity) == 8:
                                amountCounter = 4
                            elif dimension == 3 and len(elements[k].connectivity) == 10:
                                amountCounter = 4
                            elif dimension == 3 and len(elements[k].connectivity) == 20:
                                amountCounter = 8
                            else:
                                amountCounter = 1
                            tmpValue = 0
                            if index >= 0:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].data[index]
                            elif index == -1:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].data
                            elif index == -2:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].inv3
                            elif index == -3:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].magnitude
                            elif index == -4:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].maxInPlanePrincipal
                            elif index == -5:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].maxPrincipal
                            elif index == -6:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].midPrincipal
                            elif index == -7:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].minInPlanePrincipal
                            elif index == -8:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].minPrincipal
                            elif index == -9:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].mises
                            elif index == -10:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].outOfPlanePrincipal
                            elif index == -11:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].press
                            elif index == -12:
                                for y in range(amountCounter):
                                    tmpValue += value[(elements[k].label + elementOffset)*amountCounter + y].tresca
                            tmpValue /= amountCounter
                            if tmpValue >= min:
                                if tmpValue <= max:
                                    for z in range(amountCounter):
                                        tab[1].append(indexOfElement + z)
                                        #tab[1].append((elements[k].label + elementOffset)*amountCounter + z)
                                    for x in range(len(elements[k].connectivity)):
                                        myFile.write(str(elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]) + " ")
                                        tab[0].append(elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]])
                                    myFile.write("\n")
                            indexOfElement += amountCounter
                        break
        else:
            for i in range(len(elementsInstancesNames)):
                elementOffset = elementsOffsetTable[elementsInstancesNames[i]]
                for j in range(len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements)):
                    if odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j][0].instanceNames[0] == elementsInstancesNames[i]:
                        indexOfElement = 1 + elementsOffsetTable[elementsInstancesNames[i]]
                        elements = odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j]
                        for k in range(len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j])):
                            if dimension == 2 and len(elements[k].connectivity) == 6:
                                amountCounter = 3
                            elif dimension == 2 and len(elements[k].connectivity) == 8:
                                amountCounter = 4
                            elif dimension == 3 and len(elements[k].connectivity) == 10:
                                amountCounter = 4
                            elif dimension == 3 and len(elements[k].connectivity) == 20:
                                amountCounter = 8
                            else:
                                amountCounter = 1
                            condition = False
                            if index >= 0:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].data[index] >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].data[index] <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            elif index == -1:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].data >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].data <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            elif index == -2:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].inv3 >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].inv3 <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            elif index == -3:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].magnitude >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].magnitude <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            elif index == -4:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].maxInPlanePrincipal >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].maxInPlanePrincipal <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            elif index == -5:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].maxPrincipal >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].maxPrincipal <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            elif index == -6:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].midPrincipal >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].midPrincipal <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            elif index == -7:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].minInPlanePrincipal >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].minInPlanePrincipal <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            elif index == -8:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].minPrincipal >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].minPrincipal <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            elif index == -9:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].mises >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].mises <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            elif index == -10:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].outOfPlanePrincipal >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].outOfPlanePrincipal <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            elif index == -11:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].press >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].press <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            elif index == -12:
                                for x in range(len(elements[k].connectivity)):
                                    if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].tresca >= minimum:
                                        if value[elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]].tresca <= maximum:
                                            condition = True
                                        else:
                                            condition = False
                                            break
                                    else:
                                        condition = False
                                        break
                            if condition:
                                for z in range(amountCounter):
                                    tab[1].append(indexOfElement + z)
                                    #tab[1].append((elements[k].label + elementOffset)*amountCounter + z)
                                for x in range(len(elements[k].connectivity)):
                                    myFile.write(str(elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]) + " ")
                                    tab[0].append(elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]])
                                myFile.write("\n")
                            indexOfElement += amountCounter
                        break
        myFile.close()
        tab[0] = self.removeRedundant(tab[0])
        tab[1] = self.removeRedundant(tab[1])
        return tab

    def exportSetElements(self, odb, modelPath, elementsInstancesNames, nodesOffsetTable, setName, elementsOffsetTable, step, frame):
        tab = []
        tab.append([])
        tab.append([])
        myFile = open(modelPath+'ELEMENTS.csv','w')
        elements = odb.rootAssembly.elementSets[setName].elements[0]
        if len(odb.steps[step].frames[frame].fieldOutputs["U"].values[0].data) == 3:
            for i in range(len(odb.rootAssembly.elementSets[setName].elements[0])):
                for x in range(len(elements[i].connectivity)):
                    myFile.write(str(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]]) + " ")
                    tab[0].append(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]])
                myFile.write("\n")
                if len(elements[i].connectivity) == 20:
                    for j in range(8):
                        tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*8 + j)
                elif len(elements[i].connectivity) == 10:
                    for j in range(4):
                        tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*4 + j)
                else:
                    tab[1].append(elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])
        else:
            for i in range(len(odb.rootAssembly.elementSets[setName].elements[0])):
                for x in range(len(elements[i].connectivity)):
                    myFile.write(str(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]]) + " ")
                    tab[0].append(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]])
                myFile.write("\n")
                if len(elements[i].connectivity) == 8:
                    for j in range(4):
                        tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*4 + j)
                elif len(elements[i].connectivity) == 6:
                    for j in range(3):
                        tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*3 + j)
                else:
                    tab[1].append(elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])
        myFile.close()
        tab[0] = self.removeRedundant(tab[0])
        tab[1] = self.removeRedundant(tab[1])
        return tab

    def exportElements(self, odb, modelPath, elementsInstancesNames, nodesOffsetTable):
        print "model path " + modelPath
        myFile = open(modelPath+'ELEMENTS.csv','w')
        for i in range(len(elementsInstancesNames)):
            for j in range(len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements)):
                if odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j][0].instanceNames[0] == elementsInstancesNames[i]:
                    elements = odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j]
                    for k in range(len(odb.rootAssembly.elementSets[" ALL ELEMENTS"].elements[j])):
                        for x in range(len(elements[k].connectivity)):
                            myFile.write(str(elements[k].connectivity[x] + nodesOffsetTable[elementsInstancesNames[i]]) + " ")
                        myFile.write("\n")
                    break
        myFile.close()
    
    def exportInstanceSetElements(self, odb, modelPath, elementsInstancesNames, nodesOffsetTable, instanceName, instanceSetName, elementsOffsetTable, step, frame):
        tab = []
        tab.append([])
        tab.append([])
        myFile = open(modelPath+'ELEMENTS.csv','w')
        elements = odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements
        if len(odb.steps[step].frames[frame].fieldOutputs["U"].values[0].data) == 3:
            index = 1 + elementsOffsetTable[elements[0].instanceNames[0]]
            for i in range(len(odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements)):
                for x in range(len(elements[i].connectivity)):
                    myFile.write(str(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]]) + " ")
                    tab[0].append(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]])
                myFile.write("\n")
                if len(elements[i].connectivity) == 20:
                    for j in range(8):
                        tab[1].append(index + j)
                    index += 8
                        #tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*8 + j)
                elif len(elements[i].connectivity) == 10:
                    for j in range(4):
                        tab[1].append(index + j)
                    index += 4
                        #tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*4 + j)
                else:
                    tab[1].append(elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])
        else:
            index = 1 + elementsOffsetTable[elements[0].instanceNames[0]]
            for i in range(len(odb.rootAssembly.instances[instanceName].elementSets[instanceSetName].elements)):
                for x in range(len(elements[i].connectivity)):
                    myFile.write(str(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]]) + " ")
                    tab[0].append(elements[i].connectivity[x] + nodesOffsetTable[elements[i].instanceNames[0]])
                myFile.write("\n")
                if len(elements[i].connectivity) == 8:
                    for j in range(4):
                        tab[1].append(index + j)
                    index += 4
                        #tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*4 + j)
                elif len(elements[i].connectivity) == 6:
                    for j in range(3):
                        tab[1].append(index + j)
                    index += 3
                        #tab[1].append((elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])*3 + j)
                else:
                    tab[1].append(elements[i].label + elementsOffsetTable[elements[i].instanceNames[0]])
        myFile.close()
        tab[0] = self.removeRedundant(tab[0])
        tab[1] = self.removeRedundant(tab[1])
        return tab

    def exportValues(self, odb, step, frame, fileName, elementsInstancesNames, elementsOffsetTable, fieldoutpuNamesTab):
        tabFilesHandler = []
        if len(fieldoutpuNamesTab) == 0:
            fieldOutputKeys = odb.steps[step].frames[frame].fieldOutputs.keys()
        else:
            fieldOutputKeys = fieldoutpuNamesTab
        for i in range(len(fieldOutputKeys)):
            try:  
                os.makedirs(fileName + fieldOutputKeys[i])
            except OSError as error:
                error
            if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values[0].elementLabel) != "None":
                fieldOutputComponentLabelsKeys = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].componentLabels
                for j in range(len(fieldOutputComponentLabelsKeys)):
                    myFile = open(fileName + fieldOutputKeys[i] + "\\" + fieldOutputComponentLabelsKeys[j] +".csv",'w')
                    for k in range(len(elementsInstancesNames)):
                        index = elementsOffsetTable[elementsInstancesNames[k]]
                        if k != len(elementsInstancesNames) - 1:
                            size = elementsOffsetTable[elementsInstancesNames[k+1]] - index
                        else:
                            size = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values) - index - 1
                        values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
                        offset = elementsOffsetTable[elementsInstancesNames[k]] + 1
                        for x in range(size):
                            myFile.write(str(values[x + offset].data[j]) + "\n")
                    myFile.write("ELEMENT")
                    myFile.close()
                if len(fieldOutputComponentLabelsKeys) == 0:
                    myFile = open(fileName + fieldOutputKeys[i] + "\\" + "value.csv",'w')
                    for k in range(len(elementsInstancesNames)):
                        index = elementsOffsetTable[elementsInstancesNames[k]]
                        if k != len(elementsInstancesNames) - 1:
                            size = elementsOffsetTable[elementsInstancesNames[k+1]] - index
                        else:
                            size = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values) - index - 1
                        values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
                        offset = elementsOffsetTable[elementsInstancesNames[k]] + 1
                        for x in range(size):
                            myFile.write(str(values[x + offset].data) + "\n")
                    myFile.write("ELEMENT")
                    myFile.close()
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\inv3.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\magnitude.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxInPlanePrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxPrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\midPrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minInPlanePrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minPrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\mises.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\outOfPlanePrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\press.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\tresca.csv","w"))
                for k in range(len(elementsInstancesNames)):
                    index = elementsOffsetTable[elementsInstancesNames[k]]
                    if k != len(elementsInstancesNames) - 1:
                        size = elementsOffsetTable[elementsInstancesNames[k+1]] - index
                    else:
                        size = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values) - index - 1
                    values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
                    offset = elementsOffsetTable[elementsInstancesNames[k]] + 1
                    for x in range(size):
                        tabFilesHandler[0].write(str(values[x + offset].inv3) + "\n")
                        tabFilesHandler[1].write(str(values[x + offset].magnitude) + "\n")
                        tabFilesHandler[2].write(str(values[x + offset].maxInPlanePrincipal) + "\n")
                        tabFilesHandler[3].write(str(values[x + offset].maxPrincipal) + "\n")
                        tabFilesHandler[4].write(str(values[x + offset].midPrincipal) + "\n")
                        tabFilesHandler[5].write(str(values[x + offset].minInPlanePrincipal) + "\n")
                        tabFilesHandler[6].write(str(values[x + offset].minPrincipal) + "\n")
                        tabFilesHandler[7].write(str(values[x + offset].mises) + "\n")
                        tabFilesHandler[8].write(str(values[x + offset].outOfPlanePrincipal) + "\n")
                        tabFilesHandler[9].write(str(values[x + offset].press) + "\n")
                        tabFilesHandler[10].write(str(values[x + offset].tresca) + "\n")
                for j in range(len(tabFilesHandler)):
                    tabFilesHandler[j].write("ELEMENT")
                for j in range(len(tabFilesHandler)):
                    tabFilesHandler[j].close()
                tabFilesHandler = []
            else:
                fieldOutputComponentLabelsKeys = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].componentLabels
                for j in range(len(fieldOutputComponentLabelsKeys)):
                    myFile = open(fileName + fieldOutputKeys[i] + "\\" + fieldOutputComponentLabelsKeys[j] +".csv",'w')
                    size = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values)
                    values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
                    for x in range(size):
                        myFile.write(str(values[x].data[j]) + "\n")
                    myFile.write("NODAL")
                    myFile.close()
                if len(fieldOutputComponentLabelsKeys) == 0:
                    myFile = open(fileName + fieldOutputKeys[i] + "\\" + "value.csv",'w')
                    size = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values)
                    values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
                    for x in range(size):
                        myFile.write(str(values[x].data) + "\n")
                    myFile.write("NODAL")
                    myFile.close()
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\inv3.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\magnitude.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxInPlanePrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxPrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\midPrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minInPlanePrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minPrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\mises.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\outOfPlanePrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\press.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\tresca.csv","w"))
                size = len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values)
                values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
                for x in range(size):
                    tabFilesHandler[0].write(str(values[x].inv3) + "\n")
                    tabFilesHandler[1].write(str(values[x].magnitude) + "\n")
                    tabFilesHandler[2].write(str(values[x].maxInPlanePrincipal) + "\n")
                    tabFilesHandler[3].write(str(values[x].maxPrincipal) + "\n")
                    tabFilesHandler[4].write(str(values[x].midPrincipal) + "\n")
                    tabFilesHandler[5].write(str(values[x].minInPlanePrincipal) + "\n")
                    tabFilesHandler[6].write(str(values[x].minPrincipal) + "\n")
                    tabFilesHandler[7].write(str(values[x].mises) + "\n")
                    tabFilesHandler[8].write(str(values[x].outOfPlanePrincipal) + "\n")
                    tabFilesHandler[9].write(str(values[x].press) + "\n")
                    tabFilesHandler[10].write(str(values[x].tresca) + "\n")
                for j in range(len(tabFilesHandler)):
                    tabFilesHandler[j].write("NODAL")
                for j in range(len(tabFilesHandler)):
                    tabFilesHandler[j].close()
                tabFilesHandler = []

    def exportSet(self, odb, step, frame, fileName, elementsInstancesNames, elementsOffsetTable, nodesElementsTab, fieldoutpuNamesTab):
        if len(nodesElementsTab[0]) == 0:
            print("DID NOT FIND ANY SUITABLE ELEMENTS")
            return 0
        tabFilesHandler = []
        if len(fieldoutpuNamesTab) == 0:
            fieldOutputKeys = odb.steps[step].frames[frame].fieldOutputs.keys()
        else:
            fieldOutputKeys = fieldoutpuNamesTab
        for i in range(len(fieldOutputKeys)):
            try:  
                os.makedirs(fileName + fieldOutputKeys[i])
            except OSError as error:
                error
            if str(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values[0].elementLabel) != "None":
                fieldOutputComponentLabelsKeys = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].componentLabels
                for j in range(len(fieldOutputComponentLabelsKeys)):
                    myFile = open(fileName + fieldOutputKeys[i] + "\\" + fieldOutputComponentLabelsKeys[j] +".csv",'w')
                    values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
                    for x in range(len(nodesElementsTab[1])):
                        myFile.write(str(values[nodesElementsTab[1][x]].data[j]) + "\n")
                    myFile.write("ELEMENT")
                    myFile.close()
                if len(fieldOutputComponentLabelsKeys) == 0:
                    myFile = open(fileName + fieldOutputKeys[i] + "\\" + "value.csv",'w')
                    values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
                    for x in range(len(nodesElementsTab[1])):
                        myFile.write(str(values[nodesElementsTab[1][x]].data) + "\n")
                    myFile.write("ELEMENT")
                    myFile.close()
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\inv3.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\magnitude.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxInPlanePrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxPrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\midPrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minInPlanePrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minPrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\mises.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\outOfPlanePrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\press.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\tresca.csv","w"))
                values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
                for x in range(len(nodesElementsTab[1])):
                        tabFilesHandler[0].write(str(values[nodesElementsTab[1][x]].inv3) + "\n")
                        tabFilesHandler[1].write(str(values[nodesElementsTab[1][x]].magnitude) + "\n")
                        tabFilesHandler[2].write(str(values[nodesElementsTab[1][x]].maxInPlanePrincipal) + "\n")
                        tabFilesHandler[3].write(str(values[nodesElementsTab[1][x]].maxPrincipal) + "\n")
                        tabFilesHandler[4].write(str(values[nodesElementsTab[1][x]].midPrincipal) + "\n")
                        tabFilesHandler[5].write(str(values[nodesElementsTab[1][x]].minInPlanePrincipal) + "\n")
                        tabFilesHandler[6].write(str(values[nodesElementsTab[1][x]].minPrincipal) + "\n")
                        tabFilesHandler[7].write(str(values[nodesElementsTab[1][x]].mises) + "\n")
                        tabFilesHandler[8].write(str(values[nodesElementsTab[1][x]].outOfPlanePrincipal) + "\n")
                        tabFilesHandler[9].write(str(values[nodesElementsTab[1][x]].press) + "\n")
                        tabFilesHandler[10].write(str(values[nodesElementsTab[1][x]].tresca) + "\n")
                for j in range(len(tabFilesHandler)):
                    tabFilesHandler[j].write("ELEMENT")
                for j in range(len(tabFilesHandler)):
                    tabFilesHandler[j].close()
                tabFilesHandler = []

            else:
                fieldOutputComponentLabelsKeys = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].componentLabels
                for j in range(len(fieldOutputComponentLabelsKeys)):
                    myFile = open(fileName + fieldOutputKeys[i] + "\\" + fieldOutputComponentLabelsKeys[j] +".csv",'w')
                    values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
                    tmpIndex = 0
                    maxIndex = len(nodesElementsTab[0])
                    for k in range(len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values)):
                        if k == nodesElementsTab[0][tmpIndex]:
                            myFile.write(str(values[k].data[j]) + "\n")
                            tmpIndex += 1
                            if tmpIndex == maxIndex:
                                tmpIndex = 0
                        else:
                            myFile.write("None\n")
                    myFile.write("NODAL")
                    myFile.close()
                if len(fieldOutputComponentLabelsKeys) == 0:
                    myFile = open(fileName + fieldOutputKeys[i] + "\\" + "value.csv",'w')
                    values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
                    tmpIndex = 0
                    maxIndex = len(nodesElementsTab[0])
                    for k in range(len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values)):
                        if k == nodesElementsTab[0][tmpIndex]:
                            myFile.write(str(values[k].data) + "\n")
                            tmpIndex += 1
                            if tmpIndex == maxIndex:
                                tmpIndex = 0
                        else:
                            myFile.write("None\n")
                    myFile.write("NODAL")
                    myFile.close()
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\inv3.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\magnitude.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxInPlanePrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\maxPrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\midPrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minInPlanePrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\minPrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\mises.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\outOfPlanePrincipal.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\press.csv","w"))
                tabFilesHandler.append(open(fileName + fieldOutputKeys[i] + "\\tresca.csv","w"))
                values = odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values
                tmpIndex = 0
                maxIndex = len(nodesElementsTab[0])
                for k in range(len(odb.steps[step].frames[frame].fieldOutputs[fieldOutputKeys[i]].values)):
                    if k == nodesElementsTab[0][tmpIndex]:
                        tabFilesHandler[0].write(str(values[k].inv3) + "\n")
                        tabFilesHandler[1].write(str(values[k].magnitude) + "\n")
                        tabFilesHandler[2].write(str(values[k].maxInPlanePrincipal) + "\n")
                        tabFilesHandler[3].write(str(values[k].maxPrincipal) + "\n")
                        tabFilesHandler[4].write(str(values[k].midPrincipal) + "\n")
                        tabFilesHandler[5].write(str(values[k].minInPlanePrincipal) + "\n")
                        tabFilesHandler[6].write(str(values[k].minPrincipal) + "\n")
                        tabFilesHandler[7].write(str(values[k].mises) + "\n")
                        tabFilesHandler[8].write(str(values[k].outOfPlanePrincipal) + "\n")
                        tabFilesHandler[9].write(str(values[k].press) + "\n")
                        tabFilesHandler[10].write(str(values[k].tresca) + "\n")
                        tmpIndex += 1
                        if tmpIndex == maxIndex:
                            tmpIndex = 0
                    else:
                        tabFilesHandler[0].write("None\n")
                        tabFilesHandler[1].write("None\n")
                        tabFilesHandler[2].write("None\n")
                        tabFilesHandler[3].write("None\n")
                        tabFilesHandler[4].write("None\n")
                        tabFilesHandler[5].write("None\n")
                        tabFilesHandler[6].write("None\n")
                        tabFilesHandler[7].write("None\n")
                        tabFilesHandler[8].write("None\n")
                        tabFilesHandler[9].write("None\n")
                        tabFilesHandler[10].write("None\n")
                for j in range(len(tabFilesHandler)):
                    tabFilesHandler[j].write("NODAL")
                for j in range(len(tabFilesHandler)):
                    tabFilesHandler[j].close()
                tabFilesHandler = []

    def take_model_screenshots(self, odb_object, step_name,frames,set_name,field_output_names,instance_name,
                               instance_set_name,folder_path,folder_name,file_name,field_output,value,minimum,maximum, views):
        frames_list = self.parse_to_frames(frames)
        field_outputs = self.parse_to_field_output(field_output_names)
        # print "frames list " + str(framesList)
            
        #     file_name = folder_path
        #     file_name += "\\"
        #     file_name += str(frame)
        #     file_name += "\\"
           
        #     print("STARTING EXPORTING")

        #     modelPath = file_name + "\\model\\"

        #     try:  
        #         os.makedirs(modelPath)
        #     except OSError as error:
        #         print " " + str(error)

        #     fieldoutpuNamesTab = self.parse_to_field_output(field_output_names)
        #todo ustawic biale tlo
        # https://classes.engineering.wustl.edu/2009/spring/mase5513/abaqus/docs/v6.5/books/cmd/default.htm?startat=pt03ch07s02.html
        session.viewports['Viewport: 1'].setValues(displayedObject=odb_object)
        folder_path += "\\exported\\"
        folder_path += folder_name 
        folder_path += "\\"
        folder_path += file_name 
        folder_path += "\\"
        screenshots_dir_path = folder_path + "screenshots"
        screenshots_dir_path += "\\"
        screenshots_dir_path += step_name
        screenshots_dir_path += "\\"

        #todo pamietac zeby tworzyc folder za kazdym razem jak modyfikuje sciezke bo samo sie nie zrobi 
        # dodad jeszze folder na step maybe
        # mapowanie na invariant/component itd ??? 

        for frame in frames_list:
            session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_name, 
            frame=frame)
            screenshot_path = screenshots_dir_path + str(frame)
            screenshot_path += "\\"
            for field_output in field_outputs: #??
                screenshot_path += field_output
                screenshot_path += "\\"
                session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
                variableLabel=field_output, outputPosition=INTEGRATION_POINT,refinement=(
                COMPONENT, 'S11'), )
                try:  
                    os.makedirs(screenshot_path)
                except OSError as error:
                    error
                
            for view in views: #albo zapisac wszystkie rzuty w jednym pliku????
                screenshot_name = screenshot_path +view
                # todo screeny dla poszczegolnych frames, field outputs etc
                # test_path = "C:\\tmp\\test\\exported\\plugintest\\jakis_model2\\"+view # musi byc folder utworzony wczesniej i nie musi byc relative path do folderu gdzie jest plugin
                session.viewports['Viewport: 1'].view.setValues(session.views[str(view)])
                session.printToFile(fileName=str(screenshot_name), format=PNG, canvasObjects=((session.viewports['Viewport: 1'], )))

           



        #todo thincc - najpierw zrobic screeny dla rzutow dla byle jakiego stepu dla calego modelu potem myslec co dalej 
    #     session.printToFile(
    # fileName=filepathImage,
    # format=PNG, canvasObjects=(session.viewports['Viewport: 1'],
    # session.viewports['Viewport: 3'], session.viewports['Viewport: 2']))  
        



    def removeRedundant(self, listTmp):
        listTmp.sort()
        listTmp2 = []
        prev = -1
        for i in range(len(listTmp)):
            if prev != listTmp[i]:
                listTmp2.append(listTmp[i])
                prev = listTmp[i]
        return listTmp2

        
    def parse_to_field_output(self, field_outputs_string):
        field_output_list = field_outputs_string.split(",")

        return field_output_list

    def parse_to_frames(self, string):
        frameList = []
        if string == "":
            return frameList
        tmp = ""
        counter = 0
        lastSign = "-"
        for i in string:
            if i == ",":
                lastSign = ","
            if i == "-":
                lastSign = "-"

        if lastSign == "-":
            string += ","

        for i in range(len(string)):
            if string[counter] == ",":
                frameList.append(int(tmp))
                tmp = ""
            elif string[counter] == "-":
                tmpInt1 = int(tmp)
                tmp = ""
                for j in range(counter+1,len(string)):
                    if string[j] == ",":
                        tmpInt2 = int(tmp)
                        tmp = ""
                        counter += 1
                        break
                    else:
                        tmp += string[j]
                    counter += 1
                for j in range(tmpInt1,tmpInt2+1):
                    frameList.append(j)
            else:
                tmp += string[counter]
            counter += 1
            if counter == len(string):
                break
        if tmp != "":
            frameList.append(int(tmp))
        return frameList

    