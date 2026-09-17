from inventory_core.database import engine
from inventory_core.models import Product  # ایمپورت مدل برای شناسایی توسط metadata

print("Creating database tables...")
Product.metadata.create_all(bind=engine)
print("Done.")

