from fastapi.testclient import TestClient
from web_server import app

client = TestClient(app)


def test_read_main():
  response = client.get("/")
  # بسته به اینکه ریشه سرور چه مسیری دارد (مثلاً / یا /docs) کد وضعیت بررسی می‌شود
  assert response.status_code in [200, 404]
