import os

def generate_project_structure(root_folder):
    project_structure = f"{root_folder}/\n"

    for folder_name, subfolders, filenames in os.walk(root_folder):
        depth = folder_name[len(root_folder):].count(os.sep)
        indent = " " * 4 * depth
        folder_structure = f"{indent}├── {os.path.basename(folder_name)}/\n"

        for filename in filenames:
            file_structure = f"{indent}│   ├── {filename}\n"
            folder_structure += file_structure

        # Aggiungi una linea orizzontale sotto il nome della cartella usando asterischi
        folder_structure += f"{indent}├── \n"

        project_structure += folder_structure

    return project_structure

# Cambia il percorso della cartella radice con il percorso del tuo progetto

root_folder_path = "C:\\Users\\soler\\Desktop\\TestAppCompleta\\user_management_service"
project_name = str(root_folder_path.split('\\')[-1])

# Ottieni il percorso della directory dello script corrente
script_directory = os.path.dirname(os.path.abspath(__file__))
# Combina il percorso completo del file di output
output_path = os.path.join(script_directory, f"struttura_{project_name.lower()}.md")

# Salva il risultato su un file con codifica UTF-8
with open(output_path, "w", encoding="utf-8") as file:
    file.write(generate_project_structure(root_folder_path))
    print("creato: " + project_name)
