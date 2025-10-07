from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal

class QuoteRequest(BaseModel):
    customer_id: str
    age: int = Field(ge=16, le=100)
    vehicle_value: float = Field(gt=0)
    prior_claims: int = Field(ge=0, le=10)
    credit_score: int = Field(ge=300, le=850)
    gender: Optional[Literal["M","F","X"]] = None

class QuoteResponse(BaseModel):
    probability_of_loss: float
    base_premium: float
    final_premium: float
    decision: Literal["auto_approve", "refer", "reject"]
    reasons: list[str] = []

class UnderwriteRequest(QuoteRequest):
    requested_coverage: float = Field(gt=0)

class UnderwriteResponse(BaseModel):
    decision: Literal["approved", "referred", "rejected"]
    reasons: list[str] = []

class ClaimReport(BaseModel):
    claim_id: str
    customer_id: str
    description: str
    amount_estimate: float

class ClaimResponse(BaseModel):
    summary: str
    complexity: Literal["low","medium","high"]

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

class LogRecord(BaseModel):
    id: int
    ts: str
    actor: str
    action: str
    payload: dict

class CustomerPayload(BaseModel):
    customer_id: str
    name: str
    email: str
    phone: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Email must contain a username and domain")
        return value.lower()


class CustomerResponse(CustomerPayload):
    pass


class MarketingRequest(BaseModel):
    customer_id: str
    product: str


class MarketingResponse(BaseModel):
    message: str
