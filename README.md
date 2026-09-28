# Inventory Engine

یک سیستم مدیریت انبار (CLI) ماژولار و بهینه، توسعه‌یافته با Python 3.10+ جهت اتوماسیون عملیات موجودی و پیگیری دقیق تراکنش‌های کالا.

## 🚀 ویژگی‌های فنی (Key Features)
- **معماری ماژولار:** تفکیک کامل لایه‌های ORM، Logic و CLI.
- **تضمین سلامت داده‌ها:** استفاده از **Pydantic V2** برای اعتبارسنجی ورودی‌ها (Schema Validation).
- **مدیریت دیتابیس:** استفاده از **SQLAlchemy 2.0** برای ارتباطی امن و مقیاس‌پذیر با پایگاه داده.
- **رابط کاربری تعاملی:** طراحی CLI با استفاده از **Typer** و خروجی‌های خوانا با **Rich**.
- **تست‌محور:** دارای تست‌های خودکار (Pytest) برای تضمین عملکرد صحیح CRUD.

`

markdown
## 🏗 ساختار پروژه
```text
inventory-engine/
├── cli/          # مدیریت دستورات ترمینال
├── crud/         # توابع عملیاتی دیتابیس
├── models/       # تعریف جداول و روابط (ORM)
├── schemas/      # مدل‌های اعتبارسنجی (Pydantic)
├── tests/        # تست‌های واحد و یکپارچگی
├── app_cli.py    # نقطه ورود برنامه (Entry point)
└── init_db.py    # اسکریپت اولیه دیتابیس
🛠 تکنولوژی‌ها
Language: Python 3.10+
ORM: SQLAlchemy 2.0
Validation: Pydantic V2
CLI: Typer
UI/Terminal: Rich
Testing: Pytest
🚀 راه‌اندازی (Setup)
کلون مخزن و ورود به پوشه پروژه:
bash
   git clone https://github.com/safarishah30-code/inventory-engine.git
   cd inventory-engine
   
`