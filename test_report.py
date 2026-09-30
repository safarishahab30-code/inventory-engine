import sys
import os

# اول مسیر را اضافه کن
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# سپس ایمپورت‌های پروژه
from inventory_core.database import engine, Base
from inventory_core.reports import check_low_stock_alerts

# ساخت دیتابیس
Base.metadata.create_all(bind=engine)

# اجرای تست
try:
    check_low_stock_alerts()
except Exception as e:
    print(f"خطا در اجرا: {e}")
