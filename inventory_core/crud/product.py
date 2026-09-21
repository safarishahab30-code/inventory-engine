from sqlalchemy.orm import Session
from inventory_core.models.product import Product
from inventory_core.schemas.product import ProductCreate, ProductUpdate
def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_update: ProductUpdate):
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False
def get_all_products(db: Session):
    return db.query(Product).all()
def update_product(db: Session, product_id: int, name: str = None, price: float = None, category: str = None):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    
    if name is not None:
        product.name = name
    if price is not None:
        product.price = price
    if category is not None:
        product.category = category

    db.commit()
    db.refresh(product)
    return product
def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return False
    
    db.delete(product)
    db.commit()
    return True

