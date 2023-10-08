# security_service/repository.py

from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .models_auth import TokenData, UserAuth, UserProfile,RegisteredMicroservice
from fastapi import Depends, HTTPException, status
import bcrypt

class SecurityRepository:
    def verify_token(self, token: str) -> TokenData:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            return TokenData(username=username)
        except JWTError:
            raise credentials_exception
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def is_microservice_registered(self, db: Session, service_name: str) -> bool:
        return db.query(RegisteredMicroservice).filter_by(service_name=service_name).first() is not None

    def register_microservice(self, db: Session, service_name: str):
        db_microservice = RegisteredMicroservice(service_name=service_name)
        db.add(db_microservice)
        db.commit()
        db.refresh(db_microservice)
