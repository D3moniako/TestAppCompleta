from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy.orm import relationship
from datetime import datetime
DATABASE_URL = "postgresql://user:password@localhost/db_name"
engine = create_engine(DATABASE_URL)

# Aggiungi questi modelli alla tua implementazione esistente
class UserProfile(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    bio: str
    website: str

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    roles: List[str] = Field(default=[])
    profile: UserProfile = Field(default=None, sa_relation="UserProfile", back_populates="user")

class TokenData(SQLModel):
    username: str
    
  