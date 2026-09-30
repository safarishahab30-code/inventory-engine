from inventory_core.database import SessionLocal
from inventory_core.reports import export_low_stock
import os

db = SessionLocal()
print('Exporting low stock report...')
export_low_stock(db, 'low_stock.csv')
db.close()

if os.path.exists('low_stock.csv'):
    print('SUCCESS: low_stock.csv created successfully.')
    with open('low_stock.csv', 'r', encoding='utf-8-sig') as f:
        print('File content:')
        print(f.read())
else:
    print('ERROR: File was not created.')
