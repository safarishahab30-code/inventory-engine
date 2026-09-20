import typer
from inventory_core.database import SessionLocal
from inventory_core.schemas.product import ProductCreate
from inventory_core.database import SessionLocal
from inventory_core.utils import farsi
from inventory_core.schemas.product import ProductCreate
from inventory_core.database import SessionLocal
from inventory_core.crud.product import create_product, get_products
from inventory_core.schemas.product import ProductCreate
from inventory_core.crud.product import get_all_products
from inventory_core.crud.product import get_all_products, create_product, update_product, delete_product





app = typer.Typer()

@app.command()
def add_product(
    name: str = typer.Argument(None, help="Product name"),
    category: str = typer.Argument(None, help="Product category"),
    price: float = typer.Argument(..., help="Product price"),
    quantity: int = typer.Option(0, help="Product quantity"),
    barcode: str = typer.Option(None, help="Product barcode")
):
    # دریافت تعاملی اگر آرگومان وارد نشده باشد
    if not name:
        name = typer.prompt("نام کالا")
    if not category:
        category = typer.prompt("دسته‌بندی کالا")
        
    product_data = ProductCreate(name=name, category=category, price=price, quantity=quantity, barcode=barcode)
@app.command(name="list")
def list_products():
    db = SessionLocal()
    try:
        products = get_all_products(db)
        if not products:
            print("❌ هیچ محصولی در دیتابیس یافت نشد.")
            return

        print("\n📦 لیست محصولات موجود در انبار:")
        print("-" * 50)
        for p in products:
            print(farsi(f"ID: {p.id} | نام: {p.name} | قیمت: {p.price:,.0f} تومان | دسته: {p.category}"))
        print("-" * 50 + "\n")
    finally:
        db.close()
@app.command()
def add(name: str, price: float, category: str): # اضافه شدن پارامتر category
    session = SessionLocal() 
    try:
        # پاس دادن category به مدل
        product_data = ProductCreate(name=name, price=price, category=category)
        new_product = create_product(session, product=product_data)
        print(farsi(f"محصول با شناسه {new_product.id} با موفقیت ثبت شد."))
    finally:
        session.close()
@app.command(name="update")
def update(
    product_id: int,
    name: str = typer.Option(None, "--name", "-n", help="نام جدید محصول"),
    price: float = typer.Option(None, "--price", "-p", help="قیمت جدید محصول"),
    category: str = typer.Option(None, "--category", "-c", help="دسته‌بندی جدید محصول")
):
    session = SessionLocal()
    try:
        updated = update_product(session, product_id=product_id, name=name, price=price, category=category)
        if not updated:
            print(farsi(f"❌ محصولی با شناسه {product_id} یافت نشد."))
            return
        
        print(farsi(f"✅ محصول با شناسه {product_id} با موفقیت ویرایش شد."))
    finally:
        session.close()
@app.command(name="delete")
def delete(product_id: int):
    session = SessionLocal()
    try:
        success = delete_product(session, product_id=product_id)
        if not success:
            print(farsi(f"❌ محصولی با شناسه {product_id} یافت نشد."))
            return
        
        print(farsi(f"🗑️ محصول با شناسه {product_id} با موفقیت حذف شد."))
    finally:
        session.close()

if __name__ == "__main__":
    app()
