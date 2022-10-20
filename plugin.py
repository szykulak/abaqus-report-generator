import ODBExtractor
from abaqus import session
from odbAccess import*

def extractor_function(odb_dir_path, step_name, frames, results_dir_path, results_dir_name, include_mesh_data, export_to_csv, take_model_screenshots,
                       field_output_names, set_name, instance_name, instance_set_name, field_output, value, minimum, maximum,
                       view_names, fo_disp_vars, item_type, item_names, contour_plot_limits, mesh_on):
    '''
     TODO:
     - jakies krotkie readme z objasnieniem pol 
     - testowanie w roznych konfiguracjach (zeby eksport dziaial, moze modele prostowania zrobic XD)
     - teoria
     '''

    user_data = {
        "ODB directory path": odb_dir_path,
        "Step name": step_name,
        "Frames": frames,
        "Field output names": field_output_names,
        "Set name": set_name,
        "Instance name": instance_name,
        "Instance set name": instance_set_name, 
        "Folder path": results_dir_path,
        "Folder name": results_dir_name,
        "Field output": field_output,
        "Value": value,
        "Minimum": minimum,
        "Maximum": maximum,
        "Views": view_names,
        "Field output display variables": fo_disp_vars,
        "Contour plot limits": contour_plot_limits,
        "Item type to display":item_type,
        "Names of items to display":item_names,
        "Include mesh data": include_mesh_data,
        "Export to csv": export_to_csv,
        "Take model screenshots": take_model_screenshots,
        "Mesh on": mesh_on

    }
    # TODO include_mesh_data wziac z checkboxa ??? albo w ogole gdzie to przekazywac 
    # TODO zrobic wywolywanie metod opcjonalnie w zaleznosci co uzytkownik wybierze
    print("testuje cos") 
    odb_extr = ODBExtractor.ODBExtractor(user_data)
    odb_extr.run_extractor()

