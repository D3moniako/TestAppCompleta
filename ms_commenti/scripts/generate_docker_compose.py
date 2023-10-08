import os
import shutil
from scripts.constants import Constants

def generate_docker_compose():
    # Percorso del template del Docker Compose generale
    template_docker_compose = Constants.TEMPLATE_DOCKER_COMPOSE

    # Nome del microservizio
    service_name = Constants.SERVICE_NAME

    # Percorso del Docker Compose per il microservizio corrente
    docker_compose_path = os.path.join(Constants.MICROSERVICE_DIR, "docker-compose.yml")

    # Copia il template del Docker Compose generale nel Docker Compose specifico del microservizio
    shutil.copy(template_docker_compose, docker_compose_path)

    # Leggi le costanti dal file e sostituisci i segnaposto nel Docker Compose
    with open(Constants.CONSTANTS_FILE_PATH, "r") as file:
        constants_data = file.read()
        with open(docker_compose_path, "r") as docker_file:
            docker_data = docker_file.read()
            updated_docker_data = docker_data.replace("__DB_CONNECTION_STRING__", constants_data)
            updated_docker_data = updated_docker_data.replace("__JWT_SECRET_KEY__", constants_data)
            updated_docker_data = updated_docker_data.replace("__SERVICE_NAME__", service_name)

    with open(docker_compose_path, "w") as file:
        file.write(updated_docker_data)

    print(f"Docker Compose per {service_name} creato con successo.")

if __name__ == "__main__":
    generate_docker_compose()
