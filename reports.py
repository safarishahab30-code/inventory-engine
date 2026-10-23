from sqlalchemy.orm import Session
from sqlalchemy import func
from inventory_core.models.product import Product
from inventory_core.models.stock_batch import StockBatch

def get_inventory_valuation(db: Session):
    # محاسبه موجودی و ارزش مالی بر اساس StockBatch
    results = db.query(
        Product.id,
        Product.sku,
        Product.name,
        func.coalesce(func.sum(StockBatch.quantity), 0).label("total_on_hand"),
        func.coalesce(func.sum(StockBatch.quantity * StockBatch.purchase_price), 0.0).label("total_value")
    ).outerjoin(StockBatch, Product.id == StockBatch.product_id)\
     .group_by(Product.id, Product.sku, Product.name).all()
     
    return results
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
# ایمپورت‌های دیتابیس و مدل‌ها (متناسب با پروژه خودت)

@router.get("/reports/low-stock")
def get_low_stock_report(db: Session = Depends(get_db)):
    # محاسبه موجودی کل هر محصول و مقایسه با reorder_level
    results = (
        db.query(
            Product.id,
            Product.sku,
            Product.name,
            Product.reorder_level,
            func.coalesce(func.sum(StockBatch.quantity), 0).label("total_quantity")
        )
        .outerjoin(StockBatch, Product.id == StockBatch.product_id)
        .group_by(Product.id)
        .having(func.coalesce(func.sum(StockBatch.quantity), 0) <= Product.reorder_level)
        .all()
    )
    
    # خروجی به صورت لیست JSON یا آماده‌سازی برای CSV
    return [
        {
            "product_id": r.id,
            "sku": r.sku,
            "name": r.name,
            "reorder_level": r.reorder_level,
            "total_quantity": r.total_quantity
        }
        for r in results
    ]
