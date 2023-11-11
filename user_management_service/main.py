import asyncio
from h11 import Request
import jwt
import bcrypt
import requests
import uvicorn
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status,Header,Query

from typing import List,Optional

import logging
from starlette.middleware.trustedhost import TrustedHostMiddleware
from confluent_kafka import Producer, Consumer, KafkaError

from middleware import RoleMiddleware,get_current_user
from repository import UserManagementRepository, SecurityRepository
from db.manager import create_table, Session
from db.modelli import Utente, TokenData,UserRole
from db.engine import get_db, get_engine
from scripts.config_eureka import eureka_config
from registrazione_service import register_service
from convalida.email_manager import convalida_via_email
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from convalida.sms_manager import send_whatsapp
from starlette.requests import Request

# Crea un'app FastAPI e un router API
app = FastAPI()
router = APIRouter()
#### INCLUDO ROTTE #####
app.include_router(router)
##### INCLUDO CSS E HTML STATICO
# Monta la cartella statics per gestire le risorse statiche
app.mount("/statics", StaticFiles(directory="statics"), name="statics")

# Configura i template Jinja2
templates = Jinja2Templates(directory="templates")

#################################

# Aggiungi configurazione per il logging
logging.basicConfig(level=logging.INFO)

# Inizializza i repository e il middleware

user_repository = UserManagementRepository()
security_repository = SecurityRepository()  # Aggiunto l'invocazione della classe
role_middleware = RoleMiddleware

# Configura il motore del database e crea le tabelle
engine = get_engine()
create_table()
# Funzione per ottenere la sessione locale

def get_session_local():
    engine = get_db()
    return Session(bind=engine)  # Cambia questa riga


# SessionLocal è ora una funzione invece di un'istanza
SessionLocal = get_session_local()


# Configurazione del server Kafka

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
                n_telefono = event_data["n_telefono"]

                role_id=event_data["role_id"]
                print(f"Creating user: {username}, Email: {email}")  # Stampa le informazioni dell'utente
                db_session = get_session_local()            
                user_repository.create_user(
                    db_session, username, email, hashed_password="some_hashed_password",role_id=role_id,n_telefono=n_telefono
                )
                # Chiudi la sessione dopo l'uso
                db_session.close()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        consumer.close()


# Aggiungi il middleware TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)
# Configura lo schema di autenticazione OAuth2

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
producer = Producer({"bootstrap.servers": kafka_bootstrap_servers})


######################### FUNZIONI SICUREZZA#############################
# Funzione per ottenere l'hash della password
def get_password_hash(password: str):      
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

# Funzione per creare un token JWT
def create_jwt_token(data: dict):
    to_encode = data.copy()
    return jwt.encode(to_encode, "SECRET_KEY", algorithm="HS256")

######################### API TOKEN ###################
# API per ottenere un token di accesso
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session_local)):
    user = security_repository.authenticate_user(db, form_data.username, form_data.password)

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
    if user and user.status == 0:
        # if not send_whatsapp(user, token): # viene eseguita una volta e allo stesso tempo eseguendola so se è vera o falsa
        #     raise HTTPException(                 # e posso usarla per gestire l'eccezione
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Errore durante l'invio dell'messaggio whatsapp di conferma",
        #     ) 
        if not convalida_via_email(user, token): # viene eseguita una volta e allo stesso tempo eseguendola so se è vera o falsa
            raise HTTPException(                 # e posso usarla per gestire l'eccezione
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Errore durante l'invio dell'email di conferma",
            )  
        
    
    return {"access_token": token, "token_type": "bearer"}

# Funzione per ottenere l'utente dal token
def get_user_from_token(token: str = Depends(oauth2_scheme),db: Session = Depends(get_session_local)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossibile convalidare le credenziali",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodifica il token
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    # Ottieni l'utente dal repository o dal database
    user = security_repository.get_user_by_username(db, username)

    if user is None:
        raise credentials_exception

    return user



# Questo sarebbe l'endpoint per la conferma dell'account
@app.get("/conferma_account")
async def conferma_account(token: str = Query(..., description="Token di conferma dell'account"), db: Session = Depends(get_session_local)):
    # Estrai l'utente dal database utilizzando il token
    user = get_user_from_token(token, db)
    username = user.username
    role_name = user.role.role_name
    print(f'role_name da api conferma_account: {role_name}')
    if user:
        # Aggiorna lo stato dell'account nel database (simulato come un cambio di stato da 0 a 1)
        user_repository.update_account_status(db, username, new_status=1)    
        if role_name == 'admin':
            redirect_url = f"http://localhost:8000/home?token={token}"
            response = RedirectResponse(url=redirect_url, status_code=303)
            return response
        # return {"message": f"Account di {username} confermato con successo"}   
    else:
        raise HTTPException(status_code=400, detail="Token non valido")













# API per ottenere l'utente corrente dal token
@app.get("/users/me", response_model=Utente)
async def read_users_me(current_user: Utente = Depends(get_user_from_token)):
    # convalida_via_email(current_user)
    return current_user


#####################################KAFKA EVENTI###########################
# Esempio di produttore Kafka
@app.post("/send_event/")
async def send_event():
    # Logica per creare un evento
    event_data = {"event_type": "custom_event", "data": "Dati personalizzati"}

    # Invia l'evento a Kafka
    producer.produce("user_events", value=str(event_data))

    return {"message": "Evento inviato con successo a Kafka"}






#############################SECURE POINT################################RUOLI###########################################################


# In sintesi, questa funzione rappresenta un endpoint sicuro che restituisce alcune informazioni 
# sull'utente corrente autenticato in risposta a una richiesta GET a "/secure-endpoint/".
# aggiunto il middlaware come dipendenza
# API sicura con middleware per ruoli specifici

@app.get("/secure-endpoint/", response_model=dict,dependencies=[Depends(role_middleware)])
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
    
    

# Esempio di endpoint con middleware per ruoli specifici
@app.get("/endpoint-for-admins", response_model=dict, dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))],)
async def endpoint_for_admins(current_user: TokenData = Depends(get_current_user)):
    return {"message": f"Questa api è accessibile a for admins: Benvenuto, {current_user.username}"}

@app.get("/endpoint-for-users", response_model=dict, dependencies=[Depends(RoleMiddleware(allowed_roles=["base_user"]))])
async def endpoint_for_users(current_user: TokenData = Depends(get_current_user)):
    return {"message": f"Questa api è accessibile a for users: Benvenuto, {current_user.username}"}

@app.post("/endpoint-foreditors/", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin", "editor"]))])
async def endpoint_for_multiroles(current_user: TokenData = Depends(get_current_user)):
    return {"message": f"Questa api è accessibile a  users and editors: Benvenuto, {current_user.username}"}
#In questo esempio, RoleMiddleware accetta una lista di ruoli consentiti e verifica se l'utente autenticato possiede almeno uno di questi ruoli. Puoi applicare questo middleware a diversi endpoint, specificando i ruoli consentiti per ciascun endpoint.

#########################CRUD RUOLI###################
###CREA RUOLI
@app.post("/create-role/", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
async def create_role(
    role_name: str,
    user: Utente = Depends(RoleMiddleware(allowed_roles=["admin"])),
    db: Session = Depends(get_session_local)
):
    existing_role = db.query(UserRole).filter_by(role_name=role_name).first()

    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ruolo con nome {role_name} esiste già",
        )

    new_role = user_repository.create_role(db, role_name)

    if new_role:
        return {"message": f"Nuovo ruolo {role_name} creato con successo"}

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to create role",
    )


###CANCELLA RUOLI 
@app.delete("/delete-role/{role_name}", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
async def delete_role(role_name: str, db: Session = Depends(get_session_local)):
    result = user_repository.delete_role(db, role_name)
    return result
### VISUALIZZA TUTTI I RUOLI
@app.get("/get-all-roles", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
async def get_all_roles(db: Session = Depends(get_session_local)):
    roles = user_repository.get_all_roles(db)
    return roles


### ASSEGNARE RUOLI
@app.post("/assign-role-with-userid/", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
async def assign_role_with_id(
    user_id: int,
    role_name: str,
    db: Session = Depends(get_session_local),
    user_repo: UserManagementRepository = Depends(UserManagementRepository)
):
    return user_repo.upload_role_to_user_by_name(db, user_id, role_name)

@app.post("/assign-role-by-username/", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
async def assign_role_by_username(
    username: str,
    role_name: str,
    db: Session = Depends(get_session_local),
    user_repo: UserManagementRepository = Depends(UserManagementRepository)
):
    user = user_repo.get_user_by_username(db, username)

    if user:
        if user.role_id:
            # Aggiorna il ruolo esistente
            user_repo.upload_role_to_user_by_name(db, user.id, role_name)
            return {"message": "Ruolo aggiornato con successo"}

        # Se l'utente non ha un ruolo, assegna il nuovo ruolo
        user_repo.upload_role_to_user_by_name(db, user.id, role_name)
        return {"message": "Ruolo assegnato con successo"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Utente con username {username} non trovato",
    )



#####################################MICROSERVIZI

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

#  endpoint ...
##########################GESTIONE UTENTE########################

##CREA ADMIN
##CREA ADMIN
@app.post("/registration_admin", response_model=Utente)
async def registration_admin(username: str, password: str, email: str,n_telefono:Optional[str], db: Session = Depends(get_session_local)):

    # Verifica se il ruolo "admin" esiste
    admin_role = user_repository.get_role_by_name(db, role_name="admin")
  
    if not admin_role:
        # Se non esiste, crea il ruolo
        admin_role = user_repository.create_role(db, role_name="admin")

    # Controllo se esiste già un utente con la stessa email
    existing_user_by_email = user_repository.get_user_by_email(db, email)
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {email} already exists",
        )

    # Controllo se esiste già un utente con lo stesso username
    existing_user_by_username = user_repository.get_user_by_username(db, username)
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username {username} already exists",
        )

    # Procedi con la registrazione se entrambi i controlli passano
    hashed_password = get_password_hash(password)
    roleid = admin_role.id
    user = user_repository.create_admin(db, username, email, hashed_password,roleid,n_telefono)
    

    # Invia l'evento di creazione utente a Kafka
    event_data = {"event_type": "user_created", "username": user.username}
    producer.produce("user_events", value=str(event_data))

    return user


# API REGISTRA UTENTE 
@app.post("/register_user", response_model=Utente)
async def register_user(username: str, password: str, email: str,n_telefono:Optional[str], db: Session = Depends(get_session_local)):

    # Controllo se esiste già un utente con la stessa email
    existing_user_by_email = user_repository.get_user_by_email(db, email)
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {email} already exists",
        )
        

    # Controllo se esiste già un utente con lo stesso username
    existing_user_by_username = user_repository.get_user_by_username(db, username)
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username {username} already exists",
        )

    # Procedi con la registrazione se entrambi i controlli passano
    hashed_password = get_password_hash(password)
    base_user_role = user_repository.get_role_by_name(db, role_name="base_user")
    role_id = base_user_role.id

    user = user_repository.create_user(db, username, email, hashed_password,role_id, n_telefono)


    # Assegna automaticamente il ruolo "user_base"
    user_repository.assign_role_to_user_by_name(db, user.id, role_name="base_user")


    # Invia l'evento di creazione utente a Kafka
    event_data = {"event_type": "user_created", "username": user.username}
    producer.produce("user_events", value=str(event_data))

    return user


###########################API TEST GATAWAY##########
   # request serve per passare qualcosa che non so nel caso volessi passare dati a questa api che genera una pagina html
@app.get("/home", response_class=HTMLResponse)
def get_home(current_user: Utente = Depends(get_current_user)):
    print("DALL HTML FATTO MALISSIMO")
    return templates.TemplateResponse("admin_profile.html", {"request": {"user": current_user}})

    # return "ciaoooooooo"
@app.get('/ciao')
async def saluta():
    return{"message":" CIAO DAL MICROSERVIZO USER_MANAGEMENT"}

@app.get("/health")
async def health():
    return {"status": "ok"}     
###############################        


# ...

@app.post("/handle_comment_submission")
async def handle_comment_submission(event_data: dict):
    # Esegui le operazioni necessarie per elaborare il commento
    username = event_data.get("username", "")
    product_id = event_data.get("product_id", "")
    comment = event_data.get("comment", "")

    # Aggiungi logica per gestire il commento
    logging.info(f"Received comment for product {product_id} from user {username}: {comment}")
    
    return {"message": "Comment handled successfully"}
############################################
if __name__ == "__main__":
    service_name = "user_management_service"
    service_port = 80

    loop = asyncio.get_event_loop()
    #REGISTAZIONE CONSUL
    loop.run_until_complete(register_service(service_name, service_port))
    
    # Esegui la funzione consume_kafka_events in un thread separato
    asyncio.ensure_future(consume_kafka_events())
    # Avvia il server Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=service_port, reload=True)