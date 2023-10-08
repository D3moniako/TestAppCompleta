# security_service/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from jose import JWTError, jwt
from .repository import SecurityRepository
from .models_auth import TokenData, User
from .database import get_db, OAuth2PasswordBearer
from starlette.middleware.trustedhost import TrustedHostMiddleware
from scripts.config import eureka_config
import bcrypt

app = FastAPI()

# Configura Eureka Client
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In produzione, specifica gli host consentiti
)

app.eureka_config = eureka_config
router = APIRouter()
security_repository = SecurityRepository()

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

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = security_repository.authenticate_user(form_data.username, form_data.password)
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
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(security_repository.get_current_user)):
    return current_user

@router.post("/register_user", response_model=User)
async def register_user(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(password)
    return security_repository.create_user(db, username, hashed_password)

@router.get("/secure-endpoint/", response_model=dict)
async def secure_endpoint(current_user: TokenData = Depends(security_repository.get_current_user)):
    user = security_repository.get_user_by_username(current_user.username)
    return {"message": "This is a secure endpoint!", "username": user.username, "email": user.email}

app.include_router(router)
# Esegui l'app FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8500)