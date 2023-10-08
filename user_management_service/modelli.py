# user_management_service/models.py

from sqlmodel import SQLModel, Field
from typing import List

class TokenData(SQLModel):
    sub: str  # Soggetto del token (solitamente l'username o l'ID dell'utente)
    scopes: List[str] = []  # Elenco degli ambiti/permessi associati al token

    # Altri campi opzionali che potresti voler includere:
    # exp: int  # Scadenza del token (timestamp UNIX)
    # iss: str  # Emittente del token
    # alti campi che ritieni necessari per il tuo caso d'uso

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
    # profile: "UserProfile" = Field(default=None, foreign_key="userprofile.id")  

    
class UserAuth(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    roles: List[str] = Field(default=[])
    # profile: "UserProfile" = Field(default=None, foreign_key="userprofile.id")
