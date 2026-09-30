from inventory_core.database import SessionLocal
from inventory_core.reports import get_low_stock_report

db = SessionLocal()
print('Checking low stock items...')

items = get_low_stock_report(db)

if not items:
    print('No items found with low stock in database.')
else:
    for i in items:
        print(f'Product: {i.name}, Qty: {i.quantity}, Min: {i.min_stock}')

db.close()
