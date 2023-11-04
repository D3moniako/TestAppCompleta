from typing import List
from sqlmodel import SQLModel, Field, Relationship

class TokenData(SQLModel):
    sub: str
    scopes: List[str] = []

class User(SQLModel):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    role_id: int
    profile: "UserProfile"  # Rimuovi l'assegnazione iniziale
    role: "UserRole" = Relationship(back_populates="users")

class UserProfile(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    bio: str
    website: str
    user: User = Relationship(back_populates="profile")

class UserAuth(SQLModel):
    id: int
    username: str
    email: str
    hashed_password: str
    roles: List["UserRole"] = Relationship(back_populates="user")

class UserRole(SQLModel):
    id: int = Field(default=None, primary_key=True)
    role_name: str
    users: List[User] = Relationship(back_populates="role")

class RegisteredMicroservice(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    service_name: str
