from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from repository import SecurityRepository, UserManagementRepository
from jose import JWTError, jwt
from db.modelli import TokenData, Utente,UserRole
from db.engine import get_engine, get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security_repository = SecurityRepository()
engine = get_engine()

# Funzione per ottenere la sessione locale
def get_session_local():
    engine = get_db()
    return Session(bind=engine)

class RoleMiddleware:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_session_local)):
        try:
            payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
            print("Token payload:", payload)  # Stampa il payload per debug

            username: str = payload.get("sub")
            print("lo username è questo : ", username)
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Cambia questa riga
            user = db.query(Utente).filter(Utente.username == username).first()
            print(f"Ecco la query al database di User:  {user}")
            print(f"Username: {user.username}")
            print(f"Role: {user.role}")

            if user:
                user_role = user.role.role_name
                if user_role not in self.allowed_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You do not have access to this resource",
                    )
                print(f"User {username} has role: {user_role}, allowed roles: {self.allowed_roles}")
                return user
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            print(f"Error during role validation: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
def get_current_user(token: str = Depends(SecurityRepository().verify_token)):
    return token