from datetime import datetime, timezone
from sqlalchemy import asc
from inventory_core.models.stock_batch import StockBatch
from inventory_core.models.product import Product
from inventory_core.models.stock_batch import StockBatch

class InventoryService:
    def __init__(self, db):
        self.db = db

    def add_stock(self, product_id: int, quantity: int, purchase_price: float, batch_name: str = None):
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("محصول یافت نشد")

        new_batch = StockBatch(
            product_id=product_id,
            quantity=quantity,
            purchase_price=purchase_price,
            batch_name=batch_name,
            received_at=datetime.now(timezone.utc)
        )
        product.quantity += quantity

        self.db.add(new_batch)
        self.db.commit()
        self.db.refresh(product)
        return new_batch

    def issue_stock(self, product_id: int, quantity: int):
        """خروج کالا با منطق FIFO (اولین ورودی، اولین خروجی)"""
        # دریافت تمام بچ‌های موجود به ترتیب تاریخ ورود (قدیمی‌ترین‌ها اول)
        batches = self.db.query(StockBatch).filter(
            StockBatch.product_id == product_id,
            StockBatch.quantity > 0
                # خط مرتب‌سازی بر اساس تاریخ دریافت:
        ).order_by(asc(StockBatch.received_at)).all()

        remaining_to_issue = quantity

        for batch in batches:
            if remaining_to_issue <= 0:
                break
            
            if batch.quantity >= remaining_to_issue:
                batch.quantity -= remaining_to_issue
                remaining_to_issue = 0
            else:
                remaining_to_issue -= batch.quantity
                batch.quantity = 0
        
        if remaining_to_issue > 0:
            raise ValueError(f"موجودی کافی برای محصول {product_id} نیست.")
        
        self.db.commit()

    def calculate_rop(self, daily_usage: float, lead_time: int, safety_stock: float) -> float:
        """محاسبه نقطه سفارش (Reorder Point)"""
        return (daily_usage * lead_time) + safety_stock

    def check_stock_status(self, product_id: int, rop_value: float):
        """بررسی وضعیت کالا نسبت به نقطه سفارش"""
        total_stock = sum(b.quantity for b in self.db.query(StockBatch).filter(StockBatch.product_id == product_id).all())
        
        if total_stock <= 0:
            return "OUT_OF_STOCK"
        if total_stock <= rop_value:
            return "NEEDED_REORDER"
        return "OK"

    def get_expired_batches(self):
        """شناسایی بچ‌های منقضی شده نسبت به تاریخ امروز"""
        return self.db.query(StockBatch).filter(
            StockBatch.expiry_date < datetime.utcnow(),
            StockBatch.quantity > 0
        ).all()
