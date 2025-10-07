from sklearn.ensemble import IsolationForest
import numpy as np

class FraudAgent:
    def __init__(self):
        rng = np.random.default_rng(0)
        # synthetic non-fraud claim amounts ~ Normal(3000, 1000)
        normal_claims = rng.normal(3000, 1000, size=1000).clip(200, 20000).reshape(-1,1)
        self.model = IsolationForest(contamination=0.03, random_state=0)
        self.model.fit(normal_claims)

    def score_claim(self, amount: float) -> float:
        x = np.array([[amount]], dtype=float)
        # decision_function: lower is more anomalous; convert to 0..1 "risk"
        score = self.model.decision_function(x)[0]
        # map roughly to [0,1]
        risk = float(round((0.5 - score), 4))
        return max(0.0, min(1.0, risk))
