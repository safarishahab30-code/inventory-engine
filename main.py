from sqlalchemy.exc import IntegrityError
from rich.table import Table
from rich.console import Console
import questionary
from sqlalchemy import or_
from inventory_core.database import SessionLocal
# فرض بر اینکه ماژول‌های مورد نیاز در مسیر هستند
from inventory_core.service import InventoryService
from inventory_core.models.product import Product
import sys
sys.stdout.reconfigure(encoding='utf-8')
from bidi.algorithm import get_display
import arabic_reshaper
from inventory_core.crud.product import product_crud
def farsi(text):
    # تغییر شکل حروف (Reshaping)
    reshaped_text = arabic_reshaper.reshape(text)
    # اصلاح جهت نمایش (Bidi)
    return get_display(reshaped_text)

console = Console()
def get_safe_input(prompt):
    """دریافت ورودی با پردازش farsi."""
    full_prompt = f"{prompt} (برای بازگشت: b)"
    answer = questionary.text(farsi(full_prompt)).ask()
    if answer is None: return None
    answer = answer.strip()
    if not answer or answer.lower() in {"b", "back", "بازگشت"}:
        return None
    return answer

def display_status(session):
    products = product_crud.get_multi(session)
    table = Table(title=farsi("وضعیت فعلی انبار"))
    table.add_column("ID", style="cyan")
    table.add_column(farsi("نام کالا"), style="magenta")
    table.add_column(farsi("موجودی"), justify="right", style="green")

    for product in products:
        table.add_row(str(product.id), farsi(product.name), str(product.quantity))
    console.print(table)

def search_products(session):
    """جستجوی محصول بر اساس نام یا SKU."""
    term = get_safe_input("عبارت مورد نظر (نام یا SKU)")
    if term is None: return

    results = product_crud.search(session, term)
    if not results:
        console.print(farsi("[yellow]محصولی با این مشخصات یافت نشد.[/yellow]"))
        return

    table = Table(title=farsi("نتایج جستجو"))
    table.add_column("ID", style="cyan")
    table.add_column(farsi("نام کالا"), style="magenta")
    table.add_column(farsi("موجودی"), style="green")

    for p in results:
        table.add_row(str(p.id), farsi(p.name), str(p.quantity))
    console.print(table)

def show_logs(service):
    """نمایش تاریخچه تراکنش‌ها."""
    logs = service.get_transaction_history()
    
    table = Table(title=farsi("تاریخچه تراکنش‌ها"))
    table.add_column(farsi("تاریخ"), style="dim")
    table.add_column(farsi("نوع"), style="cyan")
    table.add_column(farsi("تعداد"), style="magenta")

    for log in logs:
        # تنظیم بر اساس فیلدهای مدل موجود
        table.add_row(str(log.timestamp), farsi(log.type), str(log.quantity))
    
    console.print(table)

def create_product(session):
    name = get_safe_input("نام کالا")
    if name is None: return
    sku = get_safe_input("کد SKU")
    if sku is None: return
    category = get_safe_input("دسته‌بندی")
    if category is None: return
    price_text = get_safe_input("قیمت فروش")
    if price_text is None: return

    try:
        price = float(price_text)
        new_product = ProductCreate(name=name, sku=sku, category=category, price=price, selling_price=price)
        product_crud.create(session, obj_in=new_product)
        console.print(farsi("[bold green]✅ محصول با موفقیت ایجاد شد.[/bold green]"))
    except IntegrityError:
        session.rollback()
        console.print(farsi("[bold red]❌ خطا: این SKU قبلاً ثبت شده است.[/bold red]"))
    except Exception as error:
        session.rollback()
        console.print(farsi(f"[bold red]❌ خطا: {error}[/bold red]"))

def add_stock(service):
    pid_text = get_safe_input("شناسه محصول (ID)")
    if pid_text is None: return
    qty_text = get_safe_input("تعداد ورودی")
    if qty_text is None: return
    price_text = get_safe_input("قیمت خرید")
    if price_text is None: return

    try:
        service.add_stock(int(pid_text), int(qty_text), float(price_text))
        console.print(farsi("[bold green]✅ موجودی با موفقیت اضافه شد.[/bold green]"))
    except Exception as error:
        console.print(farsi(f"[bold red]❌ ناموفق: {error}[/bold red]"))

def issue_stock(service):
    pid_text = get_safe_input("شناسه محصول (ID)")
    if pid_text is None: return
    qty_text = get_safe_input("تعداد خروجی")
    if qty_text is None: return

    try:
        service.issue_stock(int(pid_text), int(qty_text))
        console.print(farsi("[bold yellow]⚠️ موجودی کسر شد.[/bold yellow]"))
    except Exception as error:
        console.print(farsi(f"[bold red]❌ ناموفق: {error}[/bold red]"))
def main():
    session =SessionLocal()
    service = InventoryService(session)

    try:  # شروع بلاک try
        while True:
            console.clear()
            choice = questionary.select(
                message=farsi("Inventory Engine - پنل مدیریت:"),
                choices=[
                    farsi("ایجاد محصول جدید"),
                    farsi("افزودن کالا"),
                    farsi("خروج کالا"),
                    farsi("مشاهده موجودی"),
                    farsi("جستجوی پیشرفته"),
                    farsi("مشاهده تاریخچه تراکنش‌ها"),
                    farsi("خروج")
                ]
            ).ask()

            # بررسی خروج
            if choice is None or choice == farsi("خروج"):
                console.print(farsi("[bold red]سیستم متوقف شد.[/bold red]"))
                break

            # مدیریت انتخاب‌ها (خارج از بلاک break)
            if choice == farsi("ایجاد محصول جدید"):
                create_product(session)
            elif choice == farsi("افزودن کالا"):
                add_stock(service)
            elif choice == farsi("خروج کالا"):
                issue_stock(service)
            elif choice == farsi("مشاهده موجودی"):
                display_status(session)
                questionary.press_any_key_to_continue(farsi("\nبرای بازگشت کلید بزنید...")).ask()
            elif choice == farsi("جستجوی پیشرفته"):
                # فرض بر اینکه این تابع را قبلاً تعریف کرده‌ای
                run_advanced_search(session) 
            elif choice == farsi("مشاهده تاریخچه تراکنش‌ها"):
                show_logs(service)
                
    except KeyboardInterrupt:
        console.print(farsi("\n[bold yellow]عملیات توسط کاربر لغو شد.[/bold yellow]"))
    finally:
        session.close()

if __name__ == "__main__":
    main()
