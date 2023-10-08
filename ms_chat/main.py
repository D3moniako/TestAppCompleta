from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from . import models, repository, event_handler
from .dtos import ChatCreate, MessageCreate, ChatRead, MessageRead
from .auth import get_current_user, check_user_role
from starlette.middleware.trustedhost import TrustedHostMiddleware
from scripts.config import eureka_config
import requests
import routes  # Assicurati di importare le routes del microservizio

app = FastAPI()

# Configura Eureka Client
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In produzione, specifica gli host consentiti
)
# Configurazione della sessione del database
database_url = "postgresql://user:password@localhost/db_name"
engine = create_engine(database_url)
models.Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# Registra il microservizio presso il servizio di autenticazione
def register_microservice(service_name):
    auth_service_url = "http://authentication_service:5000/register_microservice"
    data = {"service_name": service_name}
    response = requests.post(auth_service_url, json=data)
    print(response.json())

# Esempio di registrazione del microservizio
register_microservice("ms_chat")

chat_repository = repository.ChatRepository()
message_repository = repository.MessageRepository()

# Endpoint per creare un nuovo messaggio in una chat
@app.post("/chats/{chat_id}/messages/", response_model=MessageRead)
async def create_message(
    chat_id: int,
    message: MessageCreate,
    db: Session = Depends(repository.get_db),
    current_user: str = Depends(get_current_user)
):
    # Verifica se l'utente fa parte della chat
    chat = chat_repository.get_chat_by_id(db, chat_id)
    if current_user not in (chat.participant1_id, chat.participant2_id):
        raise HTTPException(status_code=403, detail="You are not a participant in this chat")

    # Crea e restituisci il messaggio
    return message_repository.create_message(db, chat_id, current_user, message)

# Endpoint per ottenere tutti i messaggi di una chat con paginazione
@app.get("/chats/{chat_id}/messages/", response_model=List[MessageRead])
async def get_chat_messages(
    chat_id: int,
    db: Session = Depends(repository.get_db),
    skip: int = Query(0, ge=0, description="Numero di messaggi da saltare"),
    limit: int = Query(10, le=100, description="Limite di messaggi da restituire"),
    current_user: str = Depends(get_current_user)
):
    # Verifica se l'utente fa parte della chat
    chat = chat_repository.get_chat_by_id(db, chat_id)
    if current_user not in (chat.participant1_id, chat.participant2_id):
        raise HTTPException(status_code=403, detail="You are not a participant in this chat")

    # Ottieni i messaggi con paginazione
    messages = message_repository.get_messages_by_chat_id(db, chat_id, skip, limit)
    return messages

# Endpoint per avviare una chat
@app.post("/chats/", response_model=models.Chat)
async def create_chat(
    participant2_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(repository.get_db),
    check_user_role: bool = Depends(check_user_role)
):
    # Verifica se il participant2_id esiste o è valido
    if not user_repository.user_exists(db, participant2_id):
        raise HTTPException(status_code=404, detail="Participant2 does not exist")

    # Creazione della chat
    chat = chat_repository.create_chat(db, participant1_id=current_user, participant2_id=participant2_id)

    # Pubblicazione dell'evento di chat creata
    event_handler.publish_chat_created_event(chat)

    return chat

# Endpoint per ottenere tutte le chat
@app.get("/chats/", response_model=List[ChatRead])
async def get_chats(
    db: Session = Depends(repository.get_db),
    current_user: str = Depends(get_current_user)
):
    # Ottieni tutte le chat in cui l'utente è coinvolto
    chats = chat_repository.get_chats_by_participant(db, current_user)
    return chats

# Esegui l'app FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
