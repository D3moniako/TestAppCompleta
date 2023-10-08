# auth.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .repository_auth import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
user_repository = UserRepository()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # La tua implementazione per ottenere l'utente corrente

def check_user_role(required_role: str = None, current_user: str = Depends(get_current_user)):
    user = user_repository.get_user_by_username(db, current_user)
    
    if required_role and user.role != required_role:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return user
