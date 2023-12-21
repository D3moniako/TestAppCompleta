from typing import Optional
from typing import List
from sqlmodel import SQLModel, Field, Column,Relationship
from sqlalchemy import String, null

class TokenData(SQLModel):###
    sub: str
#     scopes: List[str] = []



class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bio: str
    website: str
    utente_id: Optional[int] = Field(default=None, foreign_key="utente.id")
class UserRole(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(index=True, unique=True)
    # utente: List["Utente"] = Relationship(back_populates="roles") #molti a molti
    users: List["Utente"] = Relationship(back_populates="role")

class Utente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(default=None,nullable=False,unique=True)
    hashed_password: str =Field(default=None,nullable=False)
    status: int = Field(default=0,nullable=False)
    n_telefono: Optional[str] = Field(default=None,nullable=True,unique=True)
    role_id: Optional[int] = Field(default=None, foreign_key="userrole.id")
    #FIGHISSIMO POSSO GESTIRE LE RELAZIONI TRA TABELLE ANCHE SE SONO SU DUE MICROSERVIZI DIFFERENTI 
    profile_id: Optional[int] = Field(default=None, foreign_key="ms_profile.profile.id")
     # Aggiungi questa relazione per ottenere i ruoli di un utente
    role: UserRole = Relationship(back_populates="users")
   
    # roles: List["UserRole"] = Relationship(back_populates="utente") molti a molti

class UserAuth(SQLModel, table=True):
    id: Optional[int]= Field(default=None,primary_key=True)
    username: str =Field(default=None,nullable=False,unique=True)
    password: str =Field(default=None,nullable=False)
    roles_id: Optional[int] = Field(default=None, foreign_key="userrole.id")
    profile_id: Optional[int] = Field(default=None, foreign_key="userprofile.id")

#################################################################
class UtenteBase(SQLModel):
    username: str
    email: str
    hashed_password: str

class UserRoleBase(SQLModel):
    role_name: str
# class UserRolesLink(SQLModel, table=True):
#     user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
#     role_id: int = Field(default=None, foreign_key="userrole.id", primary_key=True)
class UserProfileBase(SQLModel):
    bio: str
    website: str


    # roles: List[str]  # Utilizza List[str] o un altro tipo supportato da SQLAlchemy

class RegisteredMicroservice(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    service_name: str

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
