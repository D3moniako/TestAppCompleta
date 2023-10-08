# comments_models.py
from typing import List
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str

class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str
    price: int
    tags: List["ProductTag"] = Field(sa_relationship="ProductTag", back_populates="product")
    reviews: List["Review"] = Field(sa_relationship="Review", back_populates="product")

class Tag(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    products: List["ProductTag"] = Field(sa_relationship="ProductTag", back_populates="tag")

class ProductTag(SQLModel, table=True):
    product_id: int = Field(foreign_key="product.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)
    product: Product = Field(sa_relationship="Product", back_populates="tags")
    tag: Tag = Field(sa_relationship="Tag", back_populates="products")

class Review(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    stars: int
    comment: str
    user: User = Field(sa_relationship="User", back_populates="reviews")
    product: Product = Field(sa_relationship="Product", back_populates="reviews")
