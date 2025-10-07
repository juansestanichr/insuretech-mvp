"""High level smoke tests for the public FastAPI endpoints.

The repository is organised so that the application code lives in ``backend/app``.
When pytest executes from the ``backend`` directory the package is importable as
``app``. Some environments, however, run pytest from the repository root or
without automatically adding the current working directory to ``sys.path``. To
ensure the tests always run (for example on GitHub Actions) we explicitly append
the parent directory of this test file to ``sys.path`` before importing the
FastAPI application.
"""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_quote():
    payload = {
        "customer_id": "c1",
        "age": 30,
        "vehicle_value": 15000.0,
        "prior_claims": 0,
        "credit_score": 680,
        "gender": "F"
    }
    r = client.post("/quote", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "probability_of_loss" in data
    assert "final_premium" in data
    assert data["decision"] in {"auto_approve","refer","reject"}


def test_customer_and_marketing_flow():
    customer_payload = {
        "customer_id": "cust-123",
        "name": "Alex Johnson",
        "email": "alex@example.com",
        "phone": "+1234567890",
    }
    r = client.post("/customers", json=customer_payload)
    assert r.status_code == 200
    stored = r.json()
    assert stored["customer_id"] == customer_payload["customer_id"]
    assert stored["email"] == customer_payload["email"]

    r = client.get(f"/customers/{customer_payload['customer_id']}")
    assert r.status_code == 200
    fetched = r.json()
    assert fetched == stored

    marketing_payload = {"customer_id": customer_payload["customer_id"], "product": "Smart Auto"}
    r = client.post("/marketing/outreach", json=marketing_payload)
    assert r.status_code == 200
    message = r.json()["message"]
    assert customer_payload["name"] in message
