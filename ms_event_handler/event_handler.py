# handler/main.py
from fastapi import FastAPI, HTTPException
from kafka import KafkaProducer, KafkaConsumer
from pydantic import BaseModel

app = FastAPI()

# Configura il produttore Kafka
kafka_bootstrap_servers = 'localhost:9092'
producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)

class Event(BaseModel):
    event_type: str
    data: dict

# Endpoint per ricevere eventi da altri microservizi
@app.post("/events/")
async def receive_event(event: Event):
    # Invia l'evento al topic Kafka corrispondente
    producer.send(event.event_type, value=event.data)
    return {"message": "Event received and forwarded to Kafka"}

# Configura il consumatore Kafka
consumer = KafkaConsumer('all_events', group_id='handler_group', bootstrap_servers=kafka_bootstrap_servers)
# Funzione di esempio per gestire l'evento di recensione creata
def handle_review_created_event(data: dict):
    # Implementa la logica per gestire l'evento di recensione creata
    print(f"Review created: {data}")

# Funzione di esempio per gestire l'evento di nuovo messaggio
def handle_new_message_event(data: dict):
    # Implementa la logica per gestire l'evento di nuovo messaggio
    print(f"New message: {data}")
# Consumatore Kafka per gestire gli eventi
for message in consumer:
    event_data = eval(message.value)  # Dovresti deserializzare il messaggio come necessario
    event_type = event_data.get("event_type")
    data = event_data.get("data")

    # Esegui la logica di gestione dell'evento in base al tipo di evento
    if event_type == "review_created":
        handle_review_created_event(data)
    elif event_type == "new_message":
        handle_new_message_event(data)
    # Aggiungi altri casi se necessario per altri tipi di eventi


# Esegui l'app FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8502)