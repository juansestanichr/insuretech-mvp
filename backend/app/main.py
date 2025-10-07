from contextlib import asynccontextmanager
from pathlib import Path
from typing import Callable, MutableMapping, TypeVar, cast

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .agents.chatbot import ChatbotAgent
from .agents.claims import ClaimsAgent
from .agents.customer360 import Customer360Agent
from .agents.marketing import MarketingAgent
from .models import (
    QuoteRequest,
    QuoteResponse,
    UnderwriteRequest,
    UnderwriteResponse,
    ClaimReport,
    ClaimResponse,
    ChatRequest,
    ChatResponse,
    CustomerPayload,
    CustomerResponse,
    MarketingRequest,
    MarketingResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    obs_agent = ObservabilityAgent()
    app.state.obs_agent = obs_agent
    app.state.orchestrator = DecisionOrchestrator(obs_agent)
    app.state.agent_cache = {}
    try:
        yield
    finally:
        cache = getattr(app.state, "agent_cache", None)
        if isinstance(cache, MutableMapping):
            cache.clear()
        app.state.obs_agent = None
        app.state.orchestrator = None


app = FastAPI(title="Insuretech MVP API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_cached_agent(name: str, factory: Callable[[], AgentT]) -> AgentT:
    cache: MutableMapping[str, object] = getattr(app.state, "agent_cache", {})
    if name not in cache:
        cache[name] = factory()
        app.state.agent_cache = cache
    return cast(AgentT, cache[name])


def get_obs():
    obs = getattr(app.state, "obs_agent", None)
    if obs is None:
        obs = ObservabilityAgent()
        app.state.obs_agent = obs
    return obs


def get_orchestrator(obs=Depends(get_obs)):
    orchestrator = getattr(app.state, "orchestrator", None)
    if orchestrator is None:
        orchestrator = DecisionOrchestrator(obs)
        app.state.orchestrator = orchestrator
    return orchestrator


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(INDEX_HTML)


def get_customer360():
    return Customer360Agent()

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/quote", response_model=QuoteResponse)
def quote(req: QuoteRequest, orch: DecisionOrchestrator = Depends(get_orchestrator)):
    return orch.quote(req.model_dump())


@app.post("/underwrite", response_model=UnderwriteResponse)
def underwrite(req: UnderwriteRequest, orch: DecisionOrchestrator = Depends(get_orchestrator)):
    return orch.underwrite(req.model_dump())


@app.post("/claims", response_model=ClaimResponse)
def claims(req: ClaimReport):
    agent = _get_cached_agent("claims", ClaimsAgent)
    summary, complexity = agent.summarize(req.description)
    return {"summary": summary, "complexity": complexity}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    agent = _get_cached_agent("chatbot", ChatbotAgent)
    return {"response": agent.reply(req.message)}


@app.get("/fraud/score")
def fraud_score(amount: float):
    agent = _get_cached_agent("fraud", FraudAgent)
    score = agent.score_claim(amount)
    return {"amount": amount, "fraud_risk": score}


@app.get("/logs")
def logs(obs: ObservabilityAgent = Depends(get_obs), limit: int = 50):
    return obs.list(limit=limit)


@app.get("/fx")
async def fx(base: str = "USD"):
    agent = _get_cached_agent("external_data", ExternalDataAgent)
    return await agent.get_fx(base)


@app.post("/customers", response_model=CustomerResponse)
def upsert_customer(
    payload: CustomerPayload,
    c360: Customer360Agent = Depends(get_customer360),
    obs: ObservabilityAgent = Depends(get_obs),
):
    c360.upsert(payload.customer_id, payload.name, payload.email, payload.phone)
    obs.log("customer360", "upsert", payload.model_dump())
    stored = c360.get(payload.customer_id)
    if not stored:
        raise HTTPException(status_code=500, detail="Customer record not stored")
    return stored


@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str, c360: Customer360Agent = Depends(get_customer360)):
    record = c360.get(customer_id)
    if not record:
        raise HTTPException(status_code=404, detail="Customer not found")
    return record


@app.post("/marketing/outreach", response_model=MarketingResponse)
def marketing_outreach(
    payload: MarketingRequest,
    c360: Customer360Agent = Depends(get_customer360),
    obs: ObservabilityAgent = Depends(get_obs),
):
    customer = c360.get(payload.customer_id)
    name = customer["name"] if customer else payload.customer_id
    message = MarketingAgent().craft_outreach(name, payload.product)
    obs.log(
        "marketing",
        "outreach_generated",
        {"customer_id": payload.customer_id, "product": payload.product, "has_profile": bool(customer)},
    )
    return {"message": message}
