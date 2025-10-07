# Insuretech MVP (AI‑Native Insurer)

This repository contains a **minimum viable product** for a fully digital insurer aligned to McKinsey’s **four-layer AI-native architecture**:

1) **User Experience layer:** separate portals (customer & employee) via simple placeholders, and an API for quotes, claims and chat.
2) **Decision layer:** logistic regression risk, pricing algorithms, underwriting rules, fraud anomaly scoring; an **Orchestrator** composes decisions.
3) **Infrastructure layer:** modular **agents** (marketing, customer360, claims, chatbot, data governance, compliance/fairness, fraud, observability, external data, learning feedback, infra modernization stub).
4) **Data platform layer:** pydantic validation, simple SQLite store, and an **Observability Agent** exposing logs.

> ⚙️ Stack: FastAPI, scikit-learn, SQLAlchemy/SQLite, httpx, pydantic, pytest, Docker, GitHub Actions.

---

## Quickstart (Local)

```bash
# 1) Python env
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

# 2) Run API + UI
uvicorn app.main:app --reload --port 8000 --app-dir backend

# 3) Try it
# Visit the all-in-one control panel at http://127.0.0.1:8000/
curl -X POST http://127.0.0.1:8000/quote -H "Content-Type: application/json" -d '{"customer_id":"c1","age":30,"vehicle_value":15000,"prior_claims":0,"credit_score":680,"gender":"F"}'
```

Open **http://127.0.0.1:8000/** for the new UI or **http://127.0.0.1:8000/docs** for the interactive API.

---

## Docker (Local)

```bash
docker compose up --build
```

---

## Web control panel

The FastAPI app now serves a lightweight single-page control panel at `/`. It lets you:

- Run quotes and underwriting decisions without leaving the browser.
- Summarise claims and chat with the virtual assistant.
- Trigger fraud scoring, refresh observability logs and check API health.

All interactions call the same backend endpoints, so you can observe the resulting traces in the `/logs` view or through the API.

---

## GitHub CI

This repo ships a GitHub Actions workflow running lint/tests and building the Docker image. Add secrets (optional): `OPENAI_API_KEY` for Chatbot Agent, etc.

---

## Repo layout

```
backend/
  app/
    main.py
    models.py
    config.py
    storage.py
    agents/
      orchestrator.py
      risk_model.py
      pricing.py
      underwriting.py
      claims.py
      chatbot.py
      marketing.py
      customer360.py
      compliance.py
      fraud.py
      external_data.py
      observability.py
      data_gov.py
      learning_feedback.py
      infra_modernization.py
  tests/
    test_orchestrator.py
  Dockerfile
  requirements.txt
docker-compose.yml
.github/workflows/ci.yml
```

---

## Next steps

- Replace toy/synthetic training with real data pipelines.
- Harden compliance (KYC/AML/PEP screening via providers).
- Add **Retention** and **Product Recommendation** agents.
- Expand frontends (React/Vite apps) and auth (OAuth/OIDC, RBAC).
- Move logs to OpenTelemetry + a real backend (ELK, Grafana, etc.).
