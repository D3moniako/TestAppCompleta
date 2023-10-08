import os
import shutil

def generate_docker_compose(project_root, template_path, microservices_dir):
    # Percorso del template del Docker Compose generale
    template_docker_compose = os.path.join(project_root, template_path)

    # Loop attraverso le cartelle dei microservizi
    for microservice_dir in os.listdir(microservices_dir):
        # Nome del microservizio
        service_name = microservice_dir

        # Percorso del Docker Compose per il microservizio corrente
        docker_compose_path = os.path.join(microservices_dir, microservice_dir, "docker-compose.yml")

        # Copia il template del Docker Compose generale nel Docker Compose specifico del microservizio
        shutil.copy(template_docker_compose, docker_compose_path)

        # Sostituisci il segnaposto del nome del servizio nel Docker Compose specifico
        replace_placeholder(docker_compose_path, "__SERVICE_NAME__", service_name)

        print(f"Creato Docker Compose per {service_name}")

    print("Script completato.")

def replace_placeholder(file_path, placeholder, value):
    with open(file_path, "r") as file:
        data = file.read()
        updated_data = data.replace(placeholder, value)

    with open(file_path, "w") as file:
        file.write(updated_data)

if __name__ == "__main__":
    # Directory principale del progetto
    project_root = os.getcwd()

    # Percorso del template del Docker Compose generale
    template_path = "docker-compose.yml.template"

    # Cartella contenente i microservizi
    microservices_dir = os.path.join(project_root, "microservizi")

    # Genera i file Docker Compose
    generate_docker_compose(project_root, template_path, microservices_dir)
