import os

def generate_project_structure(start_path, depth=0):
    result = ""
    for root, dirs, files in os.walk(start_path):
        current_depth = root[len(start_path) + 1:].count(os.sep)
        if current_depth > depth:
            continue

        indent = "  " * current_depth
        result += f"{indent}- **{os.path.basename(root)}/**\n"

        for file in files:
            result += f"{indent}  - {file}\n"

    return result

project_root = "/path/to/your/project"
structure = generate_project_structure(project_root)

with open("project_structure.md", "w") as file:
    file.write(structure)