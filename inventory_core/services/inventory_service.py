import csv
from datetime import datetime, timezone

from sqlalchemy import asc

from inventory_core.models.product import Product
from inventory_core.models.stock_batch import StockBatch
from inventory_core.models.stock_movement import StockMovement


class InventoryService:
    def __init__(self, session):
        self.session = session
        self.db = session

    def add_stock(
        self,
        product_id: int,
        quantity: int,
        purchase_price: float,
        batch_name: str = "default_batch",
    ):
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("محصول یافت نشد")

        new_batch = StockBatch(
            product_id=product_id,
            quantity=quantity,
            purchase_price=purchase_price,
            batch_name=batch_name,
            received_at=datetime.now(timezone.utc),
        )
        product.quantity += quantity

        self.db.add(new_batch)
        self.db.commit()
        self.db.refresh(product)
        return new_batch

    def issue_stock(self, product_id: int, quantity: int):
        """خروج کالا با منطق FIFO (اولین ورودی، اولین خروجی)"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("محصول یافت نشد")

        batches = (
            self.db.query(StockBatch)
            .filter(
                StockBatch.product_id == product_id,
                StockBatch.quantity > 0,
            )
            .order_by(asc(StockBatch.received_at))
            .all()
        )

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

        product.quantity -= quantity

        self.db.commit()
        self.db.refresh(product)

    def calculate_rop(
        self,
        daily_usage: float,
        lead_time: int,
        safety_stock: float,
    ) -> float:
        """محاسبه نقطه سفارش (Reorder Point)"""
        return (daily_usage * lead_time) + safety_stock

    def check_stock_status(self, product_id: int, rop_value: float):
        """بررسی وضعیت کالا نسبت به نقطه سفارش"""
        batches = (
            self.db.query(StockBatch)
            .filter(StockBatch.product_id == product_id)
            .all()
        )
        total_stock = sum(batch.quantity for batch in batches)

        if total_stock <= 0:
            return "OUT_OF_STOCK"
        if total_stock <= rop_value:
            return "NEEDED_REORDER"
        return "OK"

    def get_expired_batches(self):
        """شناسایی بچ‌های منقضی شده نسبت به تاریخ امروز"""
        return (
            self.db.query(StockBatch)
            .filter(
                StockBatch.expiry_date < datetime.now(timezone.utc),
                StockBatch.quantity > 0,
            )
            .all()
        )

    def record_stock_movement(
        self,
        product_id: int,
        change_qty: int,
        movement_type: str,
        reason: str = "No reason provided",
    ):
        """ثبت ورود یا خروج کالا و تغییر موجودی محصول"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("محصول مورد نظر یافت نشد.")

        new_stock = product.quantity + change_qty
        if new_stock < 0:
            raise ValueError("موجودی کالا نمی‌تواند منفی شود.")

        product.quantity = new_stock

        movement = StockMovement(
            product_id=product_id,
            change_qty=change_qty,
            movement_type=movement_type,
            reason=reason,
        )
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(product)
        return product, movement

    def export_inventory_csv(self, file_path: str = "inventory_report.csv"):
        """خروجی لیست محصولات و موجودی به فایل CSV استاندارد اکسل"""
        products = self.db.query(Product).all()

        headers = [
            "شناسه",
            "نام کالا",
            "دسته‌بندی",
            "موجودی کل",
            "قیمت واحد",
            "نقطه سفارش (ROP)",
        ]

        with open(file_path, mode="w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)

            for product in products:
                writer.writerow(
                    [
                        product.id,
                        product.name,
                        product.category,
                        product.quantity,
                        product.price,
                        getattr(product, "reorder_point", "-"),
                    ]
                )

        return file_path

