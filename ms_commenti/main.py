# ms_comment/main.py
from fastapi import FastAPI, HTTPException, Depends, WebSocket
from sqlalchemy.orm import Session
from kafka import KafkaConsumer, KafkaProducer
from scripts.config import eureka_config
from starlette.middleware.trustedhost import TrustedHostMiddleware
from . import comments_models, comments_repository

app = FastAPI()

# Configura Eureka Client
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In produzione, specifica gli host consentiti
)

# Dipendenza per ottenere la sessione del database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configurazione della sessione del database
database_url = "postgresql://user:password@localhost/db_name"
engine = create_engine(database_url)
comments_models.Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Inizializzazione del repository
review_repository = comments_repository.ReviewRepository()

# Configura il consumatore Kafka
kafka_bootstrap_servers = 'localhost:9092'
consumer = KafkaConsumer('review_events', group_id='review_group', bootstrap_servers=kafka_bootstrap_servers)

# Configura il produttore Kafka
producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)

# Consumatore Kafka per gestire gli eventi
for message in consumer:
    event_data = eval(message.value)  # Dovresti deserializzare il messaggio come necessario
    if event_data["event_type"] == "review_created":
        review_repository.handle_review_created_event(event_data)
    # Aggiungi altri casi se necessario per altri tipi di eventi

# Esempio di produttore Kafka
@app.post("/send_event/")
async def send_event():
    # Logica per creare un evento
    event_data = {"event_type": "custom_event", "data": "Dati personalizzati"}
    
    # Invia l'evento a Kafka
    producer.send("review_events", value=str(event_data))

    return {"message": "Evento inviato con successo a Kafka"}

# Endpoint per creare una nuova recensione
@app.post("/reviews/", response_model=comments_models.Review)
async def create_review(review: comments_models.Review, db: Session = Depends(get_db)):
    # Logica per creare la recensione...

    # Esempio di invio di un evento a Kafka
    review_event = {"event_type": "review_created", "data": {"review_id": 456, "product_id": review.product_id}}
    producer.send("review_events", value=str(review_event))

    return review_repository.create_review(db, review)


# Endpoint per ottenere tutte le recensioni di un prodotto
@app.get("/reviews/{product_id}", response_model=list[comments_models.Review])
async def get_reviews_for_product(product_id: int, db: Session = Depends(get_db)):
    return review_repository.get_reviews_for_product(db, product_id)
# Esegui l'app FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)