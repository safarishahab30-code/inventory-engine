from rich.console import Console
from rich.table import Table
import questionary
from sqlalchemy.exc import IntegrityError

from inventory_core.services.inventory_service import InventoryService
from inventory_core.database import SessionLocal
from inventory_core.crud.product import product_crud
from inventory_core.utils import farsi
from inventory_core.schemas.product import ProductCreate

console = Console()

def get_safe_input(prompt):
    """دریافت ورودی با پردازش farsi."""
    full_prompt = f"{prompt} (برای بازگشت: b)"
    answer = questionary.text(farsi(full_prompt)).ask()

    if answer is None:
        return None

    answer = answer.strip()
    if not answer or answer.lower() in {"b", "back", "بازگشت"}:
        return None
    return answer

def display_status(session):
    """نمایش وضعیت فعلی موجودی."""
    products = product_crud.get_multi(session)
    table = Table(title=farsi("وضعیت فعلی انبار"))
    table.add_column("ID", style="cyan")
    table.add_column(farsi("نام کالا"), style="magenta")
    table.add_column(farsi("موجودی"), justify="right", style="green")

    for product in products:
        table.add_row(
            str(product.id),
            farsi(product.name),
            str(product.quantity),
        )
    console.print(table)

def create_product(session):
    """ایجاد محصول جدید با مدیریت خطای IntegrityError."""
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
        if price < 0: raise ValueError
        
        new_product = ProductCreate(
            name=name,
            sku=sku,
            category=category,
            price=price,
            selling_price=price,
        )
        product_crud.create(session, obj_in=new_product)
        console.print(farsi("[bold green]✅ محصول با موفقیت ایجاد شد.[/bold green]"))
    except IntegrityError:
        session.rollback()
        console.print(farsi("[bold red]❌ خطا: این SKU قبلاً در سیستم ثبت شده است.[/bold red]"))
    except ValueError:
        console.print(farsi("[bold red]❌ قیمت باید یک عدد معتبر و مثبت باشد.[/bold red]"))
    except Exception as error:
        session.rollback()
        console.print(farsi(f"[bold red]❌ خطا: {error}[/bold red]"))

def add_stock(service):
    """افزودن موجودی."""
    pid_text = get_safe_input("شناسه محصول (ID)")
    if pid_text is None: return
    qty_text = get_safe_input("تعداد ورودی")
    if qty_text is None: return
    price_text = get_safe_input("قیمت خرید")
    if price_text is None: return

    try:
        product_id = int(pid_text)
        quantity = int(qty_text)
        purchase_price = float(price_text)

        if product_id <= 0 or quantity <= 0 or purchase_price < 0:
            raise ValueError

        service.add_stock(product_id, quantity, purchase_price)
        console.print(farsi("[bold green]✅ موجودی با موفقیت اضافه شد.[/bold green]"))
    except ValueError:
        console.print(farsi("[bold red]❌ مقادیر وارد شده نامعتبر هستند.[/bold red]"))
    except Exception as error:
        console.print(farsi(f"[bold red]❌ افزودن موجودی ناموفق بود: {error}[/bold red]"))

def issue_stock(service):
    """کسر موجودی با اعتبارسنجی دقیق."""
    pid_text = get_safe_input("شناسه محصول (ID)")
    if pid_text is None: return
    qty_text = get_safe_input("تعداد خروجی")
    if qty_text is None: return

    try:
        product_id = int(pid_text)
        quantity = int(qty_text)

        if product_id <= 0:
            console.print(farsi("[bold red]❌ شناسه کالا باید بزرگتر از صفر باشد.[/bold red]"))
            return
        if quantity <= 0:
            console.print(farsi("[bold red]❌ تعداد کالا باید بزرگتر از صفر باشد.[/bold red]"))
            return

        service.issue_stock(product_id, quantity)
        console.print(farsi("[bold yellow]⚠️ موجودی کسر شد.[/bold yellow]"))
    except ValueError:
        console.print(farsi("[bold red]❌ ورودی‌ها باید فقط عدد صحیح باشند.[/bold red]"))
    except Exception as error:
        console.print(farsi(f"[bold red]❌ خروج کالا ناموفق بود: {error}[/bold red]"))

def main():
    session = SessionLocal()
    service = InventoryService(session)

    try:
        while True:
            choice = questionary.select(
                farsi("Inventory Engine - پنل مدیریت:"),
                choices=[
                    farsi("ایجاد محصول جدید"),
                    farsi("افزودن کالا"),
                    farsi("خروج کالا"),
                    farsi("مشاهده موجودی"),
                    farsi("خروج")
                ],
            ).ask()

            if choice is None: break

            if choice == farsi("ایجاد محصول جدید"):
                create_product(session)
            elif choice == farsi("افزودن کالا"):
                add_stock(service)
            elif choice == farsi("خروج کالا"):
                issue_stock(service)
            elif choice == farsi("مشاهده موجودی"):
                display_status(session)
                questionary.press_any_key_to_continue(farsi("برای بازگشت کلید بزنید...")).ask()
            elif choice == farsi("خروج"):
                console.print(farsi("[bold red]سیستم متوقف شد.[/bold red]"))
                break
    except KeyboardInterrupt:
        console.print(farsi("\n[bold yellow]عملیات لغو شد.[/bold yellow]"))
    except Exception as error:
        console.print(farsi(f"[bold red]❌ خطا رخ داد: {error}[/bold red]"))
    finally:
        session.close()

if __name__ == "__main__":
    main()
