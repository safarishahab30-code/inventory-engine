from fastapi.testclient import TestClient
from web_server import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
def test_get_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_inventory_report():
    response = client.get("/inventory/report")
    assert response.status_code in [200, 401]  # بسته به نیاز به احراز هویت
