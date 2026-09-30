from sqlalchemy.exc import IntegrityError
from rich.table import Table
from rich.console import Console
import questionary
from sqlalchemy import or_
from inventory_core.database import SessionLocal
from inventory_core.models.product import Product
import sys
sys.stdout.reconfigure(encoding='utf-8')
from bidi.algorithm import get_display
import arabic_reshaper
from inventory_core.crud.product import product_crud
from inventory_core.schemas.product import ProductCreate
from inventory_core.reports import count_low_stock, get_low_stock_report, check_low_stock_alerts
from inventory_core.utils import farsi
from inventory_core.logic import log_event, InventoryService
from inventory_core.models.transaction import TransactionLog



db_session = SessionLocal()
service = InventoryService(db_session)
pending_orders = []


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

def create_product(session):
    while True:
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

        # منوی انتخاب ادامه یا بازگشت
        action = questionary.select(
            farsi("عملیات بعدی را انتخاب کنید:"),
            choices=[
                farsi("ثبت محصول دیگر"),
                farsi("بازگشت به منوی اصلی")
            ]
        ).ask()

        if action != farsi("ثبت محصول دیگر"):
            break
def add_stock(service):
    pid_text = get_safe_input("شناسه محصول (ID)")
    if pid_text is None:
        return

    qty_text = get_safe_input("تعداد ورودی")
    if qty_text is None:
        return

    price_text = get_safe_input("قیمت خرید")
    if price_text is None:
        return

    batch_name = get_safe_input("نام/شناسه بهر (Batch)")
    if batch_name is None:
        return
    min_stock_text = get_safe_input("حداقل موجودی (اینتر = 1)")
    if min_stock_text is None:
        return
    min_stock = int(min_stock_text) if min_stock_text.strip().isdigit() else 5

    try:
        service.add_stock(
            int(pid_text),
            int(qty_text),
            float(price_text),
            batch_name,
            min_stock  # در صورتی که سرویس این آرگومان را بپذیرد
        )
        console.print(farsi("[bold green]✅ موجودی با موفقیت اضافه شد.[/bold green]"))
    except Exception as error:
        console.print(farsi(f"[bold red]❌ ناموفق: {error}[/bold red]"))
def issue_stock(service):
    pid_text = get_safe_input("شناسه محصول (ID)")
    if pid_text is None: return

    qty_text = get_safe_input("تعداد خروجی")
    if qty_text is None: return

    reason = get_safe_input("دلیل خروج")
    if reason is None: return

    try:
        # فراخوانی متدِ کلاس InventoryService
        service.issue_stock(int(pid_text), int(qty_text), reason)
        console.print(farsi("[bold green]✅ کالا با موفقیت خارج شد.[/bold green]"))
    except Exception as error:
        console.print(farsi(f"[bold red]❌ ناموفق: {error}[/bold red]"))

def run_advanced_search(service: InventoryService):
    while True:
        term = input(farsi("\nعبارت جستجو (نام یا SKU) [یا '0' برای بازگشت]: ")).strip()
        
        # شرط خروج از حلقه جستجو
        if term in ("0", "q", "exit"):
            break
            
        if not term:
            print(farsi("⚠️  خطا: عبارت جستجو نمی‌تواند خالی باشد."))
            continue

        results = service.search_products(term)
        
        if not results:
            print(farsi(f"❌ نتیجه‌ای برای «{term}» یافت نشد. لطفاً عبارت دیگری را امتحان کنید."))
        else:
            print(farsi(f"\n✅ نتایج جستجو برای «{term}» ({len(results)} مورد):"))
            print("-" * 50)
            for p in results:
                print(f"ID: {p.id} | SKU: {p.sku} | Name: {p.name} | Stock: {p.quantity}")
            print("-" * 50)


def main():
    session = session = SessionLocal()
    service = InventoryService(session)
    pending_orders = []

    # بخش هشدار اولیه در استارتاپ
    low_count = count_low_stock(session)
    if low_count > 0:
        print(farsi(f"⚠️ هشدار: {low_count} کالا با موجودی بحرانی وجود دارد!"))
        choice = input(farsi("آیا مایل به مشاهده آن‌ها هستید؟ (y/n): ")).strip().lower()
        if choice == 'y':
            items = get_low_stock_report(session)
            for item in items:
                min_limit = item.min_stock if item.min_stock is not None else 1
                print(farsi(f"- کالا: {item.name} | موجودی: {item.quantity} | حداقل مجاز: {min_limit}"))
            input(farsi("\nبرای ورود به منو کلید Enter را بزنید..."))

    try:
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
                    farsi("ثبت سفارش کسری‌ها"),
                    farsi("مشاهده لیست سفارش‌های در انتظار"),
                    farsi("ثبت نهایی"),
                    farsi("گزارش موجودی کم (Export to CSV)"),
                    farsi("خروج")
                ]
            ).ask()

            if choice is None or choice == farsi("خروج"):
                console.print(farsi("[bold red]سیستم متوقف شد.[/bold red]"))
                break

            # ۱. ایجاد محصول
            if choice == farsi("ایجاد محصول جدید"):
                create_product(session)

            # ۲. افزایش موجودی
            elif choice == farsi("افزودن کالا"):
                add_stock(service)
                questionary.press_any_key_to_continue(farsi("برای بازگشت کلید بزنید...")).ask()

            # ۳. خروج موجودی
            elif choice == farsi("خروج کالا"):
                issue_stock(service)
                questionary.press_any_key_to_continue(farsi("برای بازگشت کلید بزنید...")).ask()

            # ۴. مشاهده موجودی کل
            elif choice == farsi("مشاهده موجودی"):
                display_status(session)
                questionary.press_any_key_to_continue(farsi("\nبرای بازگشت کلید بزنید...")).ask()

            # ۵. جستجوی پیشرفته
            elif choice == farsi("جستجوی پیشرفته"):
                run_advanced_search(service)

            # ۶. مشاهده تاریخچه تراکنش‌ها
            elif choice == farsi("مشاهده تاریخچه تراکنش‌ها"):
                page = 1
                while True:
                    service.show_logs(page=page)
                
                    print("\n" + farsi("1. صفحه بعد (Next Page)"))
                    print(farsi("2. حذف یک تراکنش (Delete Transaction)"))
                    print(farsi("3. پاکسازی کامل لاگ‌ها (Clear All)"))
                    print(farsi("4. بازگشت (Exit)"))
                    
                    cmd = questionary.text(farsi("لطفاً گزینه مورد نظر را انتخاب کنید: ")).ask()
                    
                    if cmd == "1":
                        page += 1
                    elif cmd == "2":
                        tid = questionary.text(farsi("شناسه تراکنش برای حذف را وارد کنید: ")).ask()
                        pwd = questionary.text(farsi("رمز عبور مدیریت را وارد کنید: ")).ask()
                        if service.delete_transaction(int(tid), pwd):
                            print(farsi("تراکنش با موفقیت حذف شد."))
                        else:
                            print(farsi("خطا: رمز عبور اشتباه است یا شناسه وجود ندارد."))
                        questionary.press_any_key_to_continue(farsi("برای ادامه کلید بزنید...")).ask()
                    elif cmd == "3":
                        pwd = questionary.text(farsi("رمز عبور مدیریت برای پاکسازی کل لاگ‌ها: ")).ask()
                        if service.clear_all_logs(pwd):
                            print(farsi("تمامی تاریخچه تراکنش‌ها با موفقیت پاک شدند."))
                        else:
                            print(farsi("خطا: رمز عبور مدیریت نادرست است."))
                        questionary.press_any_key_to_continue(farsi("برای ادامه کلید بزنید...")).ask()
                    else:
                        break

            # ۷. ثبت سفارش کسری‌ها
            elif choice == farsi("ثبت سفارش کسری‌ها"):
                items = get_low_stock_report(session)
                if not items:
                    console.print(farsi("[bold green]✔ تمام کالاها موجودی کافی دارند.[/bold green]"))
                else:
                    item_choices = [
                        questionary.Choice(
                            title=farsi(f"{item.name} (موجودی فعلی: {item.quantity})"),
                            value=item
                        )
                        for item in items
                    ]
                    item_choices.append(questionary.Choice(title=farsi("بازگشت"), value=None))

                    selected_product = questionary.select(
                        message=farsi("کالای مورد نظر برای سفارش را انتخاب کنید:"),
                        choices=item_choices
                    ).ask()

                    if selected_product:
                        order_qty_str = questionary.text(
                            message=farsi(f"تعداد مورد نیاز برای «{selected_product.name}» را وارد کنید:")
                        ).ask()

                        if order_qty_str and order_qty_str.strip().isdigit() and int(order_qty_str.strip()) > 0:
                            pending_orders.append({
                                "product_id": selected_product.id,
                                "product_name": selected_product.name,
                                "order_qty": int(order_qty_str.strip())
                            })
                            console.print(farsi("[bold green]✔ به لیست سفارش اضافه شد.[/bold green]"))
                        else:
                            console.print(farsi("[bold red]❌ تعداد وارد شده نامعتبر است.[/bold red]"))

                questionary.press_any_key_to_continue(farsi("برای بازگشت کلید بزنید...")).ask()

            # ۸. مشاهده سفارش‌های در انتظار
            elif choice == farsi("مشاهده لیست سفارش‌های در انتظار"):
                if not pending_orders:
                    console.print(farsi("[bold yellow]لیست سفارش‌های در انتظار خالی است.[/bold yellow]"))
                else:
                    console.print(farsi("\n[bold cyan]--- لیست سفارش‌های ثبت‌شده برای تامین ---[/bold cyan]"))
                    for idx, order in enumerate(pending_orders, start=1):
                        console.print(
                            farsi(f"{idx}. کالا: {order['product_name']} | شناسه: {order['product_id']} | تعداد سفارش: {order['order_qty']}")
                        )
                questionary.press_any_key_to_continue(farsi("\nبرای بازگشت کلید بزنید...")).ask()

            # ۹. ثبت نهایی
            elif choice == farsi("ثبت نهایی"):
                if not pending_orders:
                    console.print(farsi("[yellow]هیچ سفارشی در لیست موقت وجود ندارد.[/yellow]"))
                else:
                    remaining_orders = []
                    for item in pending_orders:
                        confirm = questionary.confirm(
                            farsi(f"آیا ثبت نهایی «{item['product_name']}» به تعداد {item['order_qty']} تایید می‌شود؟")
                        ).ask()

                        if confirm:
                            service.receive_order(item["product_id"], item["order_qty"])
                            console.print(farsi(f"[bold green]✔ «{item['product_name']}» با موفقیت ثبت شد.[/bold green]"))
                        else:
                            remaining_orders.append(item)
                            console.print(farsi(f"[yellow]«{item['product_name']}» در لیست انتظار باقی ماند.[/yellow]"))

                    pending_orders = remaining_orders
                questionary.press_any_key_to_continue(farsi("برای بازگشت کلید بزنید...")).ask()
            elif choice == farsi("گزارش موجودی کم (Export to CSV)"):
                from inventory_core.reports import export_low_stock
                export_low_stock(session)
                console.print(farsi("[bold green]✔ گزارش موجودی کم به فایل low_stock.csv صادر شد.[/bold green]"))
                questionary.press_any_key_to_continue(farsi("برای بازگشت کلید بزنید...")).ask()

    except KeyboardInterrupt:
        console.print(farsi("\n[bold yellow]عملیات توسط کاربر لغو شد.[/bold yellow]"))
    finally:
        session.close()

if __name__ == "__main__":
    main()
