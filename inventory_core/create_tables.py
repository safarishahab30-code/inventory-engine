import sys
import os
from inventory_core.database import Base
print(f"Current Working Directory: {os.getcwd()}")
print(f"sys.path: {sys.path}")

# اضافه کردن مسیر ریشه
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from inventory_core.database import engine, Base
    print("Imports successful.")
except ImportError as e:
    print(f"Import Error details: {e}")
    sys.exit(1)

print('Creating tables...')
Base.metadata.create_all(engine)
print('Tables created successfully.')
