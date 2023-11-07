from typing import Optional
from typing import List
\
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String

class TokenData(SQLModel):###
    sub: str
#     scopes: List[str] = []

class UserRoleBase(SQLModel):
    role_name: str
# class UserRolesLink(SQLModel, table=True):
#     user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
#     role_id: int = Field(default=None, foreign_key="userrole.id", primary_key=True)
class UserRole(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(index=True, unique=True)

class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bio: str
    website: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    role_id: Optional[int] = Field(default=None, foreign_key="userrole.id")
    profile_id: Optional[int] = Field(default=None, foreign_key="userprofile.id")

class UserAuth(SQLModel, table=True):
    id: Optional[int]= Field(default=None,primary_key=True)
    username: str
    password: str
    roles_id: Optional[int] = Field(default=None, foreign_key="userrole.id")
    profile_id: Optional[int] = Field(default=None, foreign_key="userprofile.id")


class UserBase(SQLModel):
    username: str
    email: str
    hashed_password: str


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
