class PricingAgent:
    def quote(self, prob: float, payload: dict) -> dict:
        base_rate = 300.0
        risk_multiplier = 1 + 2.5 * prob
        value_factor = max(0.5, min(2.0, payload["vehicle_value"] / 20000.0))
        prior_claims_fee = 50.0 * payload["prior_claims"]
        base_premium = base_rate * value_factor + prior_claims_fee
        final_premium = round(base_premium * risk_multiplier, 2)
        return {"base_premium": round(base_premium, 2), "final_premium": final_premium}
