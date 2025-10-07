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
