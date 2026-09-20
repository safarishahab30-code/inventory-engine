import typer
from inventory_core.database import SessionLocal
from inventory_core.schemas.product import ProductCreate
from inventory_core.database import SessionLocal
from inventory_core.utils import farsi
from inventory_core.schemas.product import ProductCreate
from inventory_core.database import SessionLocal
from inventory_core.crud.product import create_product, get_products
from inventory_core.schemas.product import ProductCreate
from inventory_core.crud.product import get_all_products, create_product, update_product, delete_product,advanced_search_products
from InquirerPy import inquirer
from inventory_core.models.product import Product
from InquirerPy.base.control import Choice
from rich.console import Console
from typing import Optional, List
from rich.table import Table
from rich import box
console = Console()




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
            console.print(f"[yellow]{fa('هیچ محصولی در انبار یافت نشد.')}[/yellow]")
            return

        table = Table(
            title=farsi("📦 فهرست موجودی انبار"),
            box=box.ROUNDED,
            show_header=True,
            header_style="bold bright_blue",
        )

        table.add_column(farsi("شناسه"), justify="center", style="cyan", no_wrap=True)
        table.add_column(farsi("نام کالا"), style="bold white")
        table.add_column(farsi("دسته‌بندی"), style="yellow")
        table.add_column(farsi("قیمت (تومان)"), justify="right", style="green")
        table.add_column(farsi("موجودی"), justify="center")

        for p in products:
            if p.quantity == 0:
                qty_str = f"[bold red]{p.quantity} ({farsi('ناموجود')})[/bold red]"
            elif p.quantity < 5:
                qty_str = f"[bold yellow]{p.quantity}[/bold yellow]"
            else:
                qty_str = f"[bold green]{p.quantity}[/bold green]"

            table.add_row(
                str(p.id),
                farsi(p.name),
                farsi(p.category or "-"),
                f"{p.price:,.0f}",
                qty_str
            )

        console.print(table)
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
def search_products_cli(db, console, interactive: bool = False, name: Optional[str] = None, category: Optional[str] = None):
    """
    تابع جستجو و نمایش کالاها با دو حالت تعاملی و فیلتر-محور
    """

    # ۱. حالت تعاملی (Interactive Mode)
    if interactive:
        products = db.query(Product).all()
        if not products:
            console.print(f"[yellow]{farsi('موجودی انبار خالی است.')}[/yellow]")
            return
        
        choices = [
            Choice(p.id, name=f"{p.name} | {farsi('دسته')}: {p.category or '-'} | {p.price:,} {farsi('تومان')} | {farsi('موجودی')}: {p.quantity}") 
            for p in products
        ]
        
        selected_id = inquirer.fuzzy(
            message=farsi("کالای مورد نظر را جستجو و انتخاب کنید:"),
            choices=choices,
            multiselect=False
        ).execute()
        
        if selected_id:
            product = db.query(Product).filter(Product.id == selected_id).first()
            if product:
                display_product_table(console, product)
        return

    # ۲. حالت غیر تعاملی (Non-Interactive / Filter Mode)
    query = db.query(Product)
    if name:
        query = query.filter(Product.name.contains(name))
    if category:
        query = query.filter(Product.category == category)
    
    products = query.all()

    if not products:
        console.print(f"[yellow]{farsi('کالایی با این مشخصات یافت نشد.')}[/yellow]")
    else:
        for p in products:
            display_product_table(console, p)

def display_product_table(console, product):
    """
    تابع کمکی برای نمایش جدول جزئیات کالا جهت جلوگیری از تکرار کد
    """
    table = Table(
        title=farsi("📦 جزئیات کالا"),
        box=box.ROUNDED,
        header_style="bold green"
    )
    table.add_column(farsi("ویژگی"), style="cyan")
    table.add_column(farsi("مقدار"), style="white")
    
    table.add_row(farsi("شناسه"), str(product.id))
    table.add_row(farsi("نام کالا"), farsi(product.name))
    table.add_row(farsi("دسته‌بندی"), farsi(product.category or "-"))
    table.add_row(farsi("قیمت"), f"{product.price:,} {farsi('تومان')}")
    table.add_row(farsi("موجودی"), str(product.quantity))
    
    console.print(table)
@app.command()
def search(
    interactive: bool = typer.Option(False, "--interactive", "-i", help="حالت تعاملی"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="نام کالا"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="دسته‌بندی")
):
    # تنظیمات دیتابیس و کنسول مطابق با کدهای قبلی
    db = get_db_session() # یا هر متغیری که session دیتابیس را برمی‌گرداند
    console = Console()
    

    search_products_cli(db, console, interactive=interactive, name=name, category=category)

if __name__ == "__main__":
    app()
