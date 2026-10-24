from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from inventory_core.database import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
import random
from inventory_core.models.stock_batch import StockBatch

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    unit: Mapped[str] = mapped_column(String(20), default="عدد")
    min_stock = Column(Integer)
    reorder_level = Column(Integer, default=5, nullable=False) 
    barcode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    selling_price = Column(Float, nullable=False, default=0.0)
    
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
    )
    category = relationship("Category", back_populates="products")
    batches = relationship("StockBatch", back_populates="product")

    @classmethod
    def create(cls, db_session, name: str, price: float, quantity: int, sku: Optional[str] = None, **kwargs):
        if not sku or sku == "DEFAULT_SKU":
            while True:
                generated_sku = f"PRD-{random.randint(1, 9999):04d}"
                exists = db_session.query(cls).filter_by(sku=generated_sku).first()
                if not exists:
                    sku = generated_sku
                    break

        if not name or name.strip() == "":
            raise ValueError("Name cannot be empty")
        if price < 0:
            raise ValueError("Price cannot be negative")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        instance = cls(
            name=name, 
            price=price, 
            quantity=quantity, 
            sku=sku, 
            **kwargs
        )
        
        db_session.add(instance)
        db_session.commit()
        db_session.refresh(instance)
        return instance
