import uuid

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def make_supplier_payload(prefix: str = "pending"):
    unique = uuid.uuid4().hex[:10]
    return {
        "supplier_id": f"sup_{prefix}_{unique}",
        "email": f"{prefix}_{unique}@example.com",
        "company_name": f"{prefix.title()} Company",
        "contact_person": "Jane Supplier",
        "password": "ValidPass123!@",
        "phone": "9876543210",
        "address": "123 Test Street, Bengaluru",
        "gst_number": "27AABCT1234H1Z0",
    }


def test_supplier_registration_starts_in_pending_status_and_blocks_login():
    payload = make_supplier_payload("pending")

    reg = client.post("/supplier/register", json=payload)
    assert reg.status_code == 200, reg.text
    body = reg.json()
    assert body["is_approved"] == 0

    login = client.post(
        "/supplier/login",
        json={"supplier_id_or_email": payload["email"], "password": payload["password"]},
    )

    assert login.status_code == 403, login.text
    assert "approval" in login.json()["detail"].lower()


def test_admin_can_approve_supplier_and_login_allowed():
    payload = make_supplier_payload("approve")

    reg = client.post("/supplier/register", json=payload)
    assert reg.status_code == 200, reg.text
    supplier_id = reg.json()["supplier_id"]

    approve = client.post(f"/supplier/approve/{supplier_id}", json={"status": "approved"})
    assert approve.status_code == 200, approve.text
    assert approve.json()["is_approved"] == 1

    login = client.post(
        "/supplier/login",
        json={"supplier_id_or_email": payload["email"], "password": payload["password"]},
    )

    assert login.status_code == 200, login.text
    assert login.json()["supplier_id"] == supplier_id
