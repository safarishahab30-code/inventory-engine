from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from inventory_core.models.product import Product
from inventory_core.schemas.product import ProductCreate, ProductUpdate
from inventory_core.crud.base import CRUDBase

# --- توابع کمکی پایه ---

def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()

def get_all_products(db: Session):
    return db.query(Product).all()

def create_product(db: Session, product: ProductCreate) -> Product:
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

def advanced_search_products(
    db: Session,
    name: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
):
    """منطق کوئری جستجوی پیشرفته در دیتابیس"""
    query = db.query(Product)

    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if in_stock is True:
        query = query.filter(Product.quantity > 0)
    elif in_stock is False:
        query = query.filter(Product.quantity == 0)

    return query.all()

def get_inventory_summary(db: Session, low_stock_threshold: int = 5):
    stats = db.query(
        func.count(Product.id).label("total_products"),
        func.coalesce(func.sum(Product.quantity), 0).label("total_stock"),
        func.coalesce(func.sum(Product.quantity * Product.price), 0).label("total_value"),
    ).first()

    low_stock_products = db.query(Product).filter(
        Product.quantity <= low_stock_threshold
    ).all()

    return {
        "total_products": stats.total_products or 0,
        "total_stock": stats.total_stock or 0,
        "total_value": stats.total_value or 0,
        "low_stock_count": len(low_stock_products),
        "low_stock_products": low_stock_products,
    }

# --- کلاس CRUD ---

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def increase_stock(self, db: Session, product_id: int, amount: int):
        p = get_product(db, product_id)
        if p:
            p.quantity = (p.quantity or 0) + amount
            db.commit()
            db.refresh(p)
            return p
        return None

    def record_sale(self, db: Session, product_id: int, amount: int):
        p = get_product(db, product_id)
        if p and (p.quantity or 0) >= amount:
            p.quantity -= amount
            db.commit()
            db.refresh(p)
            return True
        return False

    def create(self, db: Session, *, obj_in: ProductCreate) -> Product:
        return create_product(db, obj_in)

    def get_inventory_summary(self, db: Session, low_stock_threshold: int = 5):
        return get_inventory_summary(db, low_stock_threshold=low_stock_threshold)

    def advanced_search(self, db: Session, **kwargs):
        return advanced_search_products(db, **kwargs)

# نمونه سراسری
product_crud = CRUDProduct(Product)
