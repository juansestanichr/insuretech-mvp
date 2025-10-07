class UnderwritingAgent:
    def pre_decision(self, prob: float, price: dict, payload: dict):
        reasons = []
        decision = "auto_approve"
        if prob > 0.6:
            decision = "reject"
            reasons.append(f"High risk score {prob}")
        elif prob > 0.4:
            decision = "refer"
            reasons.append(f"Borderline risk score {prob}")
        if payload.get("credit_score", 650) < 550:
            decision = "refer"
            reasons.append("Low credit score")
        return decision, reasons

    def final_decision(self, prob: float, price: dict, payload: dict):
        decision, reasons = self.pre_decision(prob, price, payload)
        # add a simple capacity rule
        if payload.get("requested_coverage", 0) > 2.5 * payload.get("vehicle_value", 0):
            decision = "rejected"
            reasons.append("Coverage exceeds value threshold")
        elif decision == "auto_approve":
            decision = "approved"
        elif decision == "refer":
            decision = "referred"
        return decision, reasons
