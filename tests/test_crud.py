from uuid import uuid4
from inventory_core.crud.product import create_product, get_product, product_crud
from inventory_core.schemas.product import ProductCreate
from inventory_core.services.category_service import create_category
def _make_product(category_id: int, name: str = "کتاب تستی") -> ProductCreate:
    return ProductCreate(
        sku=f"PRD-{uuid4().hex[:8]}",
        name=name,
        description="توضیحات تستی",
        category_id=category_id,
        price=150000,
        selling_price=200000,
        unit="جلد",
        min_stock=5,
    )

def test_create_and_get_product(db_session):
    category = create_category(db_session, "کتاب و انتشارات", "admin")
    created = create_product(db_session, _make_product(category.id))
    
    assert created.id is not None
    fetched = get_product(db_session, created.id)
    assert fetched.name == "کتاب تستی"
    assert fetched.category_id == category.id


def test_update_product_quantity(db_session):
    category = create_category(db_session, "لوازم التحریر", "admin")
    created = create_product(db_session, _make_product(category.id))
    updated = product_crud.update(db_session, id=created.id, obj_in={"quantity": 12})
    
    assert updated is not None
    assert updated.quantity == 12


def test_update_missing_product_returns_none(db_session):
    assert product_crud.update(db_session, id=999999, obj_in={"quantity": 1}) is None


def test_delete_product(db_session):
    category = create_category(db_session, "عمومی", "admin")
    created = create_product(db_session, _make_product(category.id))
    
    assert product_crud.remove(db_session, product_id=created.id) is True
    assert get_product(db_session, created.id) is None


def test_delete_missing_product_returns_false(db_session):
    assert not product_crud.remove(db_session, product_id=999999)
