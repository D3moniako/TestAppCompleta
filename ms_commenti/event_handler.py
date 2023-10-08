# event_handler.py
from sqlmodel import SQLModel
from .comments_models import Review
from kafka import KafkaProducer

kafka_bootstrap_servers = 'your_kafka_bootstrap_servers'
producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)

def publish_review_created_event(review: Review):
    event_data = {
        "event_type": "review_created",
        "review_id": review.id,
        "product_id": review.product_id,
        "stars": review.stars,
    }
    producer.send("review_events", value=event_data)
