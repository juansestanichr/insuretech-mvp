from .risk_model import RiskModel
from .pricing import PricingAgent
from .underwriting import UnderwritingAgent
from .compliance import ComplianceAgent
from .data_gov import DataGovernanceAgent
from .observability import ObservabilityAgent
from .learning_feedback import LearningFeedbackAgent
from .customer360 import Customer360Agent

class DecisionOrchestrator:
    def __init__(self, obs: ObservabilityAgent):
        self.risk = RiskModel()
        self.pricing = PricingAgent()
        self.uw = UnderwritingAgent()
        self.compliance = ComplianceAgent()
        self.gov = DataGovernanceAgent()
        self.obs = obs
        self.feedback = LearningFeedbackAgent()
        self.c360 = Customer360Agent()

    def quote(self, payload: dict):
        self.gov.validate_quote(payload)
        self.obs.log("orchestrator", "quote_received", payload)
        prob = self.risk.predict_proba(payload)
        price = self.pricing.quote(prob, payload)
        decision, reasons = self.uw.pre_decision(prob, price, payload)
        # minimal fairness/compliance checks
        self.compliance.check_pep(payload.get("customer_id", ""))
        fairness_notes = self.compliance.basic_fairness_check(prob, payload)
        reasons += fairness_notes
        out = {
            "probability_of_loss": prob,
            "base_premium": price["base_premium"],
            "final_premium": price["final_premium"],
            "decision": decision,
            "reasons": reasons,
        }
        self.obs.log("orchestrator", "quote_decided", out)
        self.feedback.record("quote", payload, out)
        return out

    def underwrite(self, payload: dict):
        self.gov.validate_underwrite(payload)
        prob = self.risk.predict_proba(payload)
        price = self.pricing.quote(prob, payload)
        decision, reasons = self.uw.final_decision(prob, price, payload)
        out = {"decision": decision, "reasons": reasons}
        self.feedback.record("underwrite", payload, out)
        return out
