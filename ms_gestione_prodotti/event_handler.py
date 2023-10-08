# repository.py
from sqlmodel import Session, select
from .models import Product, ProductBase
from .event_handler import publish_product_created_event

class ProductRepository:
    def create_product(self, db: Session, product: ProductBase) -> Product:
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        # Pubblica un evento Kafka quando un nuovo prodotto è stato creato
        publish_product_created_event(db_product)
        
        return db_product

    def get_all_products(self, db: Session) -> List[Product]:
        products = db.exec(select(Product)).all()
        return products
