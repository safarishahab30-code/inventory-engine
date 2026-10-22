from pydantic import BaseModel, ConfigDict

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    price: float
    selling_price: float
    quantity: int
    category: str | None = None
    unit: str | None = None
class ProductCreate(BaseModel):
    sku: str
    name: str
    price: float
    selling_price: float
    quantity: int = 0
    category: str | None = None
    unit: str | None = "عدد"
class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    selling_price: float | None = None
    quantity: int | None = None
    category: str | None = None
    unit: str | None = None
