# ms_chat/dtos.py
from typing import List
from pydantic import BaseModel

class MessageDTO(BaseModel):
    content: str

class ChatCreate(BaseModel):
    participant2_id: int

class ChatDTO(BaseModel):
    participant1_id: int
    participant2_id: int
    messages: List[MessageDTO] = []
