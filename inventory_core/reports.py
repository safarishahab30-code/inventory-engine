from sqlalchemy import func
from inventory_core.models.product import Product
from inventory_core.utils import farsi
import csv

def export_low_stock(session, filename="low_stock.csv"):
    items = get_low_stock_report(session)
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["شناسه", "نام کالا", "کد کالا (SKU)", "موجودی فعلی", "حداقل مجاز"])
        for item in items:
            writer.writerow([item.id, item.name, item.sku, item.quantity, item.min_stock])

def count_low_stock(session):
    return session.query(Product).filter(
        func.coalesce(Product.quantity, 0) < func.coalesce(Product.min_stock, 1)
    ).count()

def get_low_stock_report(session):
    return session.query(Product).filter(
        func.coalesce(Product.quantity, 0) < func.coalesce(Product.min_stock, 1)
    ).all()

def check_low_stock_alerts(session):
    low_stock_items = get_low_stock_report(session)
    if not low_stock_items:
        print(farsi("تمام موجودی‌ها در وضعیت نرمال هستند."))
        return

    for item in low_stock_items:
        current_qty = item.quantity if item.quantity is not None else 0
        min_limit = item.min_stock if item.min_stock is not None else 1
        print(farsi(f"کالا: {item.name} | موجودی: {current_qty} | حداقل مجاز: {min_limit}"))
    print(farsi("------------------------------------"))

# در inventory_core/reports.py
def show_logs(session, page=1, page_size=10):
    from inventory_core.models.transaction import TransactionLog
    
    # محاسبه آفست برای صفحه‌بندی
    offset = (page - 1) * page_size
    logs = session.query(TransactionLog).order_by(TransactionLog.created_at.desc()).offset(offset).limit(page_size).all()
    
    if not logs:
        print(farsi("تراکنشی یافت نشد."))
        return

    print(f"\n--- {farsi('تاریخچه تراکنش‌ها')} (Page {page}) ---")
    for log in logs:
        # نمایش دقیق جزئیات
        print(f"ID: {log.id} | {log.created_at.strftime('%Y-%m-%d %H:%M')} | {log.movement_type} | Qty: {log.change_qty} | Reason: {log.reason}")
