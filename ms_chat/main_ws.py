# CHAT CON WEB SOCKET E COMUNICAZIONE REATTIVA
from fastapi import FastAPI, WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
from . import repository, models
from .auth import get_current_user, check_user_role
from kafka import KafkaConsumer
from starlette.middleware.trustedhost import TrustedHostMiddleware
import requests  # Aggiunto import per le richieste HTTP

app = FastAPI()

# Configura Eureka Client
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In produzione, specifica gli host consentiti
)

chat_repository = repository.ChatRepository()
message_repository = repository.MessageRepository()

# Configura il consumatore Kafka
kafka_bootstrap_servers = 'localhost:9092'
consumer = KafkaConsumer('chat_events', group_id='chat_group', bootstrap_servers=kafka_bootstrap_servers)

# Funzione per registrare il microservizio presso il servizio di autenticazione
def register_with_auth_service():
    auth_service_url = "http://authentication_service:8000/register_microservice"
    service_name = "chat"  # Sostituisci con il nome del tuo microservizio

    response = requests.post(auth_service_url, json={"service_name": service_name})

    if response.status_code == 200:
        return "Microservice registered successfully with authentication service"
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to register with authentication service")

# Esempio di utilizzo della funzione di registrazione
register_with_auth_service()

# Consumatore Kafka per gestire gli eventi
for message in consumer:
    event_data = eval(message.value)  # Dovresti deserializzare il messaggio come necessario
    if event_data["event_type"] == "new_message":
        chat_id = event_data["chat_id"]
        user_id = event_data["user_id"]
        content = event_data["content"]
        # Gestisci il messaggio ricevuto, ad esempio, salvalo nel database
        message = message_repository.create_message(db, chat_id, user_id, {"content": content})
        # Invia il messaggio agli altri partecipanti alla chat tramite WebSocket
        for participant_id in get_participants(chat_id):
            if participant_id != user_id:
                participant_websocket = get_websocket_by_user(participant_id)
                if participant_websocket:
                    await participant_websocket.send_text(f"{user_id}: {content}")

# Funzioni di esempio per ottenere i partecipanti e la connessione WebSocket
def get_participants(chat_id: int):
    # Implementa la logica per ottenere i partecipanti alla chat
    pass

def get_websocket_by_user(user_id: str) -> WebSocket:
    # Implementa la logica per ottenere la connessione WebSocket associata all'utente
    pass

# WebSocket endpoint per connettersi a una chat
@app.websocket("/ws/chats/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    db: Session = Depends(repository.get_db),
    current_user: str = Depends(get_current_user)
):
    # Verifica se l'utente fa parte della chat
    chat = chat_repository.get_chat_by_id(db, chat_id)
    if current_user not in (chat.participant1_id, chat.participant2_id):
        raise HTTPException(status_code=403, detail="You are not a participant in this chat")

    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        # Gestisci il messaggio ricevuto, ad esempio, salvalo nel database
        message = message_repository.create_message(db, chat_id, current_user, {"content": data})
        # Invia il messaggio agli altri partecipanti alla chat tramite WebSocket
        for participant_id in (chat.participant1_id, chat.participant2_id):
            if participant_id != current_user:
                participant_websocket = get_websocket_by_user(participant_id)
                if participant_websocket:
                    await participant_websocket.send_text(f
# Esegui l'app FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)