# main.py

from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from . import models, repository, event_handler
from .dtos import ProductCreate, ProductRead
from .auth import get_current_user, check_user_role
import requests  # Importa la libreria requests per effettuare richieste HTTP
from fastapi import FastAPI, HTTPException, Depends
from starlette.middleware.trustedhost import TrustedHostMiddleware
from scripts.config import eureka_config



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
models.Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# Inizializzazione del repository
product_repository = repository.ProductRepository()

# Configura il produttore Kafka
kafka_bootstrap_servers = 'localhost:9092'
producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)

# Esempio di produttore Kafka
@app.post("/send_event/")
async def send_event():
    # Logica per creare un evento
    event_data = {"event_type": "custom_event", "data": "Dati personalizzati"}
    
    # Invia l'evento a Kafka
    producer.send("product_events", value=str(event_data))

    return {"message": "Evento inviato con successo a Kafka"}
# Endpoint per creare un nuovo prodotto (solo per admin)
@app.post("/products/", response_model=ProductRead)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    user_role: str = Depends(check_user_role(required_role="admin"))
):
    return product_repository.create_product(db, product)

# Endpoint per ottenere tutti i prodotti con paginazione
@app.get("/products/", response_model=List[ProductRead])
async def get_all_products(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Numero di elementi da saltare"),
    limit: int = Query(10, le=100, description="Limite di elementi da restituire"),
):
    products = db.exec(select(Product).offset(skip).limit(limit)).all()
    return products

# ... Altri endpoint ...

# Endpoint per eliminare un prodotto (solo per admin)
@app.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    user_role: str = Depends(check_user_role(required_role="admin"))
):
    # Implementazione per eliminare il prodotto
    pass

# ... Altri endpoint ...

product_repository = repository.ProductRepository()

# Endpoint per registrare il microservizio presso il servizio di autenticazione
@app.post("/register_with_auth_service", response_model=str)
async def register_with_auth_service():
    auth_service_url = "http://authentication_service:8000/register_microservice"
    service_name = "products"  # Sostituisci con il nome del tuo microservizio

    response = requests.post(auth_service_url, json={"service_name": service_name})

    if response.status_code == 200:
        return "Microservice registered successfully with authentication service"
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to register with authentication service")
# Esegui l'app FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=806)