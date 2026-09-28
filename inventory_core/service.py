from sqlalchemy.orm import Session
from inventory_core.models.product import Product
from inventory_core.models.stock_batch import StockBatch
from inventory_core.models.stock_movement import StockMovement

class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def add_stock(self, product_id: int, quantity: int, price: float, batch_name: str):
        new_batch = StockBatch(
            product_id=product_id, 
            quantity=quantity, 
            purchase_price=price, 
            batch_name=batch_name
        )
        self.db.add(new_batch)
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.quantity += quantity
            self.db.commit()
        else:
            raise ValueError(f"محصول با شناسه {product_id} پیدا نشد.")

    def get_transaction_history(self):
        # کوئری دیتابیس اکنون در لایه سرویس متمرکز است
        return self.db.query(StockMovement).order_by(StockMovement.created_at.desc()).limit(20).all()

    def issue_stock(self, product_id: int, quantity: int):
        # منطق خروجی کالا اینجا قرار می‌گیرد
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product or product.quantity < quantity:
            raise ValueError("موجودی کافی نیست.")
        product.quantity -= quantity
        self.db.commit()
