
# user_management_service/main.py

from fastapi import FastAPI, Depends, HTTPException, status
import jwt
from fastapi import APIRouter  # Aggiunto import per APIRouter

from .repository import UserManagementRepository
from starlette.middleware.trustedhost import TrustedHostMiddleware
from kafka import KafkaConsumer, KafkaProducer
import bcrypt
import requests
from sqlalchemy.orm import sessionmaker
import uvicorn
from .db.manager import create_table  # Aggiunto il punto prima di db
from .modelli import User, TokenData  # Aggiunto il punto prima di modelli
from .db.engine import get_db, get_engine
from .scripts.config_eureka import eureka_config


app = FastAPI()

engine = get_engine()
create_table()
SessionLocal = get_db()

kafka_bootstrap_servers = 'localhost:9092'
consumer = KafkaConsumer('user_events', group_id='user_group', bootstrap_servers=kafka_bootstrap_servers)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)

app.eureka_config = eureka_config
router = APIRouter()
user_repository = UserManagementRepository()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)


for message in consumer:
    event_data = eval(message.value)
    if event_data["event_type"] == "user_created":
        username = event_data["username"]
        email = event_data["email"]  # Assuming email is part of the event_data
        user_repository.create_user(SessionLocal, username, email, hashed_password="some_hashed_password")







# Funzione per ottenere l'hash della password
def get_password_hash(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')
# Esempio di produttore Kafka
@app.post("/send_event/")
async def send_event():
    # Logica per creare un evento
    event_data = {"event_type": "custom_event", "data": "Dati personalizzati"}
    
    # Invia l'evento a Kafka
    producer.send("user_events", value=str(event_data))

    return {"message": "Evento inviato con successo a Kafka"}
# Funzione per creare un token JWT
def create_jwt_token(data: dict):
    to_encode = data.copy()
    return jwt.encode(to_encode, "SECRET_KEY", algorithm="HS256")

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_repository.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = {
        "sub": user.username,
        "scopes": ["me"],
    }
    token = create_jwt_token(token_data)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(user_repository.get_current_user)):
    return current_user

@router.post("/register_user", response_model=User)
async def register_user(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(password)
    user = user_repository.create_user(db, username, hashed_password)

    # Invia l'evento di creazione utente a Kafka
    producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
    event_data = {"event_type": "user_created", "username": user.username}
    producer.send("user_events", value=str(event_data))

    return user

@router.get("/secure-endpoint/", response_model=dict)
async def secure_endpoint(current_user: TokenData = Depends(user_repository.get_current_user)):
    user = user_repository.get_user_by_username(current_user.username)
    return {"message": "This is a secure endpoint!", "username": user.username, "email": user.email}
# Funzione per registrare il microservizio presso il servizio di autenticazione
def register_with_auth_service():
    auth_service_url = "http://authentication_service:8000/register_microservice"
    service_name = "user_management"  # Sostituisci con il nome del tuo microservizio

    response = requests.post(auth_service_url, json={"service_name": service_name})

    if response.status_code == 200:
        return "Microservice registered successfully with authentication service"
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to register with authentication service")

app.include_router(router)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)