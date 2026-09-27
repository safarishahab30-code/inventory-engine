from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from inventory_core.database import Base

class StockBatch(Base):
    __tablename__ = "stock_batches"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    batch_name: Mapped[str] = mapped_column(String)
    
    # رابطه
    product = relationship("Product", back_populates="batches")