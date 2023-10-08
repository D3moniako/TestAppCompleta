# event_handler.py
from sqlmodel import SQLModel
from .models import Chat
from kafka import KafkaProducer

kafka_bootstrap_servers = 'your_kafka_bootstrap_servers'
producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)

def publish_chat_created_event(chat: Chat):
    event_data = {
        "event_type": "chat_created",
        "chat_id": chat.id,
        "participant1_id": chat.participant1_id,
        "participant2_id": chat.participant2_id,
    }
    producer.send("chat_events", value=event_data)
