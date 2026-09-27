from sqlalchemy.orm import Session
from inventory_core.models.product import Product
from inventory_core.models.stock_batch import StockBatch

class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def add_stock(self, product_id: int, quantity: int, price: float, batch_name: str):
        # ثبت بچ ورود کالا
        new_batch = StockBatch(
            product_id=product_id, 
            quantity=quantity, 
            purchase_price=price, 
            batch_name=batch_name
        )
        self.db.add(new_batch)
        
        # افزایش موجودی کلی در مدل Product
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.quantity += quantity
            self.db.commit()
        else:
            raise ValueError(f"محصول با شناسه {product_id} پیدا نشد.")
