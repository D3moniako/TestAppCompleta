import os

def collect_dependencies(root_path):
    dependencies = set()

    for dirpath, _, filenames in os.walk(root_path):
        if "requirements.txt" in filenames:
            with open(os.path.join(dirpath, "requirements.txt")) as f:
                dependencies.update(line.strip() for line in f)

    return dependencies

def generate_requirements_txt(microservice_path, shared_dependencies_path):
    print(f"Microservice Path: {microservice_path}")

    microservices_dependencies = collect_dependencies(microservice_path)
    shared_dependencies = collect_dependencies(shared_dependencies_path)

    common_dependencies = microservices_dependencies.intersection(shared_dependencies)

    with open(os.path.join(microservice_path, "requirements.txt"), "w") as f:
        f.write("\n".join(common_dependencies))

    return common_dependencies  # Aggiunto questo per restituire le dipendenze comuni

def main():
    microservices_path = os.path.abspath("../")
    shared_dependencies_path = os.path.abspath("../shared-dependencies")

    common_dependencies = set()

    for microservice_name in os.listdir(microservices_path):
        if os.path.isdir(os.path.join(microservices_path, microservice_name)):
            microservice_path = os.path.join(microservices_path, microservice_name)
            common_dependencies.update(generate_requirements_txt(microservice_path, shared_dependencies_path))

    # Correggi il percorso della cartella shared-dependencies
    shared_dependencies_path = os.path.abspath(shared_dependencies_path)

    common_dependencies_file_path = os.path.join(shared_dependencies_path, "common_dependencies.txt")

    with open(common_dependencies_file_path, "w") as f:
        f.write("\n".join(common_dependencies))

    print(f"Common Dependencies written to: {common_dependencies_file_path}")

if __name__ == "__main__":
    main()
