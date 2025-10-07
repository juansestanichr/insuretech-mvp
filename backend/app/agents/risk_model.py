from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import numpy as np

class RiskModel:
    def __init__(self):
        # Train a tiny synthetic model on init
        rng = np.random.default_rng(42)
        n = 500
        age = rng.integers(18, 80, size=n)
        vehicle_value = rng.normal(20000, 8000, size=n).clip(3000, 80000)
        prior_claims = rng.integers(0, 5, size=n)
        credit_score = rng.integers(500, 800, size=n)
        # ground truth: higher prior_claims & lower credit -> higher risk
        logits = (
            0.015 * (age - 40) +
            0.00002 * (vehicle_value - 20000) +
            0.6 * (prior_claims) +
            -0.01 * (credit_score - 650)
        )
        y = (logits + rng.normal(0, 0.5, size=n) > 0.5).astype(int)

        X = np.vstack([age, vehicle_value, prior_claims, credit_score]).T
        self.pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500))
        self.pipe.fit(X, y)

    def predict_proba(self, payload: dict) -> float:
        age = payload["age"]
        vehicle_value = payload["vehicle_value"]
        prior_claims = payload["prior_claims"]
        credit_score = payload["credit_score"]
        X = np.array([[age, vehicle_value, prior_claims, credit_score]], dtype=float)
        p = self.pipe.predict_proba(X)[0, 1].item()
        return float(round(p, 4))
