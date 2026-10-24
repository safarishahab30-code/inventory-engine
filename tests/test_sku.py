from inventory_core.models.category import Category
from inventory_core.models.product import Product

def test_product_sku_creation(db_session):
    category = db_session.query(Category).filter_by(name="کتاب").first()
    if not category:
        category = Category(name="کتاب")
        db_session.add(category)
        db_session.commit()

    new_product = Product.create(
        db_session=db_session,
        name="کتاب تست",
        price=1000,
        quantity=5,
        category_id=category.id
    )
    assert new_product.sku is not None
