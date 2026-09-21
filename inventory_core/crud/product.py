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

def advanced_search_products(db: Session, query: str = None, category_id: int = None):
    q = db.query(Product)
    if query:
        q = q.filter(Product.name.ilike(f"%{query}%"))
    if category_id is not None:
        q = q.filter(Product.category_id == category_id)
    return q.all()
def adjust_product_stock(db: Session, product_id: int, amount: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError("محصول یافت نشد.")
    
    new_quantity = product.quantity + amount
    if new_quantity < 0:
        raise ValueError(f"موجودی ناکافی است. موجودی فعلی: {product.quantity}")
    
    product.quantity = new_quantity
    db.commit()
    db.refresh(product)
    return product
def get_low_stock_products(session: Session, threshold: int = 5) -> list[Product]:
    """دریافت لیست کالاهایی که موجودی آن‌ها کمتر یا مساوی آستانه مشخص است"""
    return session.query(Product).filter(Product.quantity <= threshold).all()