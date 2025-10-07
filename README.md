# Insuretech MVP (AI‑Native Insurer)

This repository contains a **minimum viable product** for a fully digital insurer aligned to McKinsey’s four-layer AI-native architecture. You can clone it from GitHub and run the demo without writing any code.

## Architecture at a glance (plain-English tour)

1. **User experience layer** – A FastAPI service exposes easy-to-use HTTP endpoints (think of them as buttons you can press) for quotes, underwriting, claims, chat support, fraud scoring and system logs. Explore everything through the automatically generated docs at <http://127.0.0.1:8000/docs>.
2. **Decision layer** – A logistic regression model estimates loss probability, the pricing agent calculates premiums, the underwriting agent produces approve/refer/reject outcomes, and compliance/fairness plus fraud scoring agents add guardrails.
3. **Infrastructure layer** – Each capability lives in its own Python “agent” so it can be reused or swapped out. Implemented agents cover marketing, Customer 360, claims summarisation, chatbot, data governance, compliance, fraud detection, observability, learning feedback, external data lookups and infrastructure modernisation.
4. **Data platform layer** – Pydantic validates every payload, SQLAlchemy/SQLite persist customer and log data, and the Observability Agent exposes the interaction history.

> ⚙️ **Technology stack:** FastAPI, scikit-learn, SQLAlchemy/SQLite, httpx, pydantic, pytest, Docker and GitHub Actions.

---

## Run the MVP locally (no prior coding knowledge needed)

1. **Install Python 3.11 or newer.** On Windows or macOS download it from <https://www.python.org/downloads/> and tick the option that adds Python to PATH.
2. **Open a terminal** (Command Prompt, PowerShell, macOS Terminal or Linux shell) and move into the folder where you cloned the repo:

   ```bash
   cd insuretech-mvp
   ```

3. **Create an isolated Python environment** so dependencies stay self-contained:

   ```bash
   python -m venv .venv
   # Windows users: .venv\Scripts\activate
   # macOS/Linux users:
   source .venv/bin/activate
   ```

4. **Install the project requirements** (this may take a minute the first time):

   ```bash
   pip install -r backend/requirements.txt
   ```

5. **Start the API server** and leave it running while you try the demo:

   ```bash
   uvicorn app.main:app --reload --port 8000 --app-dir backend
   ```

6. **Interact with the endpoints:**
   - Visit <http://127.0.0.1:8000/docs>. FastAPI serves a friendly web UI where you can click “Try it out” for every operation.
   - Or use the terminal to request a quote:

     ```bash
     curl -X POST http://127.0.0.1:8000/quote \
       -H "Content-Type: application/json" \
       -d '{"customer_id":"c1","age":30,"vehicle_value":15000,"prior_claims":0,"credit_score":680,"gender":"F"}'
     ```

   - Explore `/underwrite`, `/claims`, `/chat`, `/fraud/score`, `/fx`, `/customers`, `/marketing/outreach` and `/logs` through the docs page to see how the agents collaborate.
   - Tip: create a customer profile first so other agents can personalise responses:

     ```bash
     curl -X POST http://127.0.0.1:8000/customers \
       -H "Content-Type: application/json" \
       -d '{"customer_id":"cust-001","name":"Jamie Rivera","email":"jamie@example.com","phone":"+1-202-555-0100"}'
     ```

     Now call the marketing agent to generate outreach copy that uses the stored profile:

     ```bash
     curl -X POST http://127.0.0.1:8000/marketing/outreach \
       -H "Content-Type: application/json" \
       -d '{"customer_id":"cust-001","product":"AI Auto Protect"}'
     ```

7. **Stop the server** with `Ctrl+C` when you are finished. Deactivate the virtual environment using `deactivate`.

---

## Run with Docker (optional)

Prefer containers? Install Docker Desktop and run:

```bash
docker compose up --build
```

The API will be available on <http://127.0.0.1:8000>. Use `Ctrl+C` to stop the stack.

---

## Continuous verification

Every push triggers the GitHub Actions workflow in `.github/workflows/ci.yml`, which installs dependencies, runs the automated tests and builds the Docker image. If you fork the repo you only need to push your commits. Optionally add secrets such as `OPENAI_API_KEY` to let the Chatbot Agent call a real LLM.

To run the same test locally:

```bash
cd backend
pytest
```

---

## What each agent does

| Agent | Purpose |
| --- | --- |
| Marketing | Generates personalised outreach copy for prospects. |
| Customer 360 | Stores and retrieves customer data in SQLite. |
| Risk Model | Trains a tiny logistic regression model on synthetic data at startup and predicts probability of loss. |
| Pricing | Computes base and risk-adjusted premiums. |
| Underwriting | Applies business rules (risk thresholds, credit score, coverage limits) and outputs approval, referral or rejection reasons. |
| Compliance & Fairness | Flags politically exposed persons and adds fairness review notes. |
| Data Governance | Validates every payload using strict Pydantic schemas. |
| Claims | Summarises claim descriptions and estimates complexity. |
| Chatbot | Answers FAQ-style questions with a rule-based fallback (switches to an LLM when an OpenAI key is provided). |
| Fraud Detection | Uses an Isolation Forest to score anomalous claim amounts. |
| External Data | Retrieves FX rates from a public API with an offline fallback. |
| Observability | Logs interactions for auditing; view them via `/logs`. |
| Learning Feedback | Stores decision inputs/outputs to feed future model improvements. |
| Infrastructure Modernisation | Demonstrates how legacy documents could be transformed into structured summaries. |

Planned extensions (Retention, Product Recommendation, Advanced Fraud, Regulatory Compliance, Explainability, Market Intelligence, Talent Management, Climate Risk, Reinsurance) are sketched in the code as future enhancements.

---

## Repository layout

```text
backend/
  app/
    main.py               # FastAPI entrypoint wiring the agents together
    models.py             # Pydantic request/response schemas
    config.py             # Environment variables (DB URL, API keys)
    storage.py            # SQLAlchemy ORM models and database bootstrap
    agents/               # Individual functional components
  tests/
    test_orchestrator.py  # Smoke test that the quote endpoint works end-to-end
  Dockerfile
  requirements.txt
docker-compose.yml        # One-command local deployment
.github/workflows/ci.yml  # Continuous integration pipeline
```

---

## Next steps (suggested roadmap)

- Replace toy/synthetic training with real data pipelines.
- Harden compliance (KYC/AML/PEP screening via external providers).
- Add **Retention** and **Product Recommendation** agents.
- Expand front-ends (React/Vite apps) and authentication (OAuth/OIDC, RBAC).
- Stream logs to OpenTelemetry + an observability backend (ELK, Grafana, etc.).

