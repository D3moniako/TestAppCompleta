# main.py
# main.py
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware
from registrazione_service import register_service

app = FastAPI()  # Muovi l'import all'inizio del file

from events.eventi_handler import consume_kafka_events
from api.routes_api import router as routes_router
from api.roles_api import router as roles_router
from api.sicurezza_api import router as security_router
from db.manager import create_table, Session
import requests
from db.engine import get_engine,get_db
from fastapi.staticfiles import StaticFiles
from confluent_kafka import Consumer
from middleware import RoleMiddleware
from typing import Union


import colorama
from colorama import Fore, Style

app.include_router(routes_router, prefix="/routes", tags=["users"])
app.include_router(roles_router, prefix="/roles", tags=["roles"])
app.include_router(security_router, prefix="/security", tags=["security"])

#
app.mount("/statics", StaticFiles(directory="statics"), name="statics")


# Configura il middleware TrustedHostMiddleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

engine = get_engine()
create_table()
colorama.init(autoreset=True)  # Inizializza colorama all'inizio dello script

def colorize_ascii(file_path):
    with open(file_path, "r") as file:
        ascii_text = file.read()

    # Imposta il colore verde per il testo
    colored_ascii = f"{Fore.GREEN}{ascii_text}{Style.RESET_ALL}"

    # Stampa il testo colorato nel terminale di Visual Studio Code
    print(colored_ascii)


# Funzione per ottenere la sessione locale
print("ciao dal MAINNNNNNNN ")
def get_session_local():
    engine = get_db()
    return Session(bind=engine)  # Cambia questa riga


# SessionLocal è ora una funzione invece di un'istanza
SessionLocal = get_session_local()


role_middleware = RoleMiddleware

#kafka 
kafka_bootstrap_servers = "kafka:9092"
consumer = Consumer(
    {
        "bootstrap.servers": kafka_bootstrap_servers,
        "group.id": "user_group",
    }
)


# Esegui la funzione consume_kafka_events in un thread separato
# asyncio.ensure_future(consume_kafka_events())

# Funzione per registrare il microservizio presso il servizio di autenticazione
# def register_with_auth_service():  
#     auth_service_url = "http://authentication_service:8000/register_microservice"
#     service_name = "user_management"  

#     response = requests.post(auth_service_url, json={"service_name": service_name})

#     if response.status_code == 200:
#         return "Microservice registered successfully with authentication service"
#     else:
#         raise HTTPException(
#             status_code=response.status_code,
#             detail="Failed to register with authentication service",
#         )

# ... (Continua con tutte le implementazioni delle API e delle funzioni nel tuo file originale)

@app.get("/health")
async def health():
    return {"status": "ok"}
# Avvia il server Uvicorn
if __name__ == "__main__":
    
    service_name = "user_management_service"
    service_port = 80

    loop = asyncio.get_event_loop()
    # REGISTRAZIONE CONSUL
    loop.run_until_complete(register_service(service_name, service_port))
    asyncio.ensure_future(consume_kafka_events(consumer=consumer))

    # Avvia il server Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=service_port, reload=True)
    file_path = "souhail2.txt"
    colorize_ascii(file_path)
    