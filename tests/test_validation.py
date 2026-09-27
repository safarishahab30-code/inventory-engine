import pytest
from inventory_core.models.product import Product
def test_create_product_with_negative_price(db_session):
    # بررسی اینکه قیمت منفی نباید پذیرفته شود
    with pytest.raises(ValueError):
        Product.create(db_session, name="خطای قیمت", price=-10, quantity=5)

def test_create_product_with_negative_quantity(db_session):
    # بررسی اینکه موجودی منفی نباید پذیرفته شود
    with pytest.raises(ValueError):
        Product.create(db_session, name="خطای موجودی", price=10, quantity=-1)

def test_create_product_with_empty_name(db_session):
    # بررسی اینکه نام محصول نباید خالی باشد
    with pytest.raises(ValueError):
        Product.create(db_session, name="", price=10, quantity=5)
