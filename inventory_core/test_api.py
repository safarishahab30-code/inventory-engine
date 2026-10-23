import requests

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("==================================================")
    print("--- شروع تست جامع و کامل تمام بخش‌های سرور Inventory Engine ---")
    print("==================================================")

    # 1. تست دریافت محصولات
    resp = requests.get(f"{BASE_URL}/products")
    print(f"[1] GET /products --> Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"    تعداد کل محصولات موجود: {len(resp.json())}")

    # 2. تست ثبت محصول جدید
    new_product_data = {
        "sku": "FULL-TEST-099",
        "name": "کتاب جامع تست پایتون و هوش مصنوعی",
        "price": 450000.0,
        "selling_price": 520000.0,
        "quantity": 25,
        "min_stock": 5,
        "category": "فنی و مهندسی",
        "unit": "عدد"
    }
    resp = requests.post(f"{BASE_URL}/products", json=new_product_data)
    print(f"[2] POST /products --> Status: {resp.status_code}")
    print(f"    نتیجه ثبت محصول جدید: {resp.json()}")

    # 3. دریافت توکن برای احراز هویت تراکنش‌ها
    token_resp = requests.post(f"{BASE_URL}/token", data={"username": "admin", "password": "form_data.password"})
    token = token_resp.json().get("access_token") if token_resp.status_code == 200 else None
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # 4. تست ثبت تراکنش انبار (به جای مسیر منسوخ شده بچ/فروش)
    transaction_data = {
        "product_id": 9,
        "quantity": 2,
        "movement_type": "OUT",
        "notes": "تست خروج انبار"
    }
    resp = requests.post(f"{BASE_URL}/transactions", json=transaction_data, headers=headers)
    print(f"[3] POST /transactions --> Status: {resp.status_code}")
    print(f"    نتیجه ثبت تراکنش: {resp.json()}")

    # 5. تست گزارش موجودی انبار
    resp = requests.get(f"{BASE_URL}/inventory/report")
    print(f"[4] GET /inventory/report --> Status: {resp.status_code}")
    print(f"    گزارش انبار: {resp.json()}")

    # 6. تست اقلام زیر حد آستانه (Reorders)
    resp = requests.get(f"{BASE_URL}/reorders")
    print(f"[5] GET /reorders --> Status: {resp.status_code}")
    print(f"    اقلام زیر حد آستانه: {resp.json()}")

    print("==================================================")
    print("--- تست جامع به پایان رسید ---")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
