# repository.py
from sqlmodel import Session, select
from .models import Product, ProductBase
from .dtos import ProductCreate, ProductRead

class ProductRepository:
    def create_product(self, db: Session, product: ProductCreate) -> ProductRead:
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    def get_all_products(self, db: Session) -> List[ProductRead]:
        products = db.exec(select(Product)).all()
        return products
