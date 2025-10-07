class ComplianceAgent:
    PEP_LIST = {"pep_123", "pep_abc"}  # placeholder IDs

    def check_pep(self, customer_id: str):
        if customer_id in self.PEP_LIST:
            # In real life: raise or flag for manual review
            return True
        return False

    def basic_fairness_check(self, prob: float, payload: dict) -> list[str]:
        notes: list[str] = []
        if payload.get("gender") == "F" and prob > 0.5:
            notes.append("Fairness check: review female customer with high risk.")
        return notes
