import subprocess, sys, os, sqlite3, importlib, time, urllib.request, json

farsi = lambda s: s  # اگر farsi() داری، از utils ایمپورت کن
OK, FAIL = "[OK]", "[FAIL]"
results = []

def record(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"{OK if ok else FAIL} {name}" + (f" -> {detail}" if detail else ""))

# ---------- 1) Import Check ----------
MODULES = [
    "inventory_core", "inventory_core.database",
    "inventory_core.models.product", "inventory_core.models.stock_batch",
    "inventory_core.models.stock_movement", "inventory_core.models.transaction",
    "inventory_core.reports", "app_cli", "web_server",
]
print(farsi("\n=== 1) بررسی ایمپورت ماژول‌ها ==="))
for m in MODULES:
    try:
        importlib.import_module(m)
        record(f"import {m}", True)
    except Exception as e:
        record(f"import {m}", False, repr(e))

# ---------- 2) pytest ----------
print(farsi("\n=== 2) اجرای pytest ==="))
r = subprocess.run([sys.executable, "-m", "pytest", "tests", "-v", "--tb=short"],
                   capture_output=True, text=True)
record("pytest", r.returncode == 0, f"exit={r.returncode}")
print(r.stdout[-2000:] if r.stdout else r.stderr[-1000:])

# ---------- 3) Database Integrity ----------
print(farsi("\n=== 3) بررسی دیتابیس ==="))
DB_CANDIDATES = ["inventory.db", "inventory_engine.db", "data/inventory.db"]
db_path = next((p for p in DB_CANDIDATES if os.path.exists(p)), None)
if db_path:
    conn = sqlite3.connect(db_path)
    tables = [row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")]
    record("database file", True, f"{db_path} | tables={tables}")
    for t in ["products", "stock_batches", "stock_movements", "transactions"]:
        if t in tables:
            n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            record(f"table {t}", True, f"rows={n}")
        else:
            record(f"table {t}", False, "missing")
    # تست FK
    fk = conn.execute("PRAGMA foreign_key_check").fetchall()
    record("foreign key check", not fk, f"violations={len(fk)}")
    conn.close()
else:
    record("database file", False, "هیچ فایل db پیدا نشد")

# ---------- 4) CLI Smoke Test ----------
print(farsi("\n=== 4) تست CLI ==="))
CLI_CMDS = [["--help"], ["list"], ["low-stock"]]
for cmd in CLI_CMDS:
    r = subprocess.run([sys.executable, "app_cli.py"] + cmd,
                       capture_output=True, text=True, timeout=30)
    record(f"cli {' '.join(cmd)}", r.returncode == 0,
           (r.stderr.strip().splitlines() or [""])[-1][:100])

# ---------- 5) Web Server ----------
print(farsi("\n=== 5) تست وب‌سرور (اختیاری) ==="))
r = subprocess.run([sys.executable, "-m", "py_compile", "web_server.py"],
                   capture_output=True, text=True)
record("web_server compile", r.returncode == 0, r.stderr[:100])

# ---------- خلاصه ----------
print(farsi("\n" + "=" * 50))
passed = sum(1 for _, ok, _ in results if ok)
print(farsi(f"نتیجه نهایی: {passed}/{len(results)} موفق"))
for name, ok, detail in results:
    if not ok:
        print(f"{FAIL} {name} -> {detail}")
