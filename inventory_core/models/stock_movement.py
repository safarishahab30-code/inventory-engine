from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from inventory_core.database import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    change_qty = Column(Integer, nullable=False)  # مثبت برای ورود، منفی برای خروج
    movement_type = Column(String(20), nullable=False)  # IN, OUT, ADJUSTMENT
    reason = Column(String(255), nullable=True)  # علت تراکنش (خرید، فروش، ضایعات و ...)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

