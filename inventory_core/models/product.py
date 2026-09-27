from typing import List, Optional
from sqlalchemy import Integer, String, Float, Text
from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from inventory_core.database import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    unit: Mapped[str] = mapped_column(String(20), default="عدد")
    min_stock: Mapped[int] = mapped_column(Integer, default=0)
    barcode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    batches = relationship("StockBatch", back_populates="product")

    @classmethod
    def create(cls, db_session, name: str, price: float, quantity: int, sku: str = "DEFAULT_SKU", category: str = "General", **kwargs):
        # اعتبارسنجی منطقی
        if not name or name.strip() == "":
            raise ValueError("Name cannot be empty")
        if price < 0:
            raise ValueError("Price cannot be negative")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        # ساخت نمونه
        instance = cls(
            name=name, 
            price=price, 
            quantity=quantity, 
            sku=sku, 
            category=category, 
            **kwargs
        )
        
        db_session.add(instance)
        db_session.commit()
        db_session.refresh(instance)
        return instance
