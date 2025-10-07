from ..models import QuoteRequest, UnderwriteRequest

class DataGovernanceAgent:
    def validate_quote(self, payload: dict):
        QuoteRequest(**payload)  # raises if invalid
        return True

    def validate_underwrite(self, payload: dict):
        UnderwriteRequest(**payload)
        return True
