from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

# تعریف جامع پایه که فیلدهای مشترک را دارد
class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    category: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    quantity: int = Field(default=0, ge=0)
    unit: str = Field(default="عدد", max_length=20)
    min_stock: int = Field(default=0, ge=0)
    barcode: Optional[str] = Field(default=None, max_length=50)

# مدل برای ایجاد محصول جدید (ارث‌بری از بیس)
class ProductCreate(BaseModel):
    name: str
    price: float
    category: str
    sku: str
    selling_price: float # این خط را اضافه کن

# مدل برای آپدیت (فیلدها اختیاری)
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    price: Optional[float] = Field(default=None, gt=0)
    quantity: Optional[int] = Field(default=None, ge=0)
    unit: Optional[str] = Field(default=None, max_length=20)
    min_stock: Optional[int] = Field(default=None, ge=0)
    barcode: Optional[str] = Field(default=None, max_length=50)
    sku: Optional[str] = Field(default=None, min_length=1, max_length=50)

# مدل برای خروجی دیتابیس (شامل آیدی و زمان)
class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
