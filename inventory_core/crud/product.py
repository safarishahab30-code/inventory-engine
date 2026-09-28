from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from inventory_core.models.product import Product
from inventory_core.schemas.product import ProductCreate, ProductUpdate
from inventory_core.crud.base import CRUDBase

# --- توابع کمکی ---

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

def run_advanced_search(session):
    """واسط کاربری برای جستجوی پیشرفته."""
    console.print(farsi("[bold blue]جستجوی پیشرفته - مقادیر غیرضروری را خالی رها کنید (Enter بزنید).[/bold blue]"))
    
    name = get_safe_input(farsi("نام کالا"))
    category = get_safe_input(farsi("دسته‌بندی"))
    min_price_str = get_safe_input(farsi("حداقل قیمت"))
    max_price_str = get_safe_input(farsi("حداکثر قیمت"))
    
    # تبدیل ایمن قیمت‌ها
    min_price = float(min_price_str) if min_price_str and min_price_str.replace('.','',1).isdigit() else None
    max_price = float(max_price_str) if max_price_str and max_price_str.replace('.','',1).isdigit() else None

    # فراخوانی تابع اصلی
    results = advanced_search_products(
        session, 
        name=name, 
        category=category, 
        min_price=min_price, 
        max_price=max_price
    )

    if not results:
        console.print(farsi("[yellow]محصولی با این شرایط یافت نشد.[/yellow]"))
        return

    # نمایش در جدول
    table = Table(title=farsi("نتایج جستجوی پیشرفته"))
    table.add_column("ID", style="cyan")
    table.add_column(farsi("نام کالا"), style="magenta")
    table.add_column(farsi("قیمت"), style="green")
    
    for p in results:
        table.add_row(str(p.id), farsi(p.name), str(p.price))
    console.print(table)


def get_inventory_summary(db: Session, low_stock_threshold: int = 5):
    stats = db.query(
        func.count(Product.id).label("total_products"),
        func.coalesce(func.sum(Product.quantity), 0).label("total_stock"),
        func.coalesce(func.sum(Product.quantity * Product.price), 0).label("total_value")
    ).first()

    low_stock_products = db.query(Product).filter(
        Product.quantity <= low_stock_threshold
    ).all()

    return {
        "total_products": stats.total_products or 0,
        "total_stock": stats.total_stock or 0,
        "total_value": stats.total_value or 0,
        "low_stock_count": len(low_stock_products),
        "low_stock_products": low_stock_products
    }

# --- کلاس CRUD ---

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    
    def create(self, db: Session, *, obj_in: ProductCreate) -> Product:
        # اتصال کلاس به منطق ایجاد محصول
        return create_product(db, obj_in)

    def get_inventory_summary(self, db: Session, low_stock_threshold: int = 5):
        return get_inventory_summary(db, low_stock_threshold)

product_crud = CRUDProduct(Product)
