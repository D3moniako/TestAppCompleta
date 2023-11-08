from sqlalchemy.orm import Session
from sqlmodel import select
from typing import List,Optional
from db.modelli import UserAuth, Utente, UserProfile, UserRole, TokenData, RegisteredMicroservice

from jose import JWTError,jwt
from fastapi import Depends, HTTPException, status
import bcrypt

class UserManagementRepository:
    
    ###
    def create_user_auth(self, db: Session, username: str, email: str, hashed_password: str) -> UserAuth:
        utente_auth = UserAuth(username=username, email=email, hashed_password=hashed_password)
        db.add(utente_auth)
        db.commit()
        db.refresh(utente_auth)
        return utente_auth

    
    ###
    def create_user(self, db: Session, username: str, email: str, hashed_password: str) -> Utente:
        try:
            utente = Utente(username=username, email=email, hashed_password=hashed_password)
            db.add(utente)
            db.commit()
            db.refresh(utente)
            return utente
        except Exception as e:
            print(f"ERRORE NELLA CREAZIONE DELL 'UTENTE: {e}")
            db.rollback()
            # Gestisci l'eccezione o loggala in modo appropriato
            return None

    ###
    
    

    def get_user(self, db: Session, user_id: int) -> UserAuth:
        return db.get(UserAuth, user_id)

    def get_all_users(self, db: Session) -> List[UserAuth]:
        users = db.execute(select(UserAuth)).all()
        return users

    def create_user_profile(self, db: Session, profile: UserProfile) -> UserProfile:
        db_profile = UserProfile(**profile.dict())
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    #######################################
    def create_role(self, db: Session, role_name: str) -> UserRole:
        role = UserRole(name=role_name)
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    def assign_role_to_user(self, db: Session, user_id: int, role_id: int):
        user = db.get(UserAuth, user_id)
        role = db.get(UserRole, role_id)
        user.roles.append(role)
        db.commit()
        db.refresh(user)
    ################################################################
   
   
    def get_user_by_username(self, db: Session, username: str) -> Utente:
        return db.execute(select(Utente).where(Utente.username == username)).first()

    
    ########################################################################        
##NON SO SE FUNZIONA CONTROLLARE!!!

####
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
    
    def get_user_auth_by_username(self, db: Session, username: str) -> UserAuth:
        return db.query(UserAuth).filter(UserAuth.username == username).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Utente:
        # return db.execute(select(Utente).where(Utente.username == username)).first() #SINTASSI VECCHIA
        return db.query(Utente).filter(Utente.username == username).first() ## SINTASSI DIRETTA NUOVA

    
    def is_microservice_registered(self, db: Session, service_name: str) -> bool:
        return db.query(RegisteredMicroservice).filter_by(service_name=service_name).first() is not None
    ##########
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[Utente]: # cambiato da UserAuth
        user = self.get_user_by_username(db, username)
        if user and self.verify_password(password, user.hashed_password):
            return user
        return None
    
    #########
    def register_microservice(self, db: Session, service_name: str):
        db_microservice = RegisteredMicroservice(service_name=service_name)
        db.add(db_microservice)
        db.commit()
        db.refresh(db_microservice)
