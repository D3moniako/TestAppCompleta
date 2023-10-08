import subprocess
import time
import os
# qui metto i microservizi da cui creare immagini e poi container
microservices = ["ms_chat", "ms_gestione_prodotti", "altro_microservizio"]

def build_microservice_image(microservice_path, microservice_name):
    subprocess.run(["docker", "build", "-t", microservice_name, "."], cwd=microservice_path)

def start_microservice_container(microservice_path):
    subprocess.run(["docker-compose", "up", "-d"], cwd=microservice_path)
    time.sleep(5)  # Attesa breve per assicurarsi che il servizio abbia avuto il tempo di avviarsi completamente

def start_eureka_server():
    subprocess.run(["docker-compose", "-f", "../eureka/docker-compose.yml", "up", "-d"], cwd=os.path.dirname(os.path.realpath(__file__)))

def start_consul():
    subprocess.run(["docker-compose", "-f", "../consul/docker-compose.yml", "up", "-d"], cwd=os.path.dirname(os.path.realpath(__file__)))

def start_gateway():
    subprocess.run(["docker-compose", "-f", "../gateway/docker-compose.yml", "up", "-d"], cwd=os.path.dirname(os.path.realpath(__file__)))

def start_main_system():
    subprocess.run(["docker-compose", "-f", "../docker-compose.yml", "up", "-d"], cwd=os.path.dirname(os.path.realpath(__file__)))


# Esegui la costruzione delle immagini e avvia i container per i microservizi interni
for microservice in microservices:
    build_microservice_image(microservice, f"nome_microservizio_{microservice}")
    start_microservice_container(microservice)

# Avvia Consul
start_consul()

# Avvia il server Eureka
start_eureka_server()

# Avvia il container del gateway
start_gateway()

# Avvia il sistema principale con Eureka e il gateway
start_main_system()

print("Sistema avviato con successo.")
