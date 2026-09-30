from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# مسیر فایل دیتابیس
DATABASE_URL = "sqlite:///./inventory.db"

# تنظیم موتور دیتابیس
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# تنظیم سشن
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# تابع برای دریافت سشن (استفاده در اپلیکیشن)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# تابع ساخت جداول (فقط در مرحله init)
def init_db():
    from inventory_core.models.product import Product
    from inventory_core.models.stock_batch import StockBatch
    Base.metadata.create_all(bind=engine)
