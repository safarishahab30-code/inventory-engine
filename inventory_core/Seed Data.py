# در فایلی به نام seed.py
from database import SessionLocal
from inventory_core.models.product import Product

db = SessionLocal()
# درج یک کالای معیوب برای تست هشدار
item = Product(name="کالای تست", quantity=2, min_quantity=5)
db.add(item)
db.commit()
db.close()
print("داده تست درج شد.")
