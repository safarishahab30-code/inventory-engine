from inventory_core.database import SessionLocal
from inventory_core.models.product import Product

db = SessionLocal()
# مثال برای اصلاح در test_db.py
new_item = Product(
    sku='TEST-001', 
    name='کتاب تست', 
    category='آموزشی',   # مقداردهی به category
    price=100000.0,      # مقداردهی به price
    quantity=10          # جایگزین برای stock_quantity
)

db.add(new_item)
db.commit()
print('درج با موفقیت انجام شد.')
db.close()
