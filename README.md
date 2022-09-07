# ABAQUS Report Generator
Report Generator is a plugin for ABAQUS that creates simulation reports from .odb files.

## Usage
The UI consists of three tabs: Basics, CSV and Screenshots. In order to create a report you need to fill in desired fields.
Fields in Basics tab are mandatory, the rest is optional, depending on what the report should contain.

Fields explanation:
1. Basics:


    ![image1](C:\Users\asus\Desktop\Screenshot_4.jpg)
    - ODB directory path: an absolute path to the directory with .odb files to create report from. ODBs need to be similar: all of them must contain the same field outputs and steps, parts must have the same names etc. 
    - Step: name of simulation step
    - Frames: numbers of frames separated with a comma, e.g. 98,99,100
    - Path to save results: an absolute path to a directory where results will be saved
    - Results directory name: name of the directory with results that will be created in above directory
    - Include mesh data: check if you want the report to contain mesh parameters (NOT YET IMPLEMENTED)
    - Export to CSV: check if you want to export distributions of specific parameters to .csv files
    - Take model screenshots: check if you want the report to contain screenshots of the model 

    WARNING: If you're using Windows you need to add double slashes to directory paths.

2. CSV Export:

    ![image2](C:\Users\asus\Desktop\Screenshot_9.jpg)
    I:
    - Field output names: Name of field outputs to export separated with a comma
    - Set name: Name of element set to export (if the field is filled in, "Instance name" and "Instance set name" need to be empty and the other way round)
    - Instance name: Name of a specific model (or part) instance 
    - Instance set name: Name of a set which belongs to the instance passed above 
    II:
    Fill in value range for the field output need to be specified
    - Field output: primary field output variable name, e.g. "S"
    - Value: field output value name e.g. "Mises"
    - Minimum: minimum value for the field output
    - Maximum: maximum value for the field output

3. Screenshots:

    ![image2](C:\Users\asus\Desktop\Screenshot_11.jpg)
    - Views: names of views that will be included separated with a comma, possible values: Iso, Front, Back, Top, Bottom, Left, Right and names of custom views, e.g. User-1 (the last one needs to be created manually in ABAQUS first) 
    - Field output display variables: field outputs that will be displayed. It needs to be passed in following format: **FIELD OUTPUT1:REFINEMENT1,REFINEMENT2;FIELDOUTPUT2:REFINEMENT3,REFINEMENT4**, for example:
    RM:RM1;RF:Magnitude;PEEQ;S:Mises,S11
    If field output does not have any refinements then field output name separated with a semicolon is enough
    - Contour plot limits: minimum and maximum field output value that will be shown on the screenshot, passed in following format:
    **MINIMUM,MAXIMUM;MINIMUM,MAXIMUM;;MINIMUM,MAXIMUM;**. The order of minimum-maximum pairs needs to be exactly the same as order of field output display variables, if you want to leave the deafult setting just do not put anything between semicolons
    - Items to display: type of item that will be displayed, possible values: Parts, Elements, Nodes (WARNING: Might throw an error as the implementation requires some adjustments), Sets
    - Names of items to display: names of items (type chosen above) separated with a comma  
    