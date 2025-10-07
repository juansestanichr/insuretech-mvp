class ClaimsAgent:
    def summarize(self, description: str) -> tuple[str, str]:
        # Toy "summarization": first 160 chars + heuristic complexity
        desc = description.strip()
        summary = (desc[:157] + '...') if len(desc) > 160 else desc
        words = len(desc.split())
        amount_hint = "high" if words > 80 else ("medium" if words > 40 else "low")
        complexity = {"low": "low", "medium": "medium", "high": "high"}[amount_hint]
        return summary, complexity
