from sqlalchemy import select
from sqlmodel import Session, select
from .models import  User, UserProfile
from .models_auth import UserAuth, UserRole, UserProduct,RegisteredMicroservice

from typing import List

class UserRepository:
    def create_user(self, db: Session, username: str, email: str, hashed_password: str) -> UserAuth:
        user = UserAuth(username=username, email=email, hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def get_user(self, db: Session, user_id: int) -> UserAuth:
        return db.get(UserAuth, user_id)

    def get_all_users(self, db: Session) -> List[UserAuth]:
        users = db.execute(select(UserAuth)).all()
        return users

    def get_user_products(self, db: Session, user_id: int) -> List[UserProduct]:
        # Implementa la logica per ottenere i prodotti associati a un utente
        pass
    
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

    def get_user_by_username(self, db: Session, username: str) -> UserAuth:
        return db.query(UserAuth).filter(UserAuth.username == username).first()
    def create_user(self, db: Session, user: User) -> User:
        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_user_by_username(self, db: Session, username: str) -> User:
        return db.exec(select(User).where(User.username == username)).first()

    def create_user_profile(self, db: Session, profile: UserProfile) -> UserProfile:
        db_profile = UserProfile(**profile.dict())
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    
    def is_microservice_registered(self, db: Session, service_name: str) -> bool:
        return db.query(RegisteredMicroservice).filter_by(service_name=service_name).first() is not None

    def register_microservice(self, db: Session, service_name: str):
        db_microservice = RegisteredMicroservice(service_name=service_name)
        db.add(db_microservice)
        db.commit()
        db.refresh(db_microservice)