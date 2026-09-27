from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class StockBatchBase(BaseModel):
    batch_number: str = Field(..., min_length=2, max_length=50)
    quantity_initial: int = Field(..., gt=0)
    quantity_current: int = Field(..., ge=0)
    purchase_price: float = Field(..., ge=0.0)
    expires_at: Optional[datetime] = None

class StockBatchCreate(BaseModel):
    batch_number: str = Field(..., min_length=2, max_length=50)
    quantity: int = Field(..., gt=0)
    purchase_price: float = Field(..., ge=0.0)
    expires_at: Optional[datetime] = None

class StockBatchResponse(StockBatchBase):
    id: int
    product_id: int
    received_at: datetime

    model_config = ConfigDict(from_attributes=True)
