import sqlite3
from inventory_core.utils import farsi


def add_sample_books():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    books = [
        ("تمیزکاری کُد", "BK-001", 5, 200000, 280000, "جلد", 2),
        ("معماری تمیز", "BK-002", 3, 250000, 350000, "جلد", 2),
        ("برنامه‌نویس عمل‌گرا", "BK-003", 4, 220000, 310000, "جلد", 2),
        ("الگوهای طراحی", "BK-004", 2, 300000, 420000, "جلد", 2),
        ("پایتون پیشرفته", "BK-005", 6, 210000, 290000, "جلد", 2),
        ("جنگو مقدماتی", "BK-006", 8, 180000, 250000, "جلد", 2),
        ("ساختمان داده‌ها", "BK-007", 5, 160000, 220000, "جلد", 2),
        ("طراحی الگوریتم", "BK-008", 4, 170000, 240000, "جلد", 2),
        ("مفاهیم پایگاه داده", "BK-009", 7, 190000, 270000, "جلد", 2),
        ("مهندسی نرم‌افزار", "BK-010", 3, 220000, 300000, "جلد", 2),
    ]

    cursor.executemany(
        """
        INSERT INTO products (name, sku, quantity, price, selling_price, unit, reorder_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        books,
    )

    conn.commit()
    conn.close()
    print(farsi("۱۰ کتاب نمونه با موفقیت به دیتابیس اضافه شدند."))


if __name__ == "__main__":
    add_sample_books()
