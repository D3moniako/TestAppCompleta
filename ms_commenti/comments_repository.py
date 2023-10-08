# comments_repository.py
from sqlmodel import Session, select
from .comments_models import Review, User, Product
from .event_handler import publish_review_created_event

class ReviewRepository:
    def create_review(self, db: Session, review: Review) -> Review:
        db_review = Review(**review.dict())
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        
        # Pubblica un evento Kafka quando una nuova recensione è stata creata
        publish_review_created_event(db_review)
        
        return db_review

    def get_reviews_for_product(self, db: Session, product_id: int) -> List[Review]:
        reviews = db.exec(select(Review).filter(Review.product_id == product_id)).all()
        return reviews
