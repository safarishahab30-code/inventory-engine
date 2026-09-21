import typer
from sqlalchemy.orm import Session
from inventory_core.database import SessionLocal
from inventory_core.schemas.product import ProductCreate
from inventory_core.utils import farsi
from inventory_core.schemas.product import ProductCreate
from inventory_core.schemas.product import ProductCreate
from inventory_core.crud.product import get_all_products, create_product, update_product, delete_product,advanced_search_products,adjust_product_stock,get_low_stock_products
from InquirerPy import inquirer
from inventory_core.models.product import Product
from InquirerPy.base.control import Choice
from rich.console import Console
from typing import Optional, List
from rich.table import Table
from rich import box
from typing import Optional
from pathlib import Path
from inventory_core.crud.product import get_inventory_summary
from inventory_core.services.exporter import export_to_csv, export_to_excel
from inventory_core.database import SessionLocal

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
def search_products_cli(
    db,
    console,
    interactive: bool = False,
    name: Optional[str] = None,
    category: Optional[str] = None
):
    # ۱. حالت تعاملی (Interactive Mode)
    if interactive:
        products = db.query(Product).all()
        if not products:
            console.print(f"[yellow]{farsi('موجودی انبار خالی است.')}[/yellow]")
            return

        choices = []
        for p in products:
            cat = p.category or '-'
            line =farsi(f"{p.id:>3} | {p.name:<20} | {cat:<12} | {p.price:>10,.0f} | {p.quantity:>5}")
            choices.append(Choice(value=p.id, name=line))

        selected_id = inquirer.fuzzy(
            message=farsi("کالا را جستجو یا انتخاب کنید:"),
            choices=choices,
            multiselect=False
        ).execute()

        if selected_id:
            product = db.query(Product).filter(Product.id == selected_id).first()
            if product:
                display_product_table(console, product)
        return

    # ۲. حالت غیر تعاملی (Filter Mode)
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
@app.command(name="search")
def search(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="نام کالا"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="دسته‌بندی"),
    min_price: Optional[float] = typer.Option(None, "--min-price", help="حداقل قیمت"),
    max_price: Optional[float] = typer.Option(None, "--max-price", help="حداکثر قیمت"),
    in_stock: Optional[bool] = typer.Option(None, "--in-stock", help="فقط کالاهای موجود")
):
    """جستجوی پیشرفته محصولات با فیلترهای دلخواه"""
    session = SessionLocal()
    try:
        products = advanced_search_products(
            session,
            name=name,
            category=category,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock
        )

        if not products:
            console.print(f"[yellow]{farsi('هیچ محصولی با این مشخصات یافت نشد.')}[/yellow]")
            return

        table = Table(
            title=farsi("🔍 نتایج جستجو"),
            box=box.ROUNDED,
            show_header=True,
            header_style="bold bright_blue",
        )
        table.add_column(farsi("شناسه"), justify="center", style="cyan")
        table.add_column(farsi("نام کالا"), style="bold white")
        table.add_column(farsi("دسته‌بندی"), style="yellow")
        table.add_column(farsi("قیمت (تومان)"), justify="right", style="green")
        table.add_column(farsi("موجودی"), justify="center")

        for p in products:
            qty_style = "bold green" if p.quantity >= 5 else ("bold yellow" if p.quantity > 0 else "bold red")
            table.add_row(
                str(p.id),
                farsi(p.name),
                farsi(p.category or "-"),
                f"{p.price:,.0f}",
                f"[{qty_style}]{p.quantity}[/{qty_style}]"
            )

        console.print(table)
    finally:
        session.close()

@app.command()
def adjust_stock(
    product_id: int = typer.Option(..., "--id", "-i", help="Product ID"),
    amount: int = typer.Option(..., "--amount", "-a", help="Stock change amount (positive or negative)")
):
    """افزایش یا کاهش موجودی کالا"""
    db = SessionLocal()
    try:
        product = adjust_product_stock(db, product_id, amount)
        console.print(
            f"[green]{farsi('موجودی با موفقیت تغییر کرد.')}[/green] "
            f"{product.name} -> [bold]{farsi('موجودی جدید:')} {product.quantity}[/bold]"
        )
    except ValueError as e:
        console.print(f"[red]{farsi(str(e))}[/red]")
    finally:
        db.close()
@app.command(name="low-stock")
def low_stock_command(
    threshold: int = typer.Option(5, help="آستانه هشدار کسری موجودی")
):
    """گزارش‌گیری و نمایش کالاهای کم‌موجودی انبار"""
    session = SessionLocal()
    try:
        products = get_low_stock_products(session, threshold=threshold)
        
        if not products:
            typer.echo(farsi(f"هیچ کالایی با موجودی کمتر یا مساوی {threshold} یافت نشد."))
            return

        typer.echo(farsi(f"\n⚠️ لیست کالاهای کم‌موجودی (آستانه: {threshold}):\n" + "-" * 50))
        for p in products:
            # تغییر از p.stock به p.quantity
            typer.echo(farsi(f"ID: {p.id} | Name: {p.name} | Quantity: {p.quantity}"))
    except Exception as e:
        # اصلاح: پارامتر err=True فقط برای typer.echo است
        typer.echo(farsi(f"خطا در دریافت گزارش: {e}"), err=True)
    finally:
        session.close()
@app.command(name="report", help="گزارش آماری انبار با امکان خروجی فایل اکسل یا CSV")
def inventory_report(
    export: str = typer.Option(
        None, 
        "--export", "-e", 
        help="فرمت خروجی گزارش: csv یا excel"
    ),
    threshold: int = typer.Option(
        5, 
        "--threshold", "-t", 
        help="آستانه هشدار کسری موجودی"
    )
):
    db = SessionLocal()
    try:
        summary = get_inventory_summary(db, low_stock_threshold=threshold)
        
        # ۱. نمایش وضعیت کلی در کنسول
        summary_table = Table(title="📊 خلاصه وضعیت انبار")
        summary_table.add_column("شاخص", style="cyan")
        summary_table.add_column("مقدار", style="green")

        summary_table.add_row("تعداد انواع کالاها", str(summary["total_products"]))
        summary_table.add_row("مجموع موجودی فیزیکی", str(summary["total_stock"]))
        summary_table.add_row("ارزش ریالی کل انبار", f"{summary['total_value']:,} تومان")
        summary_table.add_row("تعداد کالاهای رو به اتمام", str(summary["low_stock_count"]))
        
        console.print(summary_table)

        # ۲. نمایش اقلام کم‌موجود در صورت وجود
        if summary["low_stock_products"]:  # تغییر از low_stock_items به low_stock_products
            console.print("\n[bold red]⚠️ کالاهای با موجودی بحرانی:[/bold red]")
            low_table = Table()
            low_table.add_column("شناسه", style="dim")
            low_table.add_column("نام کالا")
            low_table.add_column("موجودی", style="red")
            
            for item in summary["low_stock_products"]:
                low_table.add_row(str(item.id), item.name, str(item.quantity))
            console.print(low_table)

        # ۳. پردازش خروجی فایل (در صورت مشخص شدن فلگ --export)
        if export:
            export_format = export.lower().strip()
            # آماده‌سازی داده‌ها برای اکسپورت
            products = get_all_products(db)
            export_data = [
                {
                    "شناسه": p.id,
                    "نام کالا": p.name,
                    "بارکد": p.barcode or "-",
                    "قیمت (تومان)": p.price,
                    "موجودی": p.stock,
                    "وضعیت": "فعال" if p.is_active else "غیرفعال"
                }
                for p in products
            ]

            output_dir = Path("exports")
            if export_format == "csv":
                file_path = output_dir / "inventory_report.csv"
                export_to_csv(export_data, file_path)
                console.print(f"\n[green]✔ گزارش CSV با موفقیت ذخیره شد:[/green] {file_path}")
            elif export_format in ["excel", "xlsx"]:
                file_path = output_dir / "inventory_report.xlsx"
                export_to_excel(export_data, file_path)
                console.print(f"\n[green]✔ گزارش اکسل با موفقیت ذخیره شد:[/green] {file_path}")
            else:
                console.print(f"\n[red]❌ فرمت نامعتبر است. فرمت‌های مجاز: csv یا excel[/red]")

    finally:
        db.close()

if __name__ == "__main__":
    app()
