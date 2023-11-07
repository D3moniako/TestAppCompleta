import asyncio
import jwt
import bcrypt
import requests
import uvicorn
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
import logging
from starlette.middleware.trustedhost import TrustedHostMiddleware
from confluent_kafka import Producer, Consumer, KafkaError

from repository import UserManagementRepository, SecurityRepository
from db.manager import create_table, Session
from db.modelli import Utente, TokenData
from db.engine import get_db, get_engine
from scripts.config_eureka import eureka_config
from registrazione_service import register_service

app = FastAPI()
router = APIRouter()
user_repository = UserManagementRepository()
security_repository = SecurityRepository()  # Aggiunto l'invocazione della classe

engine = get_engine()
create_table()
# Modifica il tuo codice per definire SessionLocal come funzione
def get_session_local():
    engine = get_db()
    return Session(bind=engine)  # Cambia questa riga


# Nel tuo main.py, usa get_session_local() invece di SessionLocal()
SessionLocal = get_session_local()

kafka_bootstrap_servers = "kafka:9092"

consumer = Consumer(
    {
        "bootstrap.servers": kafka_bootstrap_servers,
        "group.id": "user_group",
    }
)

# Funzione asincrona per gestire gli eventi Kafka
async def consume_kafka_events():
    print("Trying to connect to Kafka broker...")
    consumer.subscribe(["user_events"])
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Kafka error: {msg.error()}")
                    break
            event_data = eval(msg.value().decode("utf-8"))
            print(f"Received Kafka event: {event_data}")  # Stampa l'evento Kafka ricevuto
            if event_data["event_type"] == "user_created":
                username = event_data["username"]
                email = event_data["email"]
                print(f"Creating user: {username}, Email: {email}")  # Stampa le informazioni dell'utente
                db_session = get_session_local()            
                user_repository.create_user(
                    db_session, username, email, hashed_password="some_hashed_password"
                )
                # Chiudi la sessione dopo l'uso
                db_session.close()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        consumer.close()



app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
producer = Producer({"bootstrap.servers": kafka_bootstrap_servers})

# Funzione per ottenere l'hash della password
def get_password_hash(password: str):      
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

# Esempio di produttore Kafka
@app.post("/send_event/")
async def send_event():
    # Logica per creare un evento
    event_data = {"event_type": "custom_event", "data": "Dati personalizzati"}

    # Invia l'evento a Kafka
    producer.produce("user_events", value=str(event_data))

    return {"message": "Evento inviato con successo a Kafka"}

# Funzione per registrare utente
@router.post("/register_user", response_model=Utente)
async def register_user(username: str, password: str, email: str, db: Session = Depends(get_session_local)):
  
    print("Registrazione  22 in corso CIAOOOO")
    hashed_password = get_password_hash(password)
    user = user_repository.create_user(db, username, email, hashed_password)
    
    # Invia l'evento di creazione utente a Kafka
    event_data = {"event_type": "user_created", "username": user.username}
    producer.produce("user_events", value=str(event_data))

    return user

# In sintesi, questa funzione rappresenta un endpoint sicuro che restituisce alcune informazioni 
# sull'utente corrente autenticato in risposta a una richiesta GET a "/secure-endpoint/".
@router.get("/secure-endpoint/", response_model=dict)
async def secure_endpoint(
    current_user: TokenData = Depends(security_repository.verify_token),
    user_repo: UserManagementRepository = Depends(),
):
    user = user_repo.get_user_by_username(current_user.username)
    return {
        "message": "This is a secure endpoint!",
        "username": user.username,
        "email": user.email,
    }

# Funzione per registrare il microservizio presso il servizio di autenticazione
def register_with_auth_service():  
    auth_service_url = "http://authentication_service:8000/register_microservice"
    service_name = "user_management"  # Sostituisci con il nome del tuo microservizio

    response = requests.post(auth_service_url, json={"service_name": service_name})

    if response.status_code == 200:
        return "Microservice registered successfully with authentication service"
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to register with authentication service",
        )

# Altri endpoint e configurazioni...

@app.get("/html", response_class=HTMLResponse)
def get_html():
    print("dall'html di MERDA")  # Aggiunto per il debug
    content = """
    <html>
        <head>
            <title>Test HTML Endpoint</title>
        </head>
        <body>
            <h1>Provalaaaaaaaaaaaa</h1>
            <p>You can customize this HTML content based on your needs.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=content)

@app.get('/ciao')
async def saluta():
    return{"message":" CIAO DAL MICROSERVIZO USER_MANAGEMENT"}

@app.get("/health")
async def health():
    return {"status": "ok"}             
app.include_router(router)

# Aggiungi configurazione per il logging
logging.basicConfig(level=logging.INFO)

# ...

@app.post("/handle_comment_submission")
async def handle_comment_submission(event_data: dict):
    # Esegui le operazioni necessarie per elaborare il commento
    username = event_data.get("username", "")
    product_id = event_data.get("product_id", "")
    comment = event_data.get("comment", "")

    # Aggiungi logica per gestire il commento
    logging.info(f"Received comment for product {product_id} from user {username}: {comment}")

    # Aggiungi logica aggiuntiva se necessario

    return {"message": "Comment handled successfully"}

if __name__ == "__main__":
    service_name = "user_management_service"
    service_port = 80

    loop = asyncio.get_event_loop()
    loop.run_until_complete(register_service(service_name, service_port))
    
    # Esegui la funzione consume_kafka_events in un thread separato
    asyncio.ensure_future(consume_kafka_events())
    # Avvia il server Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=service_port, reload=True)