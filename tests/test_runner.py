import requests

BASE_URL = "http://127.0.0.1:8000"


def test_inventory_api():
  session = requests.Session()

  # 1. Register User
  reg_res = session.post(
      f"{BASE_URL}/register",
      json={"username": "shahab_admin", "password": "securepassword123"},
  )
  print(f"Register Status: {reg_res.status_code}")
  try:
    print(reg_res.json())
  except Exception:
    print(reg_res.text)

  # 2. Login for Token (OAuth2 Form Data & Content-Type)
  token_res = session.post(
      f"{BASE_URL}/token",
      data={
          "username": "shahab_admin",
          "password": "securepassword123",
      },
      headers={"Content-Type": "application/x-www-form-urlencoded"},
  )
  print(f"Token Status: {token_res.status_code}")

  if token_res.status_code != 200:
    print("Token Error Response:", token_res.text)
    return

  token_data = token_res.json()
  access_token = token_data.get("access_token")
  headers = {"Authorization": f"Bearer {access_token}"}

  # 3. Get Current User
  me_res = session.get(f"{BASE_URL}/users/me", headers=headers)
  print(f"Users Me: {me_res.status_code}", me_res.json())

  # 4. Create Product
  prod_res = session.post(
      f"{BASE_URL}/products",
      headers=headers,
      json={
          "name": "Python Book",
          "sku": "BK-PY-01",
          "price": 450000,
          "quantity": 10,
      },
  )
  print(f"Create Product: {prod_res.status_code}")
  prod_data = prod_res.json()
  product_id = prod_data.get("id")

  # 5. Get Products List
  list_res = session.get(f"{BASE_URL}/products", headers=headers)
  print(
      f"Get Products: {list_res.status_code}, Count:", len(list_res.json())
  )

  # 6. Create Stock Movement (Transaction)
  trans_res = session.post(
      f"{BASE_URL}/transactions",
      headers=headers,
      json={
          "product_id": product_id,
          "movement_type": "IN",
          "quantity": 5,
          "reference": "Restock",
      },
  )
  print(f"Create Transaction: {trans_res.status_code}", trans_res.json())

  # 7. Get Inventory Report
  rep_res = session.get(f"{BASE_URL}/inventory/report", headers=headers)
  print(f"Inventory Report: {rep_res.status_code}", rep_res.json())

  # 8. Export CSV Report
  csv_res = session.get(f"{BASE_URL}/reports/inventory/csv", headers=headers)
  print(f"Export CSV Status: {csv_res.status_code}")


if __name__ == "__main__":
  test_inventory_api()
