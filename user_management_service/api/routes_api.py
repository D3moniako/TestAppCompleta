# user_management_service/api/routes_api.py
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from repository import UserManagementRepository,SecurityRepository
from middleware import RoleMiddleware
from db.engine import get_engine,get_db
# Corretto l'import per get_session_local
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.sicurezza_api import get_password_hash

from db.modelli import Utente,TokenData
from typing import Optional,List
import logging
from middleware import get_current_user
from confluent_kafka import Consumer, Producer
router = APIRouter()

# Crea un'app FastAPI e un router API


# Monta la cartella statics per gestire le risorse statiche

# Configura i template Jinja2
templates = Jinja2Templates(directory="templates")

# Aggiungi configurazione per il logging
logging.basicConfig(level=logging.INFO)
###
user_repository = UserManagementRepository()
security_repository= SecurityRepository()
role_middleware = RoleMiddleware

engine = get_engine()
# Funzione per ottenere la sessione locale

def get_session_local():
    engine = get_db()
    return Session(bind=engine)  # Cambia questa riga



# SessionLocal è ora una funzione invece di un'istanza
SessionLocal = get_session_local()
# KAFKA
# Configurazione del server Kafka
kafka_bootstrap_servers = "kafka:9092"
consumer = Consumer(
    {
        "bootstrap.servers": kafka_bootstrap_servers,
        "group.id": "user_group",
    }
)
producer = Producer({"bootstrap.servers": kafka_bootstrap_servers})

##########################GESTIONE UTENTE########################

##CREA ADMIN
##CREA ADMIN
@router.post("/registration_admin", response_model=Utente)
async def registration_admin(username: str, password: str, email: str, n_telefono: Optional[str], db: Session = Depends(get_session_local)):

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
    user = user_repository.create_admin(db, username, email, hashed_password, roleid, n_telefono)

    # Invia l'evento di creazione utente a Kafka
    event_data = {"event_type": "user_created", "username": user.username}
    producer.produce("user_events", value=str(event_data))

    return user


# API REGISTRA UTENTE 
@router.post("/register_user", response_model=Utente)
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


@router.delete("/delete_user_by_admin/", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
async def delete_user_by_admin(target_username: str, db: Session = Depends(get_db)):
    """
    Cancella un utente da un amministratore.
    """
    try:
        # Controlla se l'utente da eliminare esiste
        user_to_delete = user_repository.get_user_by_username(db, target_username)
        if user_to_delete:
            # Verifica se l'utente da cancellare ha il ruolo "superadmin"
            if user_to_delete.role.name == "superadmin":
                raise HTTPException(
                    status_code=400,
                    detail="Impossibile cancellare un superadmin."
                )

            # Cancella l'utente
            user_repository.delete_user_by_name(db, target_username)
            return {"message": f"L'utente {target_username} è stato cancellato con successo"}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Utente con username {target_username} non trovato",
            )
    except HTTPException as e:
        return e

@router.get("/users_by_criteria/", response_model=List[Utente])
async def get_users_by_criteria(role_name: str, status: int, db: Session = Depends(get_session_local)):
    """
    Ottieni utenti in base a ruolo e stato.
    """
    try:
        users = user_repository.get_users_by_criteria(db, role_name, status)
        return users
    except HTTPException as e:
        return e

########################################################################

@router.get("/get_all_users_by_status/")
async def get_all_users_by_status(status: int, db: Session = Depends(get_session_local)):
    users = user_repository.get_users_by_status(db, status)
    return users

@router.delete("/delete_user_by_status/")
async def delete_user_by_status(status: int, username: str, db: Session = Depends(get_session_local)):
    return user_repository.delete_user_by_status(db, status, username)

@router.get("/get_all_users/")
async def get_all_users(db: Session = Depends(get_session_local)):
    users = user_repository.get_all_users(db)
    return users

@router.delete("/delete_user_by_name/")
async def delete_user_by_name(username: str, db: Session = Depends(get_session_local)):
    return user_repository.delete_user_by_name(db, username)

@router.get("/get_all_users_by_role/")
async def get_all_users_by_role(role_name: str, db: Session = Depends(get_session_local)):
    users = user_repository.get_users_by_role(db, role_name)
    return users


###########################API TEST GATAWAY##########
   # request serve per passare qualcosa che non so nel caso volessi passare dati a questa api che genera una pagina html
@router.get("/home", response_class=HTMLResponse)
def get_home(current_user: Utente = Depends(get_current_user)):
    print("DALL HTML FATTO MALISSIMO")
    return templates.TemplateResponse("admin_profile.html", {"request": {"user": current_user}})

    # return "ciaoooooooo"
@router.get('/ciao')
async def saluta():
    return {"message": "CIAO DAL MICROSERVIZO USER_MANAGEMENT"}

# @router.get("/health")
# async def health():
#     return {"status": "ok"}


@router.post("/handle_comment_submission")
async def handle_comment_submission(event_data: dict):
    # Esegui le operazioni necessarie per elaborare il commento
    username = event_data.get("username", "")
    product_id = event_data.get("product_id", "")
    comment = event_data.get("comment", "")

    # Aggiungi logica per gestire il commento
    # logging.info(f"Received comment for product {product_id} from user {username}: {comment}")
    logging.info("Received comment for product %s from user %s: %s", product_id, username, comment)

    return {"message": "Comment handled successfully"}
#############################SECURE POINT################################RUOLI###########################################################


# In sintesi, questa funzione rappresenta un endpoint sicuro che restituisce alcune informazioni 
# sull'utente corrente autenticato in risposta a una richiesta GET a "/secure-endpoint/".
# aggiunto il middlaware come dipendenza
# API sicura con middleware per ruoli specifici

@router.get("/secure-endpoint/", response_model=dict,dependencies=[Depends(role_middleware)])
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
    
    
###########################SECURE POINT #########################
# Esempio di endpoint con middleware per ruoli specifici
@router.get("/endpoint-for-admins", response_model=dict, dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))],)
async def endpoint_for_admins(current_user: TokenData = Depends(get_current_user)):
    return {"message": f"Questa api è accessibile a for admins: Benvenuto, {current_user.username}"}

@router.get("/endpoint-for-users", response_model=dict, dependencies=[Depends(RoleMiddleware(allowed_roles=["base_user"]))])
async def endpoint_for_users(current_user: TokenData = Depends(get_current_user)):
    return {"message": f"Questa api è accessibile a for users: Benvenuto, {current_user.username}"}

@router.post("/endpoint-foreditors/", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin", "editor"]))])
async def endpoint_for_multiroles(current_user: TokenData = Depends(get_current_user)):
    return {"message": f"Questa api è accessibile a  users and editors: Benvenuto, {current_user.username}"}
#In questo esempio, RoleMiddleware accetta una lista di ruoli consentiti e verifica se l'utente autenticato possiede almeno uno di questi ruoli. Puoi applicare questo middleware a diversi endpoint, specificando i ruoli consentiti per ciascun endpoint.
#####################################KAFKA EVENTI###########################
# Esempio di produttore Kafka
@router.post("/send_event/")
async def send_event():
    # Logica per creare un evento
    event_data = {"event_type": "custom_event", "data": "Dati personalizzati"}

    # Invia l'evento a Kafka
    producer.produce("user_events", value=str(event_data))

    return {"message": "Evento inviato con successo a Kafka"}

