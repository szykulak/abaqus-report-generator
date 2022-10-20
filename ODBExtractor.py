from multiprocessing.sharedctypes import Value
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
from collections import OrderedDict
from FieldOutputUtils import set_field_output_display_variables
from fpdf import FPDF
import glob
import win32com.client
# from docx import Document
#   https://www.partitionwizard.com/partitionmanager/the-specified-module-could-not-be-found.html
# https://www.researchgate.net/post/Hello_everyone_I_am_trying_to_import_python_libraries_such_as_PANDA_and_pywin32_in_Abaqus_environment_Can_i_know_if_anyone_has_tried_this_please



class ODBExtractor(object):

    def __init__(self, user_data): 
        self.user_data = user_data
        self.field_output_display_vars = set_field_output_display_variables()
        self.pdf_report = None

    def run_extractor(self):
        self.open_odbs()

    def open_odbs(self):

        data = self.user_data
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

        data = self.user_data
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
        views=data["Views"]
        fo_vars = data["Field output display variables"]
        export_to_csv = data["Export to csv"]
        take_screenshots = data["Take model screenshots"]
        include_mesh_data = data["Include mesh data"]
        mesh_on = data["Mesh on"]

        self.pdf_report = FPDF(orientation = 'P', unit = 'mm', format='A4')
        self.pdf_report.add_page() 
        self.pdf_report.set_auto_page_break(auto=True)
        self.pdf_report.set_font('Arial', 'B', 16)

        
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt= "Simulation report ")
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
        self.pdf_report.set_font('Arial', 'B', 14)
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt= "Table of contents ")
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
        self.pdf_report.set_font('Arial', '', 11)
        ord_number = 1
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt= str(ord_number)+". Overview ")
        ord_number +=1
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt=str(ord_number)+". Assembly data")
        ord_number +=1
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt=str(ord_number)+". Material properties ")
        ord_number +=1
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt=str(ord_number)+". Steps information ")
        ord_number +=1
        if take_screenshots:
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt=str(ord_number)+". Results visualisation ")
            ord_number +=1
        if include_mesh_data:
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt=str(ord_number)+". Mesh properties")
            ord_number +=1
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")

        self.pdf_report.set_font('Arial', 'B', 14)
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Overwiew")
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
        # todo table of contents
        self.pdf_report.set_font('Arial', '', 11)
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt= "Model name: "+name)
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt= "Geometry: ")
        self.take_geometry_screenshot(odb_object,folder_path,folder_name)
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")

        # todo jakies table of contents, assembly data itp
        # self.pdf_report.set_font('Arial', 'B', 14)
        self.pdf_report.set_font('Arial', 'B', 14)
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Assembly data")
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
        self.pdf_report.set_font('Arial', '', 11)
        self.get_assembly_information(odb_object,folder_path,folder_name)
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
        self.pdf_report.set_font('Arial', 'B', 14)
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Material properties ")
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
        self.pdf_report.set_font('Arial', '', 11)
        self.get_material_properties(odb_object)
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
        self.pdf_report.set_font('Arial', 'B', 14)
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Steps information ")
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
        self.pdf_report.set_font('Arial', '', 11)
        self.get_steps_data(odb_object)
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")

        
        if export_to_csv:
            self.export_to_csv(odb_object, step_name,frames,set_name,field_output_names,instance_name,instance_set_name,folder_path,folder_name,file_name,field_output,value,minimum,maximum)
        if take_screenshots:
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
            self.pdf_report.set_font('Arial', 'B', 14)
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Results visualisation ")
            self.pdf_report.set_font('Arial', '', 11)
            self.take_model_screenshots(odb_object, step_name,frames,folder_path,folder_name,file_name,views,fo_vars,mesh_on)
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
            self.pdf_report.set_font('Arial', '', 11)
        if include_mesh_data:
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
            self.pdf_report.set_font('Arial', 'B', 14)
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Mesh properties")
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
            self.pdf_report.set_font('Arial', '', 11)
            self.get_mesh_properties(odb_object)
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
        
        self.create_pdf_report(name, folder_path,folder_name)
        
    def create_pdf_report(self, odb_name, folder_path, folder_name): # https://pyfpdf.readthedocs.io/en/latest/reference/FPDF/index.html
        # fpdf = FPDF(orientation = 'P', unit = 'mm', format='A4')
        # 
        path = folder_path + "\\"
        path += folder_name
        path += "\\"
        pdfs_path = path
        path += odb_name  
        try:  
                os.makedirs(path)
        except OSError as error:
            error
        path += '_report.pdf'
        self.pdf_report.output(path, 'F')
        word = win32com.client.Dispatch("Word.Application")
        word.visible = 1

        # pdfs_path = "C:\\Users\\asus\\Desktop\\rep\\"  # folder where the .pdf files are stored
        reqs_path = pdfs_path #?
        for i, doc in enumerate(glob.iglob(pdfs_path + "*.pdf")):
            print(doc)
            filename = doc.split('\\')[-1]
            in_file = os.path.abspath(doc)
            print(in_file)
            wb = word.Documents.Open(in_file)
            out_file = os.path.abspath(reqs_path + filename[0:-4] + ".docx".format(i))
            print("outfile\n", out_file)
            wb.SaveAs2(out_file, FileFormat=16)  # file format for docx
            print("success...")
            wb.Close()

        word.Quit()
        
        

         

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
        # print "frames list " + str(framesList)
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
            # print "field output names list " + str(fieldoutpuNamesTab)
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
        # print "model path " + modelPath
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

    def take_model_screenshots(self, odb_object, step_name,frames,folder_path,folder_name,file_name,views,fo_vars,mesh_on):
        print "executing take_model_screenshots"

        views_list=views.split(",")
        frames_list = self.parse_to_frames(frames)
        if mesh_on is False:
            session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
        visibleEdges=FEATURE)
        else:
            session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
        visibleEdges=EXTERIOR)


        session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(triad=OFF, 
        legend=ON, title=OFF, state=OFF, annotations=OFF, compass=OFF, legendBox=OFF, legendNumberFormat=FIXED)
        session.graphicsOptions.setValues(backgroundStyle=SOLID, 
        backgroundColor='#FFFFFF')
        session.viewports['Viewport: 1'].setValues(displayedObject=odb_object)
        session.mdbData.summary()
        session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
        CONTOURS_ON_DEF, ))
        folder_path += "\\exported\\"
        folder_path += folder_name 
        folder_path += "\\"
        folder_path += file_name 
        folder_path += "\\"
        screenshots_dir_path = folder_path + "screenshots"
        screenshots_dir_path += "\\"
        screenshots_dir_path += step_name
        screenshots_dir_path += "\\" 
        plot_limits = self.parse_contour_plot_limits()

        for frame in frames_list:
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt= "")
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt= "Frame "+str(frame))
            session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_name, 
            frame=frame)
            screenshot_path = screenshots_dir_path + str(frame)
            screenshot_path += "\\"
            screenshot_path_copy_1 = screenshot_path
            display_var_dict = self.parse_display_variables_to_dictionary(fo_vars)
            display_group = self.create_display_group()
            session.viewports['Viewport: 1'].odbDisplay.setValues(visibleDisplayGroups=(display_group,     ))
            session.viewports['Viewport: 1'].odbDisplay.displayGroupInstances[str(display_group.name)].setValues(
             lockOptions=OFF)  
 
            for key in display_var_dict:
                #display_var_dict[key] = lista refinementow
                screenshot_path = screenshot_path_copy_1
                screenshot_path += key
                screenshot_path += "\\"
                screenshot_path_copy_2 = screenshot_path
                # print "key " + str(key)
                # print "value" + str(display_var_dict[key])

                if type(display_var_dict[key]) == OrderedDict:
                    secondary_display_vars = display_var_dict[key]
                    for var in secondary_display_vars:
                        # print "var: " + str(var)
                        screenshot_path = screenshot_path_copy_2
                        screenshot_path += str(var)
                        screenshot_path += "\\"
                        try:  
                            os.makedirs(screenshot_path)
                        except OSError as error:
                            error
 
                        fo_object = next((x for x in self.field_output_display_vars if (x.var_label == key 
                                and x.refinement[1]==str(var))), None) 
                        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
                                variableLabel=fo_object.var_label, outputPosition=fo_object.output_position,refinement=fo_object.refinement, )
                        if secondary_display_vars[var] != [None]:
                            self.set_contour_plot_limits(secondary_display_vars[var][0], secondary_display_vars[var][1])
                        
                    
                        for view in views_list: 
                            screenshot_name = screenshot_path + view
                            session.viewports['Viewport: 1'].view.setValues(session.views[str(view)])
                            session.printToFile(fileName=str(screenshot_name), format=PNG, canvasObjects=((session.viewports['Viewport: 1'], )))
                            screenshot_name += '.png'
                            self.pdf_report.image(screenshot_name, w=185,h=80)
                            self.pdf_report.multi_cell(h=5.0,w=0, align='C',txt= str(fo_object.var_label)+": "+str(fo_object.refinement[1])+", view: "+ str(view))
                        
                else:
                    screenshot_path = screenshot_path_copy_1
                    screenshot_path += key
                    screenshot_path += "\\" 
                    try:
                        os.makedirs(screenshot_path)
                    except OSError as error:
                        error
                    fo_object = next((x for x in self.field_output_display_vars if (x.var_label == key 
                                and x.refinement==None)), None)
                    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
                    variableLabel=fo_object.var_label, outputPosition=fo_object.output_position, )
                    if display_var_dict[key] != [None]:
                        self.set_contour_plot_limits(display_var_dict[key][0], display_var_dict[key][1])



                    for view in views_list:
                            screenshot_name = screenshot_path +view
                            session.viewports['Viewport: 1'].view.setValues(session.views[str(view)])
                            session.printToFile(fileName=str(screenshot_name), format=PNG, canvasObjects=((session.viewports['Viewport: 1'], )))
                            screenshot_name += '.png'
                            self.pdf_report.image(screenshot_name, w=185,h=80)
                            self.pdf_report.multi_cell(h=5.0,w=0, align='C',txt= str(fo_object.var_label)+", view: "+ str(view))
                    screenshot_path = screenshot_path_copy_1
    
    def take_geometry_screenshot(self,odb_object,folder_path,folder_name):
        session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
        visibleEdges=FEATURE)
        session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(triad=OFF, 
        legend=OFF, title=OFF, state=OFF, annotations=OFF, compass=OFF, legendBox=OFF, legendNumberFormat=FIXED)
        session.graphicsOptions.setValues(backgroundStyle=SOLID, 
        backgroundColor='#FFFFFF')
        session.viewports['Viewport: 1'].setValues(displayedObject=odb_object)
        # session.mdbData.summary()
        # session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
        # CONTOURS_ON_DEF, ))

        folder_path += "\\"
        folder_path += folder_name 
        folder_path += "\\"
        try:
            os.makedirs(folder_path)
        except OSError as error:
            error
        screenshot_name = folder_path + "geometry"

        session.printToFile(fileName=str(screenshot_name), format=PNG, canvasObjects=((session.viewports['Viewport: 1'], )))
        screenshot_name += '.png'
        self.pdf_report.image(screenshot_name, w=185,h=80)


    def get_mesh_properties(self, odb_object): #todo zwrocic, zapisac, nie prinotwac wszystkiego ?? 
        assembly = odb_object.rootAssembly

        # For each instance in the assembly.

        numNodes = numElements = 0
        mesh_properties_array = []

        for name, instance in assembly.instances.items():
            mesh_dict = {}
            mesh_dict["instance name"] = name
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Instance: "+ str(name))
            n = len(instance.nodes)
            print 'Number of nodes of instance %s: %d' % (name, n)
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Number of nodes: "+ str(n))
            mesh_dict["number of nodes"] = n
            numNodes = numNodes + n

            n = len(instance.elements)
            print 'Number of elements of instance ', name, ': ', n
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Number of all elements: "+ str(n))
            mesh_dict["number of elements"] = n
            numElements = numElements + n

            # print 'ELEMENT CONNECTIVITY'
            # print ' Number  Type    Connectivity'
            element_types=[]
            for element in instance.elements:
                # print '%5d %8s' % (element.label, element.type), # zliczyc np 2137 elementu typu r2d2 itd. 
                element_types.append(element.type)
                # for nodeNum in element.connectivity:
                    # print '%4d' % nodeNum
            element_types_dict = {element:element_types.count(element) for element in element_types}
            mesh_dict["element_types"]=element_types_dict
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Element types:")
            for key in element_types_dict:
                self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt=str(key)+": "+str(element_types_dict[key]))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")

            mesh_properties_array.append(mesh_dict)
            print "Element types" + str(element_types_dict)
        print 'Number of instances: ', len(assembly.instances)
        print 'Total number of elements: ', numElements
        print 'Total number of nodes: ', numNodes
        summary = {}
        summary["Number of istances"]=len(assembly.instances)
        summary["Total number of elements"]=numElements
        summary["Total number of nodes"]=numNodes
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="")
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Mesh summary ")
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Number of istances: "+str(summary["Number of istances"]))
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Total number of elements: "+str(summary["Total number of elements"]))
        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Total number of nodes: "+str(summary["Total number of nodes"]))
        # self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Mesh properties array: "+str(mesh_properties_array))


        props = (mesh_properties_array,summary) 
        print " mesh summary: "+str(props)
        return props

    '''
        TODO:
        - model name 
        - boundary conditions - nwm czy sie da z odb 
        - assembly data (what parts and how many instances) - add screenshot??? 
        - interactions - nwm czy sie da z odb
        - materials DONE sort of
        - step information
        https://stackoverflow.com/questions/66232369/how-to-know-a-material-name-of-a-pid-in-abaqus-odb-filenot-mdb-file-using-pyth
        
        '''
    def get_assembly_information(self, odb_object,folder_path,folder_name):
        '''
                leaf = dgo.Leaf(leafType=DEFAULT_MODEL)
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.add(leaf=leaf)
    leaf = dgo.LeafFromPartInstance(partInstanceName=("BASIS-1", ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.intersect(leaf=leaf)
    leaf = dgo.Leaf(leafType=DEFAULT_MODEL)
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.add(leaf=leaf)
    leaf = dgo.LeafFromPartInstance(partInstanceName=("BERKOVICH_200NM-1", ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.intersect(leaf=leaf)
    leaf = dgo.Leaf(leafType=DEFAULT_MODEL)
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.add(leaf=leaf)
    leaf = dgo.LeafFromPartInstance(partInstanceName=("SPECIMEN-1", ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.intersect(leaf=leaf)
    leaf = dgo.Leaf(leafType=DEFAULT_MODEL)
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.add(leaf=leaf)
        
        '''

        self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Instances: ")
       
        # sections = odb_object.sections
        # cell_location = 40
        instances = odb_object.rootAssembly.instances
        session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
        visibleEdges=FEATURE)
        session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(triad=OFF, 
        legend=OFF, title=OFF, state=OFF, annotations=OFF, compass=OFF, legendBox=OFF, legendNumberFormat=FIXED)
        session.graphicsOptions.setValues(backgroundStyle=SOLID, 
        backgroundColor='#FFFFFF')

        for name,instance in instances.items():
            leaf = dgo.LeafFromPartInstance(partInstanceName=(str(name), ))
            session.viewports['Viewport: 1'].odbDisplay.displayGroup.intersect(leaf=leaf)
            

            # session.mdbData.summary()
            # session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
            # CONTOURS_ON_DEF, ))

            folder_path += "\\"
            folder_path += folder_name 
            folder_path += "\\"
            try:
                os.makedirs(folder_path)
            except OSError as error:
                error
            screenshot_name = folder_path + str(name)

            session.printToFile(fileName=str(screenshot_name), format=PNG, canvasObjects=((session.viewports['Viewport: 1'], )))
            screenshot_name += '.png'
            self.pdf_report.image(screenshot_name, w=185,h=80)
            self.pdf_report.multi_cell(h=5.0,w=0, align='C',txt=str(name))

            leaf = dgo.Leaf(leafType=DEFAULT_MODEL)
            session.viewports['Viewport: 1'].odbDisplay.displayGroup.add(leaf=leaf)
            #todo add screenshots (iso)


    def get_material_properties(self, odb_object):
        
        # sections = odb_object.sections # to zwraca dictionary z nazwami sekcji 
        # print "sections " + str(sections)
        # print "element sets " + str(odb_object.rootAssembly.instances['EX3-1'].elementSets)
        # my_elset = odb_object.rootAssembly.instances['EX3-1'].elementSets['M1']
        # element_from_set = my_elset.elements[0] # list with mesh element object, e.g. first
        # sec_category = element_from_set[0].sectionCategory.name[0]
        # print "section category" + sec_category
        instances = odb_object.rootAssembly.instances
       
        sections = odb_object.sections
        # cell_location = 40

        for name,instance in instances.items(): #tu to chyba lepsza by byla tabela ale nwm 
            # print "instance name:"+str(name)
            # self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt=str(name))
            # cell_location +=10
            section_assignments = odb_object.rootAssembly.instances[name].sectionAssignments
            materials = []

            # self.pdf_report.set_font('Arial', 'B', 14)    
            # self.pdf_report.multi_cell(h=5.0,w=0, txt="Section assignments:")
            # cell_location +=10

            for section_assignment in section_assignments:
                self.pdf_report.multi_cell(h=5.0,w=0, txt=str(section_assignment.sectionName))
                # cell_location +=10
                # print " section assignment: "+str(section_assignment)
                section_name = section_assignment.sectionName
                section = sections[section_name]

                # self.pdf_report.set_font('Arial', 'B', 12)
                self.pdf_report.multi_cell(h=5.0,w=0, txt="Materials: ")
                # cell_location +=10

                # self.pdf_report.set_font('Arial', '', 12)
                self.pdf_report.multi_cell(h=5.0,w=0, txt=str(materials))
                # cell_location +=10
                
                # materials.append(section.material)
                print "material name:"+str(materials) # todo wyciagnac wszystkie pola i lapac wyjatki jak ktoregos nie ma  
                # print "material density table; "+ str(odb_object.materials[section.material].density.table) # inne tabele tez???
                # # print "material elastic table; "+ str(odb_object.materials[section.material].depvar) # inne tabele tez???
                # print "material elastic table; "+ str(odb_object.materials[section.material].elastic.table) # inne tabele tez???
                # print "material plastic obj as trimmed string: "+ str(odb_object.materials[section.material].plastic)[1:-1]
                # s = str(odb_object.materials[section.material].plastic)[1:-1]
                # json_acceptable_string = s.replace("'", "\"")
                # print "after quote replacement: " + json_acceptable_string
                # d = json.loads(s)
                # for m in odb_object.materials[section.material].values():
                # self.pdf_report.set_font('Arial', 'B', 12)
                # self.pdf_report.cell(40, cell_location,"Material properties ",ln=2)
                # cell_location +=10
                # self.pdf_report.set_font('Arial', '', 12)

                #     print "m: " + str(m)
                print "#################### material properties #####################"
                self.pdf_report.multi_cell(h=5.0,w=0, txt="Material properties: ")
                
                try:
                    print "acoustic medium: "+ str(odb_object.materials[section.material].acousticMedium)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Acoustic medium: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Bulk table:"+ str(odb_object.materials[section.material].acousticMedium.bulkTable))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Volumetric table:"+ str(odb_object.materials[section.material].acousticMedium.volumetricTable))
                    
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "brittle cracking: "+ str(odb_object.materials[section.material].brittleCracking)
                    # self.pdf_report.cell(40, cell_location,"brittle cracking: "+ str(odb_object.materials[section.material].brittleCracking))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Brittle cracking: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].brittleCracking.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].brittleCracking.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].brittleCracking.type))

                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "cap plasticity: "+ str(odb_object.materials[section.material].capPlasticity)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Cap plasticity: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].capPlasticity.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].capPlasticity.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "cast iron plasticity: "+ str(odb_object.materials[section.material].castIronPlasticity)
                    # self.pdf_report.cell(40, cell_location,"Cast iron plasticity: "+ str(odb_object.materials[section.material].castIronPlasticity))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Cast iron plasticity: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].castIronPlasticity.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].castIronPlasticity.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "clay plasticity: "+ str(odb_object.materials[section.material].clayPlasticity)
                    # self.pdf_report.cell(40, cell_location,"clay plasticity: "+ str(odb_object.materials[section.material].clayPlasticity))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Clay plasticity: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].clayPlasticity.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].clayPlasticity.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Hardening:"+ str(odb_object.materials[section.material].clayPlasticity.hardening))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "concrete: "+ str(odb_object.materials[section.material].concrete)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Concrete: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].concrete.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].concrete.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "concrete damaged plasticity: "+ str(odb_object.materials[section.material].concreteDamagedPlasticity)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Concrete: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].concreteDamagedPlasticity.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].concreteDamagedPlasticity.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "conductivity: "+ str(odb_object.materials[section.material].conductivity)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Conductivity: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].conductivity.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].conductivity.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].conductivity.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "creep: "+ str(odb_object.materials[section.material].creep)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Creep: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].creep.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].creep.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Strain hardenng law:"+ str(odb_object.materials[section.material].creep.law))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "crushable foam: "+ str(odb_object.materials[section.material].crushableFoam)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Crushable foam: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].crushableFoam.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].crushableFoam.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Hardening:"+ str(odb_object.materials[section.material].crushableFoam.hardening))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "ductile damage initiation: "+ str(odb_object.materials[section.material].ductileDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Ductile damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].ductileDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].ductileDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].ductileDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "fld damage initiation: "+ str(odb_object.materials[section.material].fldDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Fld damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].fldDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].fldDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].fldDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "flsd damage initiation: "+ str(odb_object.materials[section.material].flsdDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Flsd damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].flsdDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].flsdDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].flsdDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "johnson cook damage initiation: "+ str(odb_object.materials[section.material].johnsonCookDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Johnson Cook damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].johnsonCookDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].johnsonCookDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].johnsonCookDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "maxe damage initiation: "+ str(odb_object.materials[section.material].maxeDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Max e damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].maxeDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].maxeDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].maxeDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "maxs damage initiation: "+ str(odb_object.materials[section.material].maxsDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Max s damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].maxsDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].maxsDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].maxsDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "maxpe damage initiation: "+ str(odb_object.materials[section.material].maxpeDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Max pe damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].maxpeDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].maxpeDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].maxpeDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "maxps damage initiation: "+ str(odb_object.materials[section.material].maxpsDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Max ps damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].maxpsDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].maxpsDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].maxpsDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "mk damage initiation: "+ str(odb_object.materials[section.material].mkDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Mk damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].mkDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].mkDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].mkDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "msfld damage initiation: "+ str(odb_object.materials[section.material].msfldDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Msfld damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].msfldDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].msfldDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].msfldDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "quade damage initiation: "+ str(odb_object.materials[section.material].quadeDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Quade damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].quadeDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].quadeDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].quadeDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "quads damage initiation: "+ str(odb_object.materials[section.material].quadsDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Quads damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].quadsDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].quadsDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].quadsDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "shear damage initiation: "+ str(odb_object.materials[section.material].shearDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Shear damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].shearDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].shearDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].shearDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "hashin damage initiation: "+ str(odb_object.materials[section.material].hashinDamageInitiation)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Hashin damage initiation: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].hashinDamageInitiation.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].hashinDamageInitiation.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].hashinDamageInitiation.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "damping: "+ str(odb_object.materials[section.material].damping)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Damping: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Alpha:"+ str(odb_object.materials[section.material].damping.alpha))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Beta:"+ str(odb_object.materials[section.material].damping.beta))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Composite:"+ str(odb_object.materials[section.material].damping.composite))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Structural:"+ str(odb_object.materials[section.material].damping.structural))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "deformation plasticity: "+ str(odb_object.materials[section.material].deformationPlasticity)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Deformation plasticity: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].deformationPlasticity.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].deformationPlasticity.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "density: "+ str(odb_object.materials[section.material].density)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Density: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].density.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].density.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Distribution type:"+ str(odb_object.materials[section.material].density.distributionType))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Field name:"+ str(odb_object.materials[section.material].density.fieldName))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "depvar: "+ str(odb_object.materials[section.material].depvar)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Depvar: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Delete var:"+ str(odb_object.materials[section.material].depvar.deleteVar))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Number of solution-dependent state variables required at each integration point:"+ str(odb_object.materials[section.material].depvar.n))
                    
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "dielectric: "+ str(odb_object.materials[section.material].dielectric)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Dielectric: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].dielectric.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].dielectric.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Frequency dependency:"+ str(odb_object.materials[section.material].dielectric.frequencyDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].dielectric.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "diffusivity: "+ str(odb_object.materials[section.material].diffusivity)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Diffusivity: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].diffusivity.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].diffusivity.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Diffusion law:"+ str(odb_object.materials[section.material].diffusivity.law))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].dielectric.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "drucker prager: "+ str(odb_object.materials[section.material].druckerPrager)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Drucker-Prager: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].druckerPrager.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].druckerPrager.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Yield criterion:"+ str(odb_object.materials[section.material].druckerPrager.shearCriterion))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Flow potential eccentricity:"+ str(odb_object.materials[section.material].druckerPrager.eccentricity))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "elastic: "+ str(odb_object.materials[section.material].elastic)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Elastic: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].elastic.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].elastic.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Moduli:"+ str(odb_object.materials[section.material].elastic.moduli))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Compressive stress:"+ str(odb_object.materials[section.material].elastic.noCompression))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Tensile stress:"+ str(odb_object.materials[section.material].elastic.noTension))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "electrical conductivity: "+ str(odb_object.materials[section.material].electricalConductivity)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Electrical conductivity: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].electricalConductivity.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].electricalConductivity.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Frequency dependency:"+ str(odb_object.materials[section.material].electricalConductivity.frequencyDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].electricalConductivity.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "eos: "+ str(odb_object.materials[section.material].eos)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Equation of state model: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].eos.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].eos.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].eos.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Detonation energy:"+ str(odb_object.materials[section.material].eos.detonationEnergy))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Solid table:"+ str(odb_object.materials[section.material].eos.solidTable))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Gas specific table:"+ str(odb_object.materials[section.material].eos.gasSpecificTable))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Reaction table:"+ str(odb_object.materials[section.material].eos.reactionTable))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Gas table:"+ str(odb_object.materials[section.material].eos.gasTable))
                    
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "expansion: "+ str(odb_object.materials[section.material].expansion)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Expansion: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].expansion.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].expansion.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].expansion.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="User subroutine:"+ str(odb_object.materials[section.material].expansion.userSubroutine))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Zero:"+ str(odb_object.materials[section.material].expansion.zero))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "fluidLeakoff: "+ str(odb_object.materials[section.material].fluidLeakoff)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Fluid leakoff: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].fluidLeakoff.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].fluidLeakoff.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].fluidLeakoff.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "gapFlow: "+ str(odb_object.materials[section.material].gapFlow)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Gap flow: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].gapFlow.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].gapFlow.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].gapFlow.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Kmax:"+ str(odb_object.materials[section.material].gapFlow.kmax))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "gasket thickness behavior: "+ str(odb_object.materials[section.material].gasketThicknessBehavior)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Gasket thickness behavior: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].gasketThicknessBehavior.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].gasketThicknessBehavior.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].gasketThicknessBehavior.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Tensile stiffness factor:"+ str(odb_object.materials[section.material].gasketThicknessBehavior.tensileStiffnessFactor))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "gasket transverse shear elastic: "+ str(odb_object.materials[section.material].gasketTransverseShearElastic)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Gasket transverse shear elastic: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].gasketTransverseShearElastic.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Variable units:"+ str(odb_object.materials[section.material].gasketTransverseShearElastic.variableUnits))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].gasketTransverseShearElastic.temperatureDependency))
                    
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "gasket membrane elastic: "+ str(odb_object.materials[section.material].gasketMembraneElastic)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Gasket membrane elastic: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].gasketMembraneElastic.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].gasketMembraneElastic.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "gel: "+ str(odb_object.materials[section.material].gel)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Gel: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].gel.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "heat generation: "+ str(odb_object.materials[section.material].heatGeneration)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="heat generation: "+ str(odb_object.materials[section.material].heatGeneration))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "hyperelastic: "+ str(odb_object.materials[section.material].hyperelastic)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Hyperelastic: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].hyperelastic.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].hyperelastic.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].hyperelastic.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Compressible:"+ str(odb_object.materials[section.material].hyperelastic.compressible))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Poisson ratio:"+ str(odb_object.materials[section.material].hyperelastic.poissonRatio))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Material type:"+ str(odb_object.materials[section.material].hyperelastic.materialType))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "hyperfoam: "+ str(odb_object.materials[section.material].hyperfoam)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Hyperfoam: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].hyperfoam.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].hyperfoam.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].hyperfoam.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Poisson ratio:"+ str(odb_object.materials[section.material].hyperfoam.poisson))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "hypoelastic: "+ str(odb_object.materials[section.material].hypoelastic)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Hypoelastic: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].hypoelastic.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "inelasticHeatFraction: "+ str(odb_object.materials[section.material].inelasticHeatFraction)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Inelastic Heat Fraction:"+ str(odb_object.materials[section.material].inelasticHeatFraction.fraction))
                    
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "jouleHeatFraction: "+ str(odb_object.materials[section.material].jouleHeatFraction)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Joule Heat Fraction:"+ str(odb_object.materials[section.material].jouleHeatFraction.fraction))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "latentHeat: "+ str(odb_object.materials[section.material].latentHeat)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Latent heat: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].latentHeat.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "lowDensityFoam: "+ str(odb_object.materials[section.material].lowDensityFoam)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Low density foam: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Element Removal:"+ str(odb_object.materials[section.material].lowDensityFoam.elementRemoval))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Max allowable principal stress:"+ str(odb_object.materials[section.material].lowDensityFoam.maxAllowablePrincipalStress))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Extrapolate stress strain curve:"+ str(odb_object.materials[section.material].lowDensityFoam.extrapolateStressStrainCurve))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Strain rate type:"+ str(odb_object.materials[section.material].lowDensityFoam.strainRateType))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="mu0:"+ str(odb_object.materials[section.material].lowDensityFoam.mu0))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="mu1:"+ str(odb_object.materials[section.material].lowDensityFoam.mu1))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Alpha:"+ str(odb_object.materials[section.material].lowDensityFoam.alpha))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "magneticPermeability: "+ str(odb_object.materials[section.material].magneticPermeability)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Magnetic permeability: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table 1:"+ str(odb_object.materials[section.material].magneticPermeability.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table 2:"+ str(odb_object.materials[section.material].magneticPermeability.table2))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table 3:"+ str(odb_object.materials[section.material].magneticPermeability.table3))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "mohrCoulombPlasticity: "+ str(odb_object.materials[section.material].mohrCoulombPlasticity)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Mohr coulomb plasticity: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].mohrCoulombPlasticity.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].mohrCoulombPlasticity.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Deviatoric eccentricity:"+ str(odb_object.materials[section.material].mohrCoulombPlasticity.deviatoricEccentricity))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Meridional eccentricity:"+ str(odb_object.materials[section.material].mohrCoulombPlasticity.meridionalEccentricity))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "moistureSwelling: "+ str(odb_object.materials[section.material].moistureSwelling)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Moisture swelling: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].moistureSwelling.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "mullinsEffect: "+ str(odb_object.materials[section.material].mullinsEffect)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Moisture swelling: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].moistureSwelling.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].mullinsEffect.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Definition:"+ str(odb_object.materials[section.material].mullinsEffect.definition))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "permeability: "+ str(odb_object.materials[section.material].permeability)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Moisture swelling: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].permeability.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Specific weight:"+ str(odb_object.materials[section.material].permeability.specificWeight))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Inertial drag coefficient:"+ str(odb_object.materials[section.material].permeability.inertialDragCoefficient))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].permeability.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].permeability.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "piezoelectric: "+ str(odb_object.materials[section.material].piezoelectric)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Piezoelectric: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].piezoelectric.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type:"+ str(odb_object.materials[section.material].piezoelectric.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].piezoelectric.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "plastic: "+ str(odb_object.materials[section.material].plastic)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Plastic: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].plastic.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type of hardening:"+ str(odb_object.materials[section.material].plastic.hardening))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Rate:"+ str(odb_object.materials[section.material].plastic.rate))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Data type:"+ str(odb_object.materials[section.material].plastic.dataType))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Strain range dependency:"+ str(odb_object.materials[section.material].plastic.strainRangeDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Number of backstresses:"+ str(odb_object.materials[section.material].plastic.numBackstresses))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].plastic.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "poreFluidExpansion: "+ str(odb_object.materials[section.material].poreFluidExpansion)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Pore fluid expansion: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].poreFluidExpansion.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type of hardening:"+ str(odb_object.materials[section.material].poreFluidExpansion.zero))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].poreFluidExpansionlastic.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "porousBulkModuli: "+ str(odb_object.materials[section.material].porousBulkModuli)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Porous bulk moduli: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].porousBulkModuli.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].porousBulkModuli.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "porousElastic: "+ str(odb_object.materials[section.material].porousElastic)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Porous elastic: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].porousElastic.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Shear definition form:"+ str(odb_object.materials[section.material].porousElastic.shear))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].porousElastic.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "porousMetalPlasticity: "+ str(odb_object.materials[section.material].porousMetalPlasticity)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Porous metal plasticity: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].porousMetalPlasticity.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Relative density:"+ str(odb_object.materials[section.material].porousMetalPlasticity.relativeDensity))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].porousMetalPlasticity.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "regularization: "+ str(odb_object.materials[section.material].regularization)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Regularization: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Rtol:"+ str(odb_object.materials[section.material].regularization.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Strain rate regularization:"+ str(odb_object.materials[section.material].regularization.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "solubility: "+ str(odb_object.materials[section.material].solubility)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Solubility: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table:"+ str(odb_object.materials[section.material].solubility.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency:"+ str(odb_object.materials[section.material].solubility.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "sorption: "+ str(odb_object.materials[section.material].sorption)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Sorption: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Absorption table: "+ str(odb_object.materials[section.material].sorption.absorptionTable))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Law absorption: "+ str(odb_object.materials[section.material].sorption.lawAbsorption))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Exsorption: "+ str(odb_object.materials[section.material].sorption.exsorption))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Law exsorption: "+ str(odb_object.materials[section.material].sorption.lawExsorption))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Scanning: "+ str(odb_object.materials[section.material].sorption.scanning))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Exsorption table: "+ str(odb_object.materials[section.material].sorption.exsorptionTable))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                    # cell_location +=10
                except AttributeError:
                    pass

                try:
                    print "swelling: "+ str(odb_object.materials[section.material].swelling)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Swelling: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Absorption table: "+ str(odb_object.materials[section.material].swelling.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Swelling behavior :"+ str(odb_object.materials[section.material].swelling.law))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency: "+ str(odb_object.materials[section.material].swelling.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                    
                    # cell_location +=10
                except AttributeError:
                    pass

                try:
                    print "userDefinedField: "+ str(odb_object.materials[section.material].userDefinedField)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="User defined field: "+ str(odb_object.materials[section.material].userDefinedField))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                    # cell_location +=10
                except AttributeError:
                    pass

                try:
                    print "userMaterial: "+ str(odb_object.materials[section.material].userMaterial)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="User material: ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type: "+ str(odb_object.materials[section.material].type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Unsymm: "+ str(odb_object.materials[section.material].unsymm))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Mechanical constants: "+ str(odb_object.materials[section.material].mechanicalConstants))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Thermal constants: "+ str(odb_object.materials[section.material].thermalConstants))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                    # cell_location +=10
                except AttributeError:
                    pass

                try:
                    print "userOutputVariables: "+ str(odb_object.materials[section.material].userOutputVariables)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="User output variables : ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Number of user-defined variables: "+ str(odb_object.materials[section.material].userOutputVariables.n))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                    # cell_location +=10
                except AttributeError:
                    pass

                try:
                    print "viscoelastic: "+ str(odb_object.materials[section.material].viscoelastic)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Viscoelastic : ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table: "+ str(odb_object.materials[section.material].viscoelastic.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Frequency: "+ str(odb_object.materials[section.material].viscoelastic.frequency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type: "+ str(odb_object.materials[section.material].viscoelastic.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Preload: "+ str(odb_object.materials[section.material].viscoelastic.preload))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")

                    # cell_location +=10
                except AttributeError:
                    pass

                try:
                    print "viscosity: "+ str(odb_object.materials[section.material].viscosity)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Viscosity : ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table: "+ str(odb_object.materials[section.material].viscosity.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Type: "+ str(odb_object.materials[section.material].viscosity.type))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Temperature dependency: "+ str(odb_object.materials[section.material].viscosity.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                except AttributeError:
                    pass

                try:
                    print "Viscous: "+ str(odb_object.materials[section.material].viscous)
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Viscoelastic : ")
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Table: "+ str(odb_object.materials[section.material].viscous.table))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Creep law: "+ str(odb_object.materials[section.material].viscous.law))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="Ttemperature dependency: "+ str(odb_object.materials[section.material].viscous.temperatureDependency))
                    self.pdf_report.multi_cell(h=5.0,w=0, txt="")
                    # cell_location +=10
                except AttributeError:
                    pass

    def get_steps_data(self, odb_object):
        steps = odb_object.steps.values()
        for step in steps:
            print "step: " + str(step)
            print "Step name: "+str(step.name)
            print "Step description: "+str(step.description)
            print "Step domain: "+str(step.domain)
            print "Step time period: "+str(step.timePeriod)
            print "Prevoius step name: "+str(step.previousStepName)
            print "geometric nonlinearity: "+str(step.nlgeom)
            print "mass: "+str(step.mass)
            print "acoustic mass: "+str(step.acousticMass)
            print "Frames: "+str(len(step.frames))
            print "history regions: "+ str(step.historyRegions)
            print "load Cases: "+ str(step.loadCases)
            print "mass center: "+ str(step.massCenter)
            print "inertia about center: "+ str(step.inertiaAboutCenter)
            print "inertia about origin: "+ str(step.inertiaAboutOrigin)
            print "acoustic mass center: "+ str(step.acousticMassCenter)
            # self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Number of istances: "+str(summary["Number of istances"]))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Step name: " + str(step.name))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Description: "+str(step.description))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Step domain: "+str(step.domain))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Time period: "+str(step.timePeriod))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Previous step name: "+str(step.previousStepName))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Geometric nonlinearity: "+str(step.nlgeom))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Mass: "+str(step.mass))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Acoustic mass: "+str(step.acousticMass))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Frames: "+str(len(step.frames)))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="History regions:"+ str(step.historyRegions))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Load cases: "+ str(step.loadCases))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Mass center: "+ str(step.massCenter))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Inertia about center: "+ str(step.inertiaAboutCenter))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Inertia about origin: "+ str(step.inertiaAboutOrigin))
            self.pdf_report.multi_cell(h=5.0,w=0, align='L',txt="Acoustic mass center: "+ str(step.acousticMassCenter))
           

    

    def create_display_group(self):
        data = self.user_data

        item_type = data["Item type to display"] 
        items_to_display =[str(p) for p in data["Names of items to display"].split(",")]
        
        session.linkedViewportCommands.setValues(_highlightLinkedViewports=True)
        if item_type.lower() == "parts":
            leaf = dgo.LeafFromPartInstance(partInstanceName=(items_to_display))
        elif item_type.lower() == "elements":
            leaf = dgo.LeafFromElementSets(elementSets=(items_to_display))
        elif item_type.lower() == "nodes": #not supported in contour plot mode?
            leaf = dgo.LeafFromNodeSets(nodeSets=(items_to_display))
        elif item_type.lower() == "surfaces":
            leaf = dgo.LeafFromSurfaceSets(surfaceSets=(items_to_display))
        else:
            print "nie wolno" # todo wywal blad 
        session.viewports['Viewport: 1'].odbDisplay.displayGroup.intersect(leaf=leaf)
        dg = session.viewports['Viewport: 1'].odbDisplay.displayGroup
        dg = session.DisplayGroup(name='dg1', objectToCopy=dg)
        return dg

    def set_contour_plot_limits(self,min,max):
        session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(maxAutoCompute=OFF, minAutoCompute=OFF) 
        session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(maxAutoCompute=OFF, maxValue=max, 
                                                                             minAutoCompute=OFF, minValue=min)

    def parse_contour_plot_limits(self):
        # returns a 2d array eg [[21,37], [21,37],[21,37], ['']]
        data = self.user_data
        contour_plot_limits = [[float(y) if y != "" else None for y in x.split(",")] \
                               for x in data["Contour plot limits"].split(";")] 
        return contour_plot_limits
               
    def removeRedundant(self, listTmp):
        listTmp.sort()
        listTmp2 = []
        prev = -1
        for i in range(len(listTmp)):
            if prev != listTmp[i]:
                listTmp2.append(listTmp[i])
                prev = listTmp[i]
        return listTmp2

    #PARSERS   
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

    def parse_display_variables_to_dictionary(self, display_variable_string):
        # "S:S11,Mises;TEMP;PEEQ"
        display_variable_dict = OrderedDict()
        contour_plot_limits = self.parse_contour_plot_limits()
        chunk_sizes = []
        # todo  
        temp1 = display_variable_string.split(";")
        for t in temp1:
            #przykladowo t = "S:S11,Mises" albo TEMP
            dict_key = None
            dict_values = []
            if ":" in t:
                dict_key = t.split(":")[0]
                dict_values = t.split(":")[1].split(",")  
                chunk_sizes.append(len(dict_values))
            else:
                dict_key = t 
                chunk_sizes.append(1) 
            display_variable_dict[dict_key] = dict_values

        # podzielenie tablicy z limitami na kawalki wielkosci tablic z secondary disp variables  
        i = 0
        contour_plot_limits_split = []
        for cs in chunk_sizes:
            contour_plot_limits_split.append(contour_plot_limits[i:i+cs])
            i +=cs
        
        # iteracja po wczesniej stworzonym dictionary zeby dodac plot limits
        # print "dict before: "+ str(display_variable_dict) 
        # print "podzielona tabica: "+ str(contour_plot_limits_split)
        for k_index, key in enumerate(display_variable_dict):
            if display_variable_dict[key]!=[]:
                plot_limits = OrderedDict()
                disp_var_array = display_variable_dict[key]
                for v_index, var in enumerate(disp_var_array):
                    # print "disp var arrray: " + str(disp_var_array)
                    # print "k index: " + str(k_index)
                    # print "v index: " + str(v_index)

                    plot_limits[var]=contour_plot_limits_split[k_index][v_index]
            else:
                plot_limits =  contour_plot_limits_split[k_index][0]
            display_variable_dict[key] = plot_limits
        # print "display variable dict: "+ str(display_variable_dict)
        return display_variable_dict

    