Set-Content -Path README.md -Value @"
# 📦 موتور مدیریت انبارداری (Inventory Engine)

یک سیستم مدیریت انبار و گردش موجودی (CLI) ماژولار، توسعه‌یافته با **Python 3.13** جهت اتوماسیون عملیات انبارداری، پیگیری دقیق تراکنش‌های کالا و انبارگردانی.

<<<<<<< HEAD
---

## ✨ ویژگی‌های کلیدی
- **معماری ماژولار و ساختاریافته:** تفکیک کامل لایه‌های مدل داده (ORM)، منطق تجاری (Business Logic) و رابط کاربری خط فرمان (CLI).
- **مدیریت هوشمند دیتابیس:** استفاده از **SQLAlchemy 2.0** برای ارتباط ایمن و تراکنش‌های پایدار با پایگاه‌داده SQLite.
- **تضمین سلامت و اعتبارسنجی داده‌ها:** جلوگیری خودکار از قیمت‌های منفی، موجودی نامعتبر و ورودی‌های خالی پیش از ثبت در دیتابیس.
- **ردیابی دقیق گردش موجودی (Stock Movements):** ثبت تراکنش‌های ورود (``IN``)، خروج (``OUT``) و تعدیل موجودی (``ADJUSTMENT``) با ثبت دلایل و زمان دقیق.
- **قوانین سخت‌گیرانه کسری کالا:** جلوگیری در لایه منطق تجاری از منفی شدن موجودی انبار هنگام خروج کالا.
- **رابط خط فرمان تعاملی:** طراحی مدرن CLI با خروجی‌های خوانا و جدولی در ترمینال با کتابخانه **Rich**.
- **پایداری بالا:** پوشش کامل توابع و منطق اصلی سیستم با ۱۱ تست خودکار با **Pytest**.

---

## 🏗 مدل داده و ارتباط موجودیت‌ها (ERD)

\`\`\`mermaid
erDiagram
    PRODUCT ||--o{ STOCK_MOVEMENT : tracks
    PRODUCT ||--o{ STOCK_BATCH : contains

    PRODUCT {
        int id PK
        string sku UK
        string name
        string category
        float price
        float selling_price
        int quantity
        int min_stock
        string barcode
    }

    STOCK_MOVEMENT {
        int id PK
        int product_id FK
        int change_qty
        string movement_type
        string reason
        datetime created_at
    }

    STOCK_BATCH {
        int id PK
        int product_id FK
        string batch_number
        int quantity
        datetime expiry_date
    }
\`\`\`

---

## 📁 ساختار پروژه

\`\`\`text
=======
## 🚀 ویژگی‌های کلیدی

- **معماری ماژولار:** تفکیک کامل لایه‌های ORM، Logic و CLI.
- **تضمین سلامت داده‌ها:** استفاده از **Pydantic V2** برای اعتبارسنجی دقیق داده‌ها.
- **مدیریت هوشمند دیتابیسمندمد:** استفاده از **SQLAlchemy 2.0** برای ارتباطی امن و مقیاس‌پذیر.
- **رابط کاربری تعاملی:** طراحی مدرن CLI با **Typer** و خروجی‌های خوانا با **Rich**.
- **پایداری:** دارای تست‌های خودکار (**Pytest**) برای تضمین عملکردِ تراکنش‌ها.

## 🏗 ساختار پروژه

```text
>>>>>>> 144faf0 (feat(api): add FastAPI web layer for products CRUD with E2E test suite)
inventory-engine/
├── inventory_core/       # بسته اصلی و لایه‌های تجاری
│   ├── models/           # مدل‌های دیتابیس (Product, StockMovement, StockBatch)
│   ├── crud/             # عملیات پایگاه داده (CRUD)
│   └── ...
├── tests/                # تست‌های واحد و یکپارچگی (Pytest)
│   ├── test_crud.py
│   ├── test_inventory_logic.py
│   └── test_validation.py
├── app_cli.py            # رابط متنی و مدیریت فرمان‌ها
├── main.py               # فایل اجرایی سیستم
├── init_db.py            # مقداردهی اولیه پایگاه داده
└── requirements.txt      # پیش‌نیازهای پروژه
\`\`\`

---

## 🛠 تکنولوژی‌ها و ابزارها
- **زبان:** Python 3.13
- **پایگاه داده و ORM:** SQLite / SQLAlchemy 2.0
- **تست خودکار:** Pytest 9.x
- **رابط خط فرمان:** Rich / Typer / Tabulate
- **گزارش‌گیری:** OpenPyXL / Python-Dateutil

---

## 🚀 راهنمای راه‌اندازی سریع

### ۱. دریافت پروژه
\`\`\`bash
git clone https://github.com/safarishahab30-code/inventory-engine.git
cd inventory-engine
\`\`\`

### ۲. فعال‌سازی محیط مجازی و نصب وابستگی‌ها
\`\`\`powershell
# ویندوز (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
\`\`\`

### ۳. آماده‌سازی دیتابیس و اجرا
\`\`\`powershell
python init_db.py
python main.py
\`\`\`

---

## 🧪 نتایج تست‌های خودکار (Pytest Suite)

اجرای ۱۱ تست پایدار پوشش‌دهنده عملیات CRUD، منطق انبار و اعتبارسنجی‌ها:

\`\`\`bash
$env:PYTHONPATH="."
pytest tests/ -v
\`\`\`

\`\`\`text
rootdir: C:\webscrapper\inventory-engine
configfile: pytest.ini
collected 11 items

<<<<<<< HEAD
tests/test_crud.py::test_create_and_get_product PASSED                     [  9%]
tests/test_crud.py::test_update_product_quantity PASSED                    [ 18%]
tests/test_crud.py::test_update_missing_product_returns_none PASSED        [ 27%]
tests/test_crud.py::test_delete_product PASSED                             [ 36%]
tests/test_crud.py::test_delete_missing_product_returns_false PASSED       [ 45%]
tests/test_inventory_logic.py::test_add_stock_increases_product_quantity PASSED [ 54%]
tests/test_inventory_logic.py::test_record_stock_movement_in_and_out PASSED     [ 63%]
tests/test_inventory_logic.py::test_record_stock_movement_negative_stock_prevented PASSED [ 72%]
tests/test_validation.py::test_create_product_with_negative_price PASSED    [ 81%]
tests/test_validation.py::test_create_product_with_negative_quantity PASSED [ 90%]
tests/test_validation.py::test_create_product_with_empty_name PASSED       [100%]

============================== 11 passed in 0.06s ===============================
\`\`\`
"@ -Encoding UTF8
=======
# ۳. ارسال به سرور
git push origin main
```
>>>>>>> 144faf0 (feat(api): add FastAPI web layer for products CRUD with E2E test suite)
