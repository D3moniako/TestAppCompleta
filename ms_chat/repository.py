# repository.py
# repository.py
from sqlmodel import Session, select
from .models import Chat, Message

class ChatRepository:
    def create_chat(self, db: Session, participant1_id: str, participant2_id: int) -> Chat:
        chat = Chat(participant1_id=participant1_id, participant2_id=participant2_id)
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    def get_all_chats(self, db: Session) -> List[Chat]:
        chats = db.exec(select(Chat)).all()
        return chats

    def get_chat_by_id(self, db: Session, chat_id: int) -> Chat:
        chat = db.get(Chat, chat_id)
        return chat

class MessageRepository:
    def create_message(self, db: Session, chat_id: int, sender_id: str, content: str) -> Message:
        message = Message(chat_id=chat_id, sender_id=sender_id, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_messages_by_chat_id(self, db: Session, chat_id: int) -> List[Message]:
        messages = db.exec(select(Message).where(Message.chat_id == chat_id)).all()
        return messages
