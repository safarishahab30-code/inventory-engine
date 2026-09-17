from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="نام کالا")
    category: str = Field(..., min_length=1, max_length=50, description="دسته‌بندی")
    price: float = Field(..., gt=0, description="قیمت باید بزرگتر از صفر باشد")
    quantity: int = Field(default=0, ge=0, description="موجودی نمی‌تواند منفی باشد")
    barcode: Optional[str] = Field(default=None, max_length=50, description="بارکد یکتا")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    price: Optional[float] = Field(default=None, gt=0)
    quantity: Optional[int] = Field(default=None, ge=0)
    barcode: Optional[str] = Field(default=None, max_length=50)


class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
