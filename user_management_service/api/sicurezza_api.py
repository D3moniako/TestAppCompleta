# user_management_service/api/security_api.py

# import logging
import bcrypt
import jwt
import requests
from fastapi import APIRouter, Depends, HTTPException, status, Query,Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from repository import UserManagementRepository, SecurityRepository
from middleware import RoleMiddleware  # Corretto l'import per get_session_local
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from db.modelli import Utente
from db.engine import get_engine,get_db
from convalida.email_manager import convalida_via_email,send_password_reset_email,cancella_via_email
from typing import Optional
from datetime import datetime, timedelta


#### INCLUDO ROTTE #####
router = APIRouter()


engine = get_engine()
# Funzione per ottenere la sessione locale

def get_session_local():
    engine = get_db()
    return Session(bind=engine)  # Cambia questa riga



# SessionLocal è ora una funzione invece di un'istanza
SessionLocal = get_session_local()
# Inizializza i repository e il middleware

user_repository = UserManagementRepository()
security_repository = SecurityRepository()  # Aggiunto l'invocazione della classe
role_middleware = RoleMiddleware

# Configura lo schema di autenticazione OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="security/token")
######################### FUNZIONI SICUREZZA#############################

# Funzione per ottenere l'hash della password
def get_password_hash(password: str):      
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")
### ottieni dal token utente attuale
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session_local)):
    return get_user_from_token(token, db)

# Funzione per creare un token JWT
def create_jwt_token(data: dict):
    to_encode = data.copy()
    return jwt.encode(to_encode, "SECRET_KEY", algorithm="HS256")

# Funzione per registrare il microservizio presso il servizio di autenticazione
def register_with_auth_service():  
    auth_service_url = "http://authentication_service:8000/register_microservice"
    service_name = "user_management"  # Sostituisci con il nome del tuo microservizio

    response = requests.post(auth_service_url, json={"service_name": service_name})

    if response.status_code == 200:
        return "Microservice registered successfully with authentication service"
    raise HTTPException(
        status_code=response.status_code,
        detail="Failed to register with authentication service",
    )
######################### API TOKEN ###################
# API per ottenere un token di accesso
@router.post("/token")
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
        print(f"DA GETUSERFROMTOKEN ECCO IL PAYLOAD :{payload}")
        username: str = payload.get("sub")
        print(f"DA GETUSERFROMTOKEN ecco USERNAME DAL TOKEN :{username}")
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    # Ottieni l'utente dal repository o dal database
    user = security_repository.get_user_by_username(db, username)
    print(" USER DAL REPOSITORY")
    if user is None:
        raise credentials_exception

    return user

#### resetta  token
def regenerate_token( username: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": username}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = create_jwt_token(to_encode)  # Usa la funzione esistente per creare il token JWT
    return encoded_jwt




# Questo sarebbe l'endpoint per la conferma dell'account
@router.get("/conferma_account")
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
            redirect_url = f"http://localhost:8000/routes/home?token={token}"
            response = RedirectResponse(url=redirect_url, status_code=303)
            return response
        # return {"message": f"Account di {username} confermato con successo"}   
    else:
        raise HTTPException(status_code=400, detail="Token non valido")

# API per eliminare l'utente corrente
@router.delete("/delete_current_user")
async def delete_current_user(
    current_user: Utente = Depends(get_current_user),
    db: Session = Depends(get_session_local)
):
    try:
        print("CIAO DAL TRY DI DELETE CURRENT USER")
        print(f"utente corrente dal cancella utente corrente {current_user.username}")
        user_repository.delete_user_by_name(db, username=current_user.username)

        message = f"Gentile signor/a {current_user.username.lower().title()}, il suo account è stato cancellato con successo. Torni a trovarci."
        # Invia conferma via email
        confirmation_email_sent = cancella_via_email(user=current_user, messaggio=message)

        if confirmation_email_sent:
            return {"message": "Utente cancellato con successo. Conferma inviata via email."}
        else:
            return {"message": "Utente cancellato con successo. Errore nell'invio della conferma via email."}
    except HTTPException as e:
        # Gestisci eventuali eccezioni durante la cancellazione dell'utente
        return {"error": str(e)}

#####
# API per ottenere l'utente corrente dal token
@router.get("/users/me", response_model=Utente)
async def read_users_me(current_user: Utente = Depends(get_user_from_token)):
    # convalida_via_email(current_user)
    return current_user

        
# manda_email con token per rignerare password
@router.post("/request_password_reset")
async def request_password_reset(email: str, db: Session = Depends(get_session_local)):
    user = user_repository.get_user_by_email(db, email)
    
    if user:
        # Genera un token per il ripristino della password e invia un'email
        reset_token = regenerate_token(username=user.username)
        reset_url = f"http://localhost:8000"
        
        if send_password_reset_email(user, reset_url, reset_token):
            return {"message": f"Email reset password inviata con successo!!!"}   
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f" Impossibile mandare l'email c'è stato un errore durante l'invio dell'email",
            )
       
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Impossibile mandare l'email non è stata trovata nessun utente associato all'email: {email} nel nostro db",
        )
# Funzione per reimpostare la password
# Funzione per reimpostare la password
@router.post("/reset_password")
async def reset_password(
    email: str = Query(..., description="Email associata all'account"),
    token: str = Query(..., description="Token di reset della password"),
    new_password: str = Query(..., description="Nuova password"),
    db: Session = Depends(get_session_local),
    security_repo: SecurityRepository = Depends()
):
    # Verifica il token utilizzando la tua funzione verify_token
    token_data = security_repo.verify_token(token)

    # Ottieni l'utente utilizzando l'email
    user = user_repository.get_user_by_email(db, email)

    # Verifica che l'utente esista e che l'utente associato al token coincida con l'utente trovato dall'email
    if user and user.username == token_data.sub:
        # Resetta la password dell'utente
        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password
        db.commit()

        # Aggiorna il token se necessario (ad esempio, per invalidare il token precedente)
        reset_token = regenerate_token(username=user.username, expires_delta=timedelta(minutes=30))


        return {"message": "Password resettata con successo"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido per l'utente specificato",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        
        
# Modifica l'API di logout
@router.post("/logout")
async def logout_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session_local), 
                      security_repo: SecurityRepository = Depends(),
                      user_repo: UserManagementRepository = Depends(),
                      ):
    try:
        # Verifica il token
        token_data = security_repo.verify_token(token)
        
        # Esegui le operazioni di logout utilizzando la repository
        # Nota: Puoi utilizzare token_data.sub per ottenere l'username dell'utente
        user_repo.logout_user(db, token_data.sub)

        return {"message": "Logout effettuato con successo"}
    except HTTPException as e:
        # Gestisci eventuali eccezioni durante la verifica del token
        return {"error": str(e)}
        