from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from inventory_core.database import Base

class TransactionLog(Base):
    __tablename__ = "transaction_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, nullable=False) # اگر Foreign Key لازم است، بعدا اضافه می‌کنیم
    change_qty = Column(Integer, nullable=False)  # مثبت برای ورود، منفی برای خروج
    movement_type = Column(String(20), nullable=False)  # IN, OUT, ADJUSTMENT
    reason = Column(String(255), nullable=True)  # علت تراکنش (خرید، فروش، ضایعات و ...)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
