from typing import Optional
import typer
from pydantic import ValidationError

from inventory_core.database import SessionLocal
from inventory_core.crud.product import create_product
from inventory_core.schemas.product import ProductCreate
from inventory_core.utils import farsi

app = typer.Typer()


@app.command()
def add(
    name: str = typer.Option(..., "--name", "-n", help="نام کالا"),
    category: str = typer.Option(..., "--category", "-c", help="دسته‌بندی"),
    price: float = typer.Option(..., "--price", "-p", help="قیمت"),
    quantity: int = typer.Option(0, "--quantity", "-q", help="موجودی"),
    barcode: Optional[str] = typer.Option(None, "--barcode", "-b", help="بارکد"),
):
    try:
        product_in = ProductCreate(
            name=name,
            category=category,
            price=price,
            quantity=quantity,
            barcode=barcode,
        )
    except ValidationError as e:
        typer.echo(farsi(f"خطای اعتبارسنجی: {e}"))
        raise typer.Exit(code=1)

    db = SessionLocal()
    try:
        new_prod = create_product(db, product_in)
        typer.echo(farsi(f"محصول '{new_prod.name}' با شناسه {new_prod.id} با موفقیت ثبت شد."))
    finally:
        db.close()


@app.command()
def test():
    typer.echo(farsi("سیستم انبارداری آماده به کار است!"))


@app.command()
def version():
    typer.echo("0.1.0")

@app.command(name="list")
def list_products():
    from inventory_core.database import SessionLocal
    from inventory_core.crud.product import get_products
    
    db = SessionLocal()
    try:
        products = get_products(db)
        if not products:
            typer.echo(farsi("هیچ محصولی یافت نشد."))
            return
        for p in products:
            typer.echo(farsi(f"{p.id} | {p.name} | {p.category} | موجودی: {p.quantity} | قیمت: {p.price}"))
    finally:
        db.close()

if __name__ == "__main__":
    app()
