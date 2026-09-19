import typer
from inventory_core.database import SessionLocal
from inventory_core.crud.product import create_product
from inventory_core.schemas.product import ProductCreate

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