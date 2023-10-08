# models.py

from typing import List
from sqlmodel import SQLModel, Field, create_engine, Session
from .decorators import relationship

DATABASE_URL = "postgresql://user:password@localhost/db_name"
engine = create_engine(DATABASE_URL)

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    cart: List["CartItem"] = relationship(sa_relationship="CartItem", back_populates="user")

class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str
    price: int
    tags: List["ProductTag"] = relationship(sa_relationship="ProductTag", back_populates="product")
    reviews: List["Review"] = relationship(sa_relationship="Review", back_populates="product")

class Tag(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    products: List["ProductTag"] = relationship(sa_relationship="ProductTag", back_populates="tag")

class ProductTag(SQLModel, table=True):
    product_id: int = Field(foreign_key="product.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)
    product: Product = relationship(sa_relationship="Product", back_populates="tags")
    tag: Tag = relationship(sa_relationship="Tag", back_populates="products")

class Review(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    stars: int
    user: User = relationship(sa_relationship="User", back_populates="reviews")
    product: Product = relationship(sa_relationship="Product", back_populates="reviews")
