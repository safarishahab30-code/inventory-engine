from inventory_core.crud.product import create_product, get_product
from inventory_core.schemas.product import ProductCreate


def test_create_and_get_product(db_session):
    product_in = ProductCreate(
        sku="PRD-TEST-001",
        name="کتاب تستی",
        description="توضیحات تستی",
        category="کتاب",
        price=150000,
        unit="جلد",
        min_stock=5,
    )

    created = create_product(db_session, product_in)

    assert created.id is not None
    assert created.sku == "PRD-TEST-001"

    fetched = get_product(db_session, created.id)

    assert fetched is not None
    assert fetched.name == "کتاب تستی"
from uuid import uuid4
from inventory_core.crud.product import create_product, get_product, product_crud
from inventory_core.schemas.product import ProductCreate


def _make_product(name: str = "کتاب تستی") -> ProductCreate:
    return ProductCreate(
        sku=f"PRD-{uuid4().hex[:8]}",
        name=name,
        description="توضیحات تستی",
        category="کتاب",
        price=150000,
        selling_price=200000,  # اضافه کردن این فیلد برای مطابقت با اسکیما
        unit="جلد",
        min_stock=5,
    )


def test_create_and_get_product(db_session):
    created = create_product(db_session, _make_product())
    assert created.id is not None
    fetched = get_product(db_session, created.id)
    assert fetched.name == "کتاب تستی"


def test_update_product_quantity(db_session):
    created = create_product(db_session, _make_product())
    updated = product_crud.update(db_session, id=created.id, obj_in={"quantity": 12})
    assert updated is not None
    assert updated.quantity == 12


def test_update_missing_product_returns_none(db_session):
    assert product_crud.update(db_session, id=999999, obj_in={"quantity": 1}) is None


def test_delete_product(db_session):
    created = create_product(db_session, _make_product())
    assert product_crud.remove(db_session, product_id=created.id) is True
    assert get_product(db_session, created.id) is None


def test_delete_missing_product_returns_false(db_session):
    assert not product_crud.remove(db_session, product_id=999999)
