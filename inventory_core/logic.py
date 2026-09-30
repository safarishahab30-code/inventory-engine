from sqlalchemy.orm import Session
from sqlalchemy import or_
from inventory_core.models.product import Product
from inventory_core.models.stock_batch import StockBatch
from inventory_core.models.stock_movement import StockMovement
from inventory_core.utils import farsi
from inventory_core.reports import export_low_stock

# تابعی که قبلاً در فایل دیگری بود، اینجا قرار می‌گیرد تا در دسترس باشد
def log_event(event_type, details):
    print(farsi(f"[LOG] {event_type}: {details}"))

class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def show_logs(self, page=1, limit=10):
        from inventory_core.models.transaction import TransactionLog
        from rich.table import Table
        from rich.console import Console
        console = Console()

        offset = (page - 1) * limit
        # تغییر از timestamp به created_at (یا نام صحیح موجود در مدل)
        logs = self.db.query(TransactionLog).order_by(TransactionLog.created_at.desc()).offset(offset).limit(limit).all()

        table = Table(title=farsi("تاریخچه تراکنش‌ها"))
        table.add_column("ID", style="cyan")
        table.add_column(farsi("نوع"), style="magenta")
        table.add_column(farsi("مقدار"), style="green")
        table.add_column(farsi("توضیح"), style="yellow")

        for log in logs:
            table.add_row(str(log.id), farsi(log.log_type), str(log.quantity), farsi(log.details))
    
        console.print(table)


    def _refresh_report(self):
        try:
            export_low_stock(self.db)
        except Exception as e:
            print(farsi(f"خطا در به‌روزرسانی گزارش: {e}"))

    def get_transaction_history(self):
        return self.db.query(StockMovement).order_by(StockMovement.created_at.desc()).all()

    def search_products(self, query: str):
        search_pattern = f"%{query}%"
        return self.db.query(Product).filter(
            or_(
                Product.name.ilike(search_pattern),
                Product.sku.ilike(search_pattern)
            )
        ).all()

    def add_stock(self, product_id: int, quantity: int, buy_price: float, batch_name: str = None, min_stock: int = 1):
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"محصول با شناسه {product_id} پیدا نشد.")

        new_batch = StockBatch(
            product_id=product_id,
            quantity=quantity,
            purchase_price=buy_price,
            batch_name=batch_name
        )
        self.db.add(new_batch)
        product.quantity += quantity

        movement = StockMovement(
            product_id=product_id,
            change_qty=quantity,
            movement_type="IN",
            reason=f"ورود کالا با پارت/بچ: {batch_name}"
        )
        if min_stock is not None:
            product.min_stock = min_stock
        self.db.add(movement)
        self.db.commit()
        log_event("ADD_STOCK", f"PID:{product_id}, Qty:{quantity}, Batch:{batch_name}")
        self._refresh_report()

    def issue_stock(self, product_id: int, quantity: int, reason: str):
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("محصول یافت نشد.")
        if product.quantity < quantity:
            raise ValueError("موجودی کافی نیست.")

        product.quantity -= quantity
        movement = StockMovement(
            product_id=product_id,
            change_qty=-quantity,
            movement_type="OUT",
            reason=reason
        )
        self.db.add(movement)
        self.db.commit()
        log_event("ISSUE_STOCK", f"PID:{product_id}, Qty:{quantity}, Reason:{reason}")
        self._refresh_report()
        return True

    def receive_order(self, product_id: int, quantity: int):
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        product.quantity += quantity
        movement = StockMovement(
            product_id=product_id,
            change_qty=quantity,
            movement_type="IN",
            reason="ورود کالا از سفارش"
        )
        self.db.add(movement)
        self.db.commit()
        log_event("RECEIVE_ORDER", f"PID:{product_id}, Qty:{quantity}")
        self._refresh_report()
        return True
