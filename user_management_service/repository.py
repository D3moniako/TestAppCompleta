from sqlalchemy.orm import Session
from sqlmodel import select
from user_management_service.modelli import UserAuth, UserProfile
from typing import List

class UserManagementRepository:
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

    def create_user_profile(self, db: Session, profile: UserProfile) -> UserProfile:
        db_profile = UserProfile(**profile.dict())
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile