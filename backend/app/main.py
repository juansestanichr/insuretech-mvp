from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .storage import init_db
from .agents.observability import ObservabilityAgent
from .agents.orchestrator import DecisionOrchestrator
from .agents.claims import ClaimsAgent
from .agents.chatbot import ChatbotAgent
from .agents.fraud import FraudAgent
from .agents.external_data import ExternalDataAgent
from .agents.customer360 import Customer360Agent
from .models import QuoteRequest, QuoteResponse, UnderwriteRequest, UnderwriteResponse, ClaimReport, ClaimResponse, ChatRequest, ChatResponse

app = FastAPI(title="Insuretech MVP API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INDEX_HTML = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")

init_db()


@app.on_event("startup")
def _startup():
    init_db()
    obs = ObservabilityAgent()
    app.state.obs_agent = obs
    app.state.orchestrator = DecisionOrchestrator(obs)


def get_obs():
    obs = getattr(app.state, "obs_agent", None)
    if obs is None:
        obs = ObservabilityAgent()
        app.state.obs_agent = obs
    return obs


def get_orchestrator(obs=Depends(get_obs)):
    orch = getattr(app.state, "orchestrator", None)
    if orch is None:
        orch = DecisionOrchestrator(obs)
        app.state.orchestrator = orch
    return orch


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(INDEX_HTML)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/quote", response_model=QuoteResponse)
def quote(req: QuoteRequest, orch: DecisionOrchestrator = Depends(get_orchestrator)):
    out = orch.quote(req.model_dump())
    return out

@app.post("/underwrite", response_model=UnderwriteResponse)
def underwrite(req: UnderwriteRequest, orch: DecisionOrchestrator = Depends(get_orchestrator)):
    return orch.underwrite(req.model_dump())

@app.post("/claims", response_model=ClaimResponse)
def claims(req: ClaimReport):
    summary, complexity = ClaimsAgent().summarize(req.description)
    return {"summary": summary, "complexity": complexity}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    return {"response": ChatbotAgent().reply(req.message)}

@app.get("/fraud/score")
def fraud_score(amount: float):
    score = FraudAgent().score_claim(amount)
    return {"amount": amount, "fraud_risk": score}

@app.get("/logs")
def logs(obs: ObservabilityAgent = Depends(get_obs), limit: int = 50):
    return obs.list(limit=limit)

@app.get("/fx")
async def fx(base: str = "USD"):
    return await ExternalDataAgent().get_fx(base)

@app.post("/customers/upsert")
def upsert_customer(customer_id: str, name: str, email: str, phone: str | None = None):
    Customer360Agent().upsert(customer_id, name, email, phone)
    return {"ok": True}
