# security_service/models_auth.py

from sqlmodel import SQLModel, Field
from typing import List

class UserProfile(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    bio: str
    website: str

class UserAuth(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    roles: List[str] = Field(default=[])
    profile: UserProfile = Field(default=None, sa_relation="UserProfile", back_populates="user")

class TokenData(SQLModel):
    username: str
    
class RegisteredMicroservice(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    service_name: str