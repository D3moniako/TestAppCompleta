# models.py
from sqlmodel import SQLModel, Field, create_engine, Session

DATABASE_URL = "postgresql://user:password@localhost/db_name"
engine = create_engine(DATABASE_URL)

class Chat(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    participant1_id: str
    participant2_id: int
    messages: List["Message"] = Field(sa_relation="Message", back_populates="chat")

class Message(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chat.id")
    sender_id: str
    content: str
    chat: Chat = Field(sa_relation="Chat", back_populates="messages")
