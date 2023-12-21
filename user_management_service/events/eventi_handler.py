from confluent_kafka import Consumer, KafkaException
from db.engine import get_db
from repository import UserManagementRepository
import logging  

# # Configura il logger
# logging.basicConfig(level=logging.INFO)  # Imposta il livello di log a INFO o il livello che preferisci
# logger = logging.getLogger(__name__)

# logger.info("Il tuo messaggio di log qui")
# logger.error("Un errore è accaduto: %s", errore)
# # Configurazione del server Kafka
# kafka_bootstrap_servers = "kafka:9092"
# consumer = Consumer(
#     {
#         "bootstrap.servers": kafka_bootstrap_servers,
#         "group.id": "user_group",
#     }
# )

# Funzione asincrona per gestire gli eventi Kafka
async def consume_kafka_events(consumer):
    # Printa un messaggio di tentativo di connessione al broker Kafka
    print("Trying to connect to Kafka broker...")

    # Sottoscrivi il consumer al topic "user_events"
    consumer.subscribe(["user_events"])
    
    try:
        # Ciclo di polling per ricevere gli eventi
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                # Gestione degli errori di Kafka
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Kafka error: {msg.error()}")
                    break
            
            # Estrai i dati dell'evento dalla stringa decodificata
            event_data = eval(msg.value().decode("utf-8"))
            print(f"Received Kafka event: {event_data}")  

            # Se l'evento è di tipo "user_created", crea un nuovo utente
            if event_data["event_type"] == "user_created":
                username = event_data["username"]
                email = event_data["email"]
                n_telefono = event_data["n_telefono"]
                role_id = event_data["role_id"]
                
                # Printa i dettagli dell'utente creato
                print(f"Creating user: {username}, Email: {email}")
                
                # Ottieni la sessione del database
                db_session = get_db()            
                user_repository = UserManagementRepository()
                
                # Crea l'utente nel database
                user_repository.create_user(
                    db_session, username, email, hashed_password="some_hashed_password", role_id=role_id, n_telefono=n_telefono
                )
                
                # Chiudi la sessione del database
                db_session.close()
    except KafkaException as kafka_exception:
        print(f"Kafka error: {kafka_exception}")
        logging.error(f"Kafka error: {kafka_exception}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        # Chiudi il consumer alla fine dell'esecuzione
        consumer.close()
# ci sono tutte le api e funzioni