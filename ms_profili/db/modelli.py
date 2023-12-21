from typing import Optional
 from typing import List
from sqlmodel import SQLModel, Field, Column,Relationship
from sqlalchemy import String, null, table
# from sqlmodel import  HttpUrl

from datetime import datetime


class Profile(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    first_name: Optional[str] =Field(default=None,nullable=True)
    second_name: Optional[str] =Field(default=None,nullable=True)
    hobby: Optional[str] =Field(default=None,nullable=False)
    music : Optional[List[str]] =Field(default=None,nullable=True)
    sport: Optional[List[str]] =Field(default=None,nullable=True)
    bio: str =Field(default=None,nullable=False)   # biografia
    user_id: int =Field(default=None,nullable=False)  # Foreign key l'utente associato
    website: str
        
class ProfileBase(SQLModel):
    first_name: Optional[str] = Field(default=None, nullable=True)
    second_name: Optional[str] = Field(default=None, nullable=True)
    hobby: Optional[str] =Field(default=None,nullable=True)
    music : Optional[List[str]] =Field(default=None,nullable=True)
    sport: Optional[List[str]] =Field(default=None,nullable=True)
    bio: str =Field(default=None,nullable=True)   # biografia
# dovrei usare lo user ma d'ora in poi meglio se lavoro solo con 
# il profilo
###########################TRACCIAMENMTO STATISTICHE###############################
class ProfileAccess(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    access_date: datetime.datetime = datetime.now()
    
    
    
class MusicPreferences(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    music_genre: str

class SportPreferences(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    favorite_sport: str
    
    
################################Immagini DB ###########################
class Image(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    name: str = Field(unique=True, nullable=False)
    url: HttpUrl = Field(default=None, nullable=False)
    state: int = Field(default=None, nullable=True)
    creation_date: datetime.datetime = datetime.now()
    source: str  # Può essere 'server' o 'db' per indicare la fonte dell'immagine

#######################àà
    
    
    
# class UserProfileBase(SQLModel):
#     bio: str
#     website: str



# ######dto
# class UserRead(UserBase):
#     id: int

# class UserCreate(UserBase):
#     pass

# class UserUpdate(SQLModel):
#     username: Optional[str] = None
#     email: Optional[str] = None
#     hashed_password: Optional[str] = None

# class UserReadwithProfile(UserRead):
#     profile: Optional["UserProfile"] = None
