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
class UserRolesLink(SQLModel, table=True):
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: int = Field(default=None, foreign_key="userrole.id", primary_key=True)

class UserRole(UserRoleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(sa_column=Column("role_name", String, unique=True))
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRolesLink)

class UserBase(SQLModel):
    username: str
    email: str
    hashed_password: str
    roles: List[UserRole] = Relationship(back_populates="users", link_model=UserRolesLink)
    profile: Optional["UserProfile"] = Relationship(back_populates="user")

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column("username", String, unique=True))
    roles: List[UserRole] = Relationship(back_populates="users", link_model=UserRolesLink)

class UserProfileBase(SQLModel):
    user_id: int
    bio: str
    website: str

class UserProfile(UserProfileBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bio: str
    website: str
    user: User = Relationship(back_populates="profile")


class UserAuth(SQLModel, table=True):
    id: Optional[int]= Field(default=None,primary_key=True)
    username: str
    password: str
    # roles: List[UserRole] = Relationship(back_populates="users", link_model=UserRolesLink)

    # roles: List[str]  # Utilizza List[str] o un altro tipo supportato da SQLAlchemy

class RegisteredMicroservice(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    service_name: str

######dto
class UserRead(UserBase):
    id: int

class UserCreate(UserBase):
    pass

class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    hashed_password: Optional[str] = None

class UserReadwithProfile(UserRead):
    profile: Optional["UserProfile"] = None
