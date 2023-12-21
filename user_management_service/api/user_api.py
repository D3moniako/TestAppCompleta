# # user_management_service/api/user_api.py


# from fastapi import APIRouter, Depends, HTTPException, status, FastAPI
# from fastapi.responses import HTMLResponse
# from fastapi.security import OAuth2PasswordBearer
# from typing import Optional

# import logging
# from starlette.middleware.trustedhost import TrustedHostMiddleware
# from sqlalchemy.orm import Session
# from confluent_kafka import Consumer, Producer
# from db.modelli import Utente
# # TokenData, UserRole
# from db.engine import  get_session_local

# # from db.manager import create_table, SessionLocal, get_db
# from middleware import RoleMiddleware, get_current_user
# from repository import UserManagementRepository, SecurityRepository
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# import bcrypt
# import jwt
# import requests 

# router = APIRouter()
# templates = Jinja2Templates(directory="templates")

# # Crea un'app FastAPI e un router API
# app = FastAPI()
# router = APIRouter()

# # Monta la cartella statics per gestire le risorse statiche
# app.mount("/statics", StaticFiles(directory="statics"), name="statics")

# # Configura i template Jinja2
# templates = Jinja2Templates(directory="templates")

# # Aggiungi configurazione per il logging
# logging.basicConfig(level=logging.INFO)

# # Inizializza i repository e il middleware
# user_repository = UserManagementRepository()
# security_repository = SecurityRepository()
# role_middleware = RoleMiddleware

# ################################################################
# # Configura il motore del database e crea le tabelle
# # SessionLocal è ora una funzione invece di un'istanza
# SessionLocal = get_session_local()

# ################################################################
# # Configurazione del server Kafka
# kafka_bootstrap_servers = "kafka:9092"
# consumer = Consumer(
#     {
#         "bootstrap.servers": kafka_bootstrap_servers,
#         "group.id": "user_group",
#     }
# )

# # Aggiungi il middleware TrustedHostMiddleware
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["*"],
# )

# # Configura lo schema di autenticazione OAuth2
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# producer = Producer({"bootstrap.servers": kafka_bootstrap_servers})

# ######################### FUNZIONI SICUREZZA#############################

# # Funzione per ottenere l'hash della password
# def get_password_hash(password: str):      
#     salt = bcrypt.gensalt()
#     hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
#     return hashed_password.decode("utf-8")

# # Funzione per creare un token JWT
# def create_jwt_token(data: dict):
#     to_encode = data.copy()
#     return jwt.encode(to_encode, "SECRET_KEY", algorithm="HS256")


# ###CANCELLA RUOLI 
# @app.delete("/delete-role/{role_name}", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
# async def delete_role(role_name: str, db: Session = Depends(get_session_local)):
#     result = user_repository.delete_role(db, role_name)
#     return result
# ### VISUALIZZA TUTTI I RUOLI
# @app.get("/get-all-roles", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
# async def get_all_roles(db: Session = Depends(get_session_local)):
#     roles = user_repository.get_all_roles(db)
#     return roles


# ### ASSEGNARE RUOLI
# @app.post("/assign-role-with-userid/", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
# async def assign_role_with_id(
#     user_id: int,
#     role_name: str,
#     db: Session = Depends(get_session_local),
#     user_repo: UserManagementRepository = Depends(UserManagementRepository)
# ):
#     return user_repo.upload_role_to_user_by_name(db, user_id, role_name)

# @app.post("/assign-role-by-username/", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
# async def assign_role_by_username(
#     username: str,
#     role_name: str,
#     db: Session = Depends(get_session_local),
#     user_repo: UserManagementRepository = Depends(UserManagementRepository)
# ):
#     user = user_repo.get_user_by_username(db, username)

#     if user:
#         if user.role_id:
#             # Aggiorna il ruolo esistente
#             user_repo.upload_role_to_user_by_name(db, user.id, role_name)
#             return {"message": "Ruolo aggiornato con successo"}

#         # Se l'utente non ha un ruolo, assegna il nuovo ruolo
#         user_repo.upload_role_to_user_by_name(db, user.id, role_name)
#         return {"message": "Ruolo assegnato con successo"}

#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f"Utente con username {username} non trovato",
#     )



# #####################################MICROSERVIZI

# # Funzione per registrare il microservizio presso il servizio di autenticazione
# def register_with_auth_service():  
#     auth_service_url = "http://authentication_service:8000/register_microservice"
#     service_name = "user_management"  # Sostituisci con il nome del tuo microservizio

#     response = requests.post(auth_service_url, json={"service_name": service_name})

#     if response.status_code == 200:
#         return "Microservice registered successfully with authentication service"
#     else:
#         raise HTTPException(
#             status_code=response.status_code,
#             detail="Failed to register with authentication service",
#         )

# #  endpoint ...
# ##########################GESTIONE UTENTE########################

# ##CREA ADMIN
# ##CREA ADMIN
# @app.post("/registration_admin", response_model=Utente)
# async def registration_admin(username: str, password: str, email: str,n_telefono:Optional[str], db: Session = Depends(get_session_local)):

#     # Verifica se il ruolo "admin" esiste
#     admin_role = user_repository.get_role_by_name(db, role_name="admin")
  
#     if not admin_role:
#         # Se non esiste, crea il ruolo
#         admin_role = user_repository.create_role(db, role_name="admin")

#     # Controllo se esiste già un utente con la stessa email
#     existing_user_by_email = user_repository.get_user_by_email(db, email)
#     if existing_user_by_email:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"User with email {email} already exists",
#         )

#     # Controllo se esiste già un utente con lo stesso username
#     existing_user_by_username = user_repository.get_user_by_username(db, username)
#     if existing_user_by_username:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"User with username {username} already exists",
#         )

#     # Procedi con la registrazione se entrambi i controlli passano
#     hashed_password = get_password_hash(password)
#     roleid = admin_role.id
#     user = user_repository.create_admin(db, username, email, hashed_password,roleid,n_telefono)
    

#     # Invia l'evento di creazione utente a Kafka
#     event_data = {"event_type": "user_created", "username": user.username}
#     producer.produce("user_events", value=str(event_data))

#     return user


# # API REGISTRA UTENTE 
# @router.post("/register_user", response_model=Utente)
# async def register_user(username: str, password: str, email: str,n_telefono:Optional[str], db: Session = Depends(get_session_local)):

#     # Controllo se esiste già un utente con la stessa email
#     existing_user_by_email = user_repository.get_user_by_email(db, email)
#     if existing_user_by_email:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"User with email {email} already exists",
#         )
        

#     # Controllo se esiste già un utente con lo stesso username
#     existing_user_by_username = user_repository.get_user_by_username(db, username)
#     if existing_user_by_username:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"User with username {username} already exists",
#         )

#     # Procedi con la registrazione se entrambi i controlli passano
#     hashed_password = get_password_hash(password)
#     base_user_role = user_repository.get_role_by_name(db, role_name="base_user")
#     role_id = base_user_role.id

#     user = user_repository.create_user(db, username, email, hashed_password,role_id, n_telefono)


#     # Assegna automaticamente il ruolo "user_base"
#     user_repository.assign_role_to_user_by_name(db, user.id, role_name="base_user")


#     # Invia l'evento di creazione utente a Kafka
#     event_data = {"event_type": "user_created", "username": user.username}
#     producer.produce("user_events", value=str(event_data))

#     return user
# ###########################API TEST GATAWAY##########
#    # request serve per passare qualcosa che non so nel caso volessi passare dati a questa api che genera una pagina html
# @app.get("/home", response_class=HTMLResponse)
# def get_home(current_user: Utente = Depends(get_current_user)):
#     print("DALL HTML FATTO MALISSIMO")
#     return templates.TemplateResponse("admin_profile.html", {"request": {"user": current_user}})

#     # return "ciaoooooooo"
# @app.get('/ciao')
# async def saluta():
#     return{"message":" CIAO DAL MICROSERVIZO USER_MANAGEMENT"}

# @app.get("/health")
# async def health():
#     return {"status": "ok"}     
# ###############################        



# @app.post("/handle_comment_submission")
# async def handle_comment_submission(event_data: dict):
#     # Esegui le operazioni necessarie per elaborare il commento
#     username = event_data.get("username", "")
#     product_id = event_data.get("product_id", "")
#     comment = event_data.get("comment", "")

#     # Aggiungi logica per gestire il commento
#     logging.info(f"Received comment for product {product_id} from user {username}: {comment}")
    
#     return {"message": "Comment handled successfully"}        

