from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .storage import init_db
from .agents.observability import ObservabilityAgent
from .agents.orchestrator import DecisionOrchestrator
from .agents.claims import ClaimsAgent
from .agents.chatbot import ChatbotAgent
from .agents.fraud import FraudAgent
from .agents.external_data import ExternalDataAgent
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

app = FastAPI(title="Insuretech MVP API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

def get_obs():
    return ObservabilityAgent()

def get_orchestrator(obs=Depends(get_obs)):
    return DecisionOrchestrator(obs)

def get_customer360():
    return Customer360Agent()

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
