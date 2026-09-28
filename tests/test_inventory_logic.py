import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from inventory_core.database import Base
from inventory_core.models.product import Product
from inventory_core.services.inventory_service import InventoryService


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
        quantity=0,
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

def test_record_stock_movement_in_and_out(db_session):
    product = Product.create(
        db_session=db_session,
        name="کتاب تستی",
        sku="TEST-SKU-100",
        price=50000,
        quantity=0,
        category="کتاب",
    )
    service = InventoryService(db_session)

    # تست ورود کالا
    batch = service.add_stock(
        product_id=product.id,
        quantity=10,
        purchase_price=40000,
        batch_name="BATCH-001",
    )
    db_session.refresh(product)
    assert product.quantity == 10
    assert batch.quantity == 10

    # تست خروج کالا
    service.issue_stock(product_id=product.id, quantity=4)
    db_session.refresh(product)
    assert product.quantity == 6


def test_record_stock_movement_negative_stock_prevented(db_session):
    product = Product.create(
        db_session=db_session,
        name="کتاب تستی دوم",
        sku="TEST-SKU-200",
        price=30000,
        quantity=0,
        category="کتاب",
    )
    service = InventoryService(db_session)
    service.add_stock(
        product_id=product.id,
        quantity=5,
        purchase_price=25000,
        batch_name="BATCH-002",
    )

    # تلاش برای خروج بیش از موجودی
    with pytest.raises(ValueError):
        service.issue_stock(product_id=product.id, quantity=10)

def test_record_stock_movement_negative_stock_prevented(db_session):
    product = Product.create(
        db_session=db_session,
        name="کتاب تستی دوم",
        sku="TEST-SKU-200",
        price=30000,
        quantity=0,
        category="کتاب",
    )
    service = InventoryService(db_session)
    service.add_stock(
        product_id=product.id,
        quantity=5,
        purchase_price=25000,
        batch_name="BATCH-002",
    )

    # تلاش برای خروج بیش از موجودی (باید خطا صادر شود)
    with pytest.raises(ValueError):
        service.issue_stock(product_id=product.id, quantity=10)
