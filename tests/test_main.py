from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_headers():
    login = client.post(
        "/auth/login",
        data={
            "username": "kevin@example.com",
            "password": "123456",
        },
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login():
    response = client.post(
        "/auth/login",
        data={
            "username": "kevin@example.com",
            "password": "123456",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_me():
    headers = get_auth_headers()
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "kevin@example.com"


def test_protected_route_requires_auth():
    response = client.get("/products/")
    assert response.status_code == 401


def test_get_products_with_auth():
    headers = get_auth_headers()
    response = client.get("/products/", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_order_invalid_dates():
    headers = get_auth_headers()

    response = client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "product_id": 1,
            "quantity": 2,
            "currency": "USD",
            "created_by": 4,
            "expected_ship_date": "2026-05-10T10:00:00",
            "expected_delivery_date": "2026-05-02T10:00:00",
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert "Expected delivery date cannot be earlier" in response.json()["detail"]


def test_create_order_calculates_total_amount():
    headers = get_auth_headers()

    response = client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "product_id": 1,
            "quantity": 3,
            "currency": "USD",
            "created_by": 4,
            "expected_ship_date": "2026-05-01T10:00:00",
            "expected_delivery_date": "2026-05-05T10:00:00",
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["unit_price"] == 12.5
    assert data["total_amount"] == 37.5
    assert data["order_status"] == "draft"
    assert data["shipment_status"] == "pending"


def test_analytics_orders_by_status():
    headers = get_auth_headers()

    response = client.get("/analytics/orders-by-status", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert "order_status" in response.json()[0]
    assert "count" in response.json()[0]


def test_shipment_summary_requires_auth():
    response = client.get("/analytics/shipment-summary")
    assert response.status_code == 401