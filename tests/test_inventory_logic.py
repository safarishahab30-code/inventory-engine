from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from inventory_core.database import Base
from inventory_core.models.product import Product
from inventory_core.services import InventoryService


def test_add_stock_increases_product_quantity():
    # 1. Setup in-memory test database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # 2. Setup initial product
    product = Product(
        sku="BOOK-001",
        name="Test Book",
        category="General",
        price=10000.0,
    )
    db.add(product)
    db.commit()

    # 3. Execute service action
    service = InventoryService(db)
    service.add_stock(
        product_id=product.id,
        quantity=50,
        batch_name="Batch 1",
        purchase_price=100000.0,
    )

    # 4. Assert outcome
    updated_product = db.query(Product).filter(Product.id == product.id).first()
    assert updated_product.quantity == 50

    db.close()
