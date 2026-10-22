from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# -----------------------------
# اسکیمای محصولات (Products)
# -----------------------------
class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    price: float
    selling_price: float
    quantity: int
    category: Optional[str] = None
    unit: Optional[str] = None


class ProductCreate(BaseModel):
    sku: str
    name: str
    price: float
    selling_price: float
    quantity: int = 0
    category: Optional[str] = None
    unit: Optional[str] = "عدد"


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[str] = None
    selling_price: Optional[float] = None
    quantity: Optional[int] = None
    category: Optional[str] = None
    unit: Optional[str] = None


# -----------------------------
# اسکیمای تراکنش‌ها (Stock Movements)
# -----------------------------
class MovementType(str, Enum):
    IN = "IN"
    OUT = "OUT"


class StockMovementCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="تعداد باید بزرگتر از صفر باشد")
    movement_type: MovementType
    notes: Optional[str] = None


class StockMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    movement_type: MovementType
    notes: Optional[str] = None
