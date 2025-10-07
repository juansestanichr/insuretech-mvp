from .observability import ObservabilityAgent

class LearningFeedbackAgent:
    def __init__(self):
        self.obs = ObservabilityAgent()

    def record(self, kind: str, inputs: dict, outputs: dict):
        self.obs.log("feedback", f"{kind}_record", {"inputs": inputs, "outputs": outputs})
