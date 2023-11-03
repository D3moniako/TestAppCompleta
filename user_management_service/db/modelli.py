from sqlmodel import SQLModel, Field, Relationship, ForeignKey
from typing import List

class TokenData(SQLModel):
    sub: str
    scopes: List[str] = []

class UserRole(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    role_name: str
    users: List["User"] = Relationship(back_populates="role")
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    profile: "UserProfile" = Relationship(back_populates="user")
    role: "UserRole" = Relationship(back_populates="users")
    role_id: int = Field(default=None, foreign_key="userrole.id")

class UserProfile(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    bio: str
    website: str
    user: "User" = Relationship(back_populates="profile")
    user_auth: "UserAuth" = Relationship(back_populates="profile")


    
class UserAuth(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    role_id: int = Field(default=None, foreign_key="userrole.id")
    profile: "UserProfile" = Relationship(back_populates="user_auth")
