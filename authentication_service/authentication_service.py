# Nel tuo file principale service_auth.py (ex. main.py)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .repository_auth import UserRepository
from .models_auth import UserAuth, UserRole, MicroserviceRegistrationRequest, TokenData
from .middleware import RoleMiddleware
from .database import get_db
from typing import List
from fastapi.responses import JSONResponse
import bcrypt
from starlette.middleware.trustedhost import TrustedHostMiddleware
from scripts.config import eureka_config
from fastapi import FastAPI


app = FastAPI()

# Configura Eureka Client
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In produzione, specifica gli host consentiti
)

app.eureka_config = eureka_config
router = APIRouter()
user_repository = UserRepository()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Funzione per ottenere l'hash della password
def get_password_hash(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

# Funzione per creare un token JWT
def create_jwt_token(data: dict):
    to_encode = data.copy()
    return jwt.encode(to_encode, "SECRET_KEY", algorithm="HS256")

# Funzione per ottenere l'utente corrente
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


@router.post("/register_microservice", response_model=JSONResponse)
def register_microservice(request_data: MicroserviceRegistrationRequest, db: Session = Depends(get_db)):
    service_name = request_data.service_name

    # Controlla se il microservizio è già registrato nel database
    if user_repository.is_microservice_registered(db, service_name):
        raise HTTPException(status_code=400, detail="Microservice already registered")

    # Se non è registrato, procedi con la registrazione
    user_repository.register_microservice(db, service_name)
    return JSONResponse(content={"message": "Microservice registered successfully"}, status_code=200)


@router.post("/users/", response_model=UserAuth)
async def create_user(username: str, email: str, password: str, roles: List[str], db: Session = Depends(get_db)):
    hashed_password = get_password_hash(password)
    return user_repository.create_user(db, username, email, hashed_password, roles)


@router.post("/roles/", response_model=UserRole)
async def create_role(
    role_name: str,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(RoleMiddleware())
):
    # Verifica se l'utente corrente ha il ruolo di "admin" tramite il middleware
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to create a new role",
        )

    # Continua con la logica per la creazione di un nuovo ruolo
    return user_repository.create_role(db, role_name)


@router.post("/users/{user_id}/roles/{role_id}")
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(RoleMiddleware())
):
    # Verifica se l'utente corrente ha il ruolo di "admin" tramite il middleware
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to assign roles to users",
        )

    # Continua con la logica per l'assegnazione del ruolo all'utente
    return user_repository.assign_role_to_user(db, user_id, role_id)


@router.get("/users/me", response_model=UserAuth)
async def read_users_me(current_user: UserAuth = Depends(get_current_user)):
    return current_user
