# test_inventory_api.py
import json
import sys
import time
from dataclasses import dataclass
from typing import Any, Optional
import requests


def farsi(text: str) -> str:
    return text


BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 10


@dataclass
class TestResult:
    name: str
    ok: bool
    details: str = ""


def pretty(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def request_json(method: str, url: str, *, expected_status: Optional[int] = None, **kwargs):
    r = requests.request(method, url, timeout=TIMEOUT, **kwargs)
    if expected_status is not None and r.status_code != expected_status:
        raise AssertionError(
            f"Expected {expected_status} but got {r.status_code}.\n"
            f"URL: {url}\n"
            f"Response: {r.text}"
        )
    if r.status_code == 204 or not r.text.strip():
        return r, None
    try:
        return r, r.json()
    except Exception:
        raise AssertionError(f"Response is not JSON.\nURL: {url}\nBody: {r.text}")


def main():
    results = []
    created_id = None

    try:
        # 1) GET /products
        t0 = time.time()
        r, data = request_json("GET", f"{BASE_URL}/products", expected_status=200)
        results.append(TestResult(
            name="GET /products",
            ok=True,
            details=f"count={len(data) if isinstance(data, list) else 'unknown'}"
        ))

        # 2) POST /products (تطبیق با وضعیت 210 سرور)
        sku = str(int(time.time()))
        payload = {
            "sku": sku,
            "name": "test product",
            "price": 0,
            "selling_price": 160000,
            "quantity": 1,
            "category": "test",
            "unit": "عدد",
        }
        r, data = request_json("POST", f"{BASE_URL}/products", json=payload, expected_status=210)
        if not isinstance(data, dict) or "id" not in data:
            raise AssertionError(f"POST response missing id:\n{pretty(data)}")

        created_id = data["id"]
        results.append(TestResult(
            name="POST /products",
            ok=True,
            details=f"created_id={created_id}, sku={sku}"
        ))

        # 3) GET /products/{id}
        r, data = request_json("GET", f"{BASE_URL}/products/{created_id}", expected_status=200)
        if data.get("id") != created_id:
            raise AssertionError(f"GET by id mismatch:\n{pretty(data)}")
        results.append(TestResult(
            name="GET /products/{id}",
            ok=True,
            details=f"name={data.get('name')}"
        ))

        # 4) PUT /products/{id} (Partial Update)
        new_name = "baba salam v2"
        r, data = request_json("PUT", f"{BASE_URL}/products/{created_id}",
                               json={"name": new_name}, expected_status=200)
        if data.get("name") != new_name:
            raise AssertionError(f"PUT did not update name:\n{pretty(data)}")
        results.append(TestResult(
            name="PUT /products/{id} (partial)",
            ok=True,
            details=f"updated_name={data.get('name')}"
        ))

        # 5) DELETE /products/{id}
        r, _ = request_json("DELETE", f"{BASE_URL}/products/{created_id}", expected_status=204)
        results.append(TestResult(
            name="DELETE /products/{id}",
            ok=True,
            details="deleted (204)"
        ))

        # 6) GET /products/{id} (Verify 404)
        r = requests.get(f"{BASE_URL}/products/{created_id}", timeout=TIMEOUT)
        if r.status_code != 404:
            raise AssertionError(
                f"Expected 404 after delete but got {r.status_code}.\nBody: {r.text}"
            )
        results.append(TestResult(
            name="GET /products/{id} after delete",
            ok=True,
            details="404 verified"
        ))

        elapsed = time.time() - t0

        print(farsi("✅ همه تست‌ها با موفقیت انجام شد"))
        print(farsi(f"زمان اجرا: {elapsed:.2f} ثانیه"))
        print(farsi("خلاصه:"))
        for tr in results:
            print(f"- {tr.name}: OK | {tr.details}")

    except Exception as e:
        print(farsi("❌ تست‌ها شکست خورد"))
        print(farsi(str(e)))

        if created_id is not None:
            try:
                requests.delete(f"{BASE_URL}/products/{created_id}", timeout=TIMEOUT)
                print(farsi(f"پاکسازی انجام شد: محصول {created_id} حذف شد"))
            except Exception:
                print(farsi("پاکسازی انجام نشد (حذف محصول ناموفق بود)"))

        sys.exit(1)


if __name__ == "__main__":
    main()
