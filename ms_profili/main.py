import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware
from api.profile_api import router as api_router
from db import Session, create_table
from events.eventi_handler import consume_kafka_events
from middleware import RoleMiddleware
from db.engine import get_db, get_engine
from fastapi.staticfiles import StaticFiles
from confluent_kafka import Consumer
import colorama
from colorama import Fore, Style
from registrazione_service import register_service
from api.profile_api import consume_user_events
app = FastAPI()

# Configura il middleware TrustedHostMiddleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

asyncio.create_task(consume_user_events())

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
def get_session_local():
    engine = get_db()
    return Session(bind=engine)

# SessionLocal è ora una funzione invece di un'istanza
SessionLocal = get_session_local()

role_middleware = RoleMiddleware

# Kafka
kafka_bootstrap_servers = "kafka:9092"
consumer = Consumer(
    {
        "bootstrap.servers": kafka_bootstrap_servers,
        "group.id": "user_group",
    }
)

# Esegui la funzione consume_kafka_events in un thread separato
asyncio.ensure_future(consume_kafka_events(consumer=consumer))

# Aggiungi le API al router principale
app.include_router(api_router, prefix="/api", tags=["api"])
app.mount("/statics", StaticFiles(directory="statics"), name="statics")

# Funzione per registrare il microservizio presso il servizio di autenticazione
def register_with_auth_service():
    # Implementa la registrazione con il servizio di autenticazione
    pass

# Aggiungi altre configurazioni e API secondo le tue esigenze

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
