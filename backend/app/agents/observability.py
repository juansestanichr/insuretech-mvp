from ..storage import SessionLocal, Log
from datetime import datetime

class ObservabilityAgent:
    def log(self, actor: str, action: str, payload: dict):
        with SessionLocal() as s:
            s.add(Log(actor=actor, action=action, payload=payload))
            s.commit()

    def list(self, limit: int = 50):
        with SessionLocal() as s:
            rows = s.query(Log).order_by(Log.id.desc()).limit(limit).all()
            return [
                {"id": r.id, "ts": r.ts.isoformat(), "actor": r.actor, "action": r.action, "payload": r.payload}
                for r in rows
            ]
