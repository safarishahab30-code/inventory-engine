# 📦 Inventory Engine

یک سیستم مدیریت انبار (CLI) ماژولار و بهینه، توسعه‌یافته با Python 3.10+ جهت اتوماسیون عملیات موجودی و پیگیری دقیق تراکنش‌های کالا.

## 🚀 ویژگی‌های کلیدی
- **معماری ماژولار:** تفکیک کامل لایه‌های ORM، Logic و CLI.
- **تضمین سلامت داده‌ها:** استفاده از **Pydantic V2** برای اعتبارسنجی دقیق داده‌ها.
- **مدیریت هوشمند دیتابیس:** استفاده از **SQLAlchemy 2.0** برای ارتباطی امن و مقیاس‌پذیر.
- **رابط کاربری تعاملی:** طراحی مدرن CLI با **Typer** و خروجی‌های خوانا با **Rich**.
- **پایداری:** دارای تست‌های خودکار (**Pytest**) برای تضمین عملکردِ تراکنش‌ها.

## 🏗 ساختار پروژه
```text
inventory-engine/
├── cli/          # مدیریت دستورات ترمینال
├── crud/         # توابع عملیاتی دیتابیس
├── models/       # تعریف جداول (SQLAlchemy)
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
🚀 راه‌اندازی سریع
۱. کلون پروژه:

bash
git clone https://github.com/safarishah30-code/inventory-engine.git
cd inventory-engine
۲. ایجاد محیط مجازی و نصب پیش‌نیازها:

bash
python -m venv venv
source venv/bin/activate  # در ویندوز: venv\Scripts\activate
pip install -r requirements.txt
۳. اجرای برنامه:

bash
python app_cli.py --help
توسعه‌یافته توسط شهاب صفری

text

### ۲. حذف فایل‌های دیتابیس لوکال (بسیار مهم)
اگر فایل‌هایی با پسوند `.db` یا `.sqlite` در پوشه اصلی داری، نباید به گیت‌هاب بروند. دیتابیس هر کس باید روی سیستم خودش ساخته شود.

### ۳. ارسال نهایی به گیت‌هاب
ترمینال را باز کن و این ۳ دستور را بزن تا همه‌چیز مرتب شود:

```bash
# ۱. اضافه کردن تغییرات README
git add README.md

# ۲. ثبت تغییرات با پیام حرفه‌ای
git commit -m "docs: finalize professional README and project structure"

# ۳. ارسال به سرور
git push origin main