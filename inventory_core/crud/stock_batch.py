from typing import List, Optional
from sqlalchemy.orm import Session
from inventory_core.models.stock_batch import StockBatch
from inventory_core.schemas.stock_batch import StockBatchCreate
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from inventory_core.database import Base

def create_stock_batch(db: Session, product_id: int, batch_in: StockBatchCreate) -> StockBatch:
    batch = StockBatch(
        product_id=product_id,
        batch_number=batch_in.batch_number,
        quantity_initial=batch_in.quantity,
        quantity_current=batch_in.quantity,
        purchase_price=batch_in.purchase_price,
        expires_at=batch_in.expires_at
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch

def get_batches_by_product(db: Session, product_id: int) -> List[StockBatch]:
    return (
        db.query(StockBatch)
        .filter(StockBatch.product_id == product_id, StockBatch.quantity_current > 0)
        .order_by(StockBatch.received_at.asc())
        .all()
    )
