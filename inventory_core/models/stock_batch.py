from sqlalchemy import ForeignKey, Integer, String, Float, DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from inventory_core.database import Base

class StockBatch(Base):
    __tablename__ = "stock_batches"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    batch_name: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer)        # مقدار وارد شده
    purchase_price: Mapped[float] = mapped_column(Float) # قیمت خرید
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="batches")
