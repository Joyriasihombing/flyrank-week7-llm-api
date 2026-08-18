Berikut adalah versi **`README.md`** yang sudah dirapikan, terstruktur dengan standar repositori produksi, memiliki hirarki yang jelas, serta dilengkapi *code block formatting* yang tepat.

Anda dapat langsung menyalin (*copy-paste*) seluruh isi di bawah ini ke dalam file `README.md` repositori Anda.

---

```markdown
# FlyRank Week 7 — Production-Oriented LLM API

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat-square&logo=fastapi)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic)
![OpenRouter](https://img.shields.io/badge/OpenRouter-API-6366F1?style=flat-square)

A production-oriented REST API that adds an LLM-powered customer support triage feature to an existing Widget Platform. 

The API accepts unstructured customer messages and returns validated, structured classifications to automate ticket handling while ensuring system reliability through deterministic safeguards.

---

## 📌 Overview

Integrating LLMs into production APIs requires handling non-deterministic outputs. This project establishes a strict reliability boundary between probabilistic LLM outputs and deterministic backend workflows.

### Key Capabilities
- **Automated Triage:** Classifies messages into categories (`billing`, `bug`, `feature`, `other`) and urgency levels (`low`, `normal`, `high`).
- **Structured JSON Output:** Enforces strict Pydantic schema validation for all LLM responses.
- **Automated Repair Retry:** Automatically prompts the LLM to fix invalid JSON outputs (limited to 1 retry).
- **Operational Kill Switch:** Instantly disable LLM processing via environment variables with zero code changes.
- **Cost & Token Logging:** Tracks token usage and estimates request costs locally.
- **Built-in Evaluation Suite:** Evaluates model accuracy against test cases.

---

## 🏗 System Flow & Architecture

### High-Level API Workflow

```text
Client Request
      │
      ▼
FastAPI Router (POST /widgets/{id}/submissions)
      │
      ├──────► Check LLM_ENABLED?
      │             │
      │             ├── [FALSE] ──► Fallback Response (Static Default)
      │             │
      │             └── [TRUE]
      │                   │
      ▼                   ▼
Versioned Prompt ──► OpenRouter / LLM Client (Timeout = 30s)
                          │
                          ▼
                  Pydantic Validation
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
       [ Valid ]                   [ Invalid ]
            │                           │
            │                           ▼
            │                    1x Repair Retry
            │                           │
            │                     Validate Again
            │                           │
            ├◄──────────────────────────┘
            │
            ▼
   Save Submission to DB ──► Return API Response

```

---

## ✨ Feature Breakdown

### 1. Versioned Prompts (`app/llm/prompts.py`)

Prompts are isolated from application logic to allow tracking changes in model behavior over time.

```python
TRIAGE_PROMPT_VERSION = "v1"

```

### 2. Schema Validation (`app/llm/schema.py`)

Outputs are strictly validated using Pydantic. If an LLM returns fields outside the schema or invalid ranges, validation fails.

* **Category:** `billing`, `bug`, `feature`, `other`
* **Urgency:** `low`, `normal`, `high`
* **Confidence:** `0.0` to `1.0`
* **Reason:** Short explanation string.

### 3. Repair Retry Mechanism

If the first output fails validation, the system sends a follow-up request asking the model to fix its response based on the validation error. Max retries are capped at `1` to prevent execution loops.

### 4. Timeout & Explicit Retry Policy (`app/llm/client.py`)

* **Timeout:** Set to `30.0s` to prevent hanging requests.
* **Max Retries:** Client-level retries are set to `max_retries=0`. All retries are handled explicitly at the application level via the JSON repair flow.

### 5. Operational Kill Switch

Disable LLM processing seamlessly during provider outages or cost spikes by setting:

```bash
LLM_ENABLED=false

```

When disabled, the system defaults to:

```json
{
  "category": "other",
  "urgency": "normal",
  "confidence": 0.5,
  "reason": "Default classification."
}

```

### 6. Cost Logging (`app/llm/cost.py`)

Tracks token usage and estimated cost per request in a local log file (`llm_cost.log`):

```text
LLM COST LOG: 2026-08-18T20:00:00 | model=openrouter/free | prompt_tokens=500 | completion_tokens=80 | total_tokens=580 | estimated_cost_usd=0.00000000

```

---

## 🛠 Tech Stack

* **Language:** Python 3.10+
* **Framework:** FastAPI, Uvicorn
* **Database & ORM:** SQLite, SQLAlchemy
* **Validation:** Pydantic v2
* **Authentication:** JWT (JSON Web Tokens), Passlib
* **LLM Integration:** OpenAI Python SDK (configured for OpenRouter)

---

## 📁 Project Structure

```text
flyrank-week7-llm-api/
│
├── app/
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py        # LLM client configuration & timeouts
│   │   ├── cost.py          # Token & cost calculation logger
│   │   ├── prompts.py       # Versioned system prompts
│   │   └── schema.py        # Pydantic validation schemas
│   │
│   ├── models/              # SQLAlchemy database models
│   │   ├── user.py
│   │   ├── widget.py
│   │   └── submission.py
│   │
│   ├── routers/             # API Route handlers
│   │   ├── auth.py
│   │   ├── triage.py
│   │   └── widgets.py
│   │
│   ├── schemas/             # Request/Response Pydantic schemas
│   │   ├── submission.py
│   │   └── widget.py
│   │
│   ├── database.py          # Database setup & sessions
│   ├── dependencies.py      # Auth & DB dependencies
│   ├── main.py              # FastAPI app entrypoint
│   └── security.py          # Hashing & JWT logic
│
├── eval/
│   ├── triage_cases.json    # Test suite dataset
│   └── run_eval.py          # Evaluation runner script
│
├── .env.example
├── .gitignore
├── JOB-CARD.md
├── requirements.txt
└── README.md

```

---

## 🚀 Getting Started

### 1. Prerequisites & Installation

Clone the repository and set up a virtual environment:

```bash
# Clone repository
git clone [https://github.com/Joyriasihombing/flyrank-week7-llm-api.git](https://github.com/Joyriasihombing/flyrank-week7-llm-api.git)
cd flyrank-week7-llm-api

# Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

```

### 2. Environment Configuration

Copy `.env.example` to `.env` and fill in your OpenRouter credentials:

```bash
cp .env.example .env

```

Set up your `.env` parameters:

```env
LLM_BASE_URL=[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)
LLM_API_KEY=your_openrouter_api_key_here
LLM_MODEL=openrouter/free

LLM_ENABLED=true

LLM_INPUT_COST_PER_1M=0.0
LLM_OUTPUT_COST_PER_1M=0.0

```

### 3. Run the Server

```bash
uvicorn app.main:app --reload

```

* **Interactive Docs (Swagger UI):** `http://127.0.0.1:8000/docs`
* **OpenAPI Spec:** `http://127.0.0.1:8000/openapi.json`

---

## 🔌 API Reference & Usage

### Step 1: Register & Login (Authentication)

**Register:**

```bash
curl -X POST [http://127.0.0.1:8000/auth/register](http://127.0.0.1:8000/auth/register) \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'

```

**Login:**

```bash
curl -X POST [http://127.0.0.1:8000/auth/login](http://127.0.0.1:8000/auth/login) \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=securepassword123"

```

*Copy the returned `access_token` for authenticated requests.*

---

### Step 2: Create a Widget

```bash
curl -X POST [http://127.0.0.1:8000/widgets/](http://127.0.0.1:8000/widgets/) \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Customer Support",
    "description": "General help desk widget",
    "widget_type": "contact",
    "button_text": "Submit Ticket"
  }'

```

---

### Step 3: Submit Customer Message (LLM Triage Endpoint)

**Endpoint:** `POST /widgets/{widget_id}/submissions`

```bash
curl -X POST [http://127.0.0.1:8000/widgets/1/submissions](http://127.0.0.1:8000/widgets/1/submissions) \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "message": "I was charged twice for my subscription this month."
  }'

```

**Response Example:**

```json
{
  "id": 1,
  "widget_id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "message": "I was charged twice for my subscription this month.",
  "category": "billing",
  "urgency": "normal",
  "confidence": 0.95,
  "reason": "The customer reports being charged twice for their subscription."
}

```

---

## 📊 Evaluation

A test suite containing 10 test cases is provided in `eval/triage_cases.json`.

Run the evaluation script:

```bash
PYTHONPATH=. python eval/run_eval.py

```

**Sample Output:**

```text
Running evaluation on 10 cases...

1. category=PASS | urgency=PASS
2. category=PASS | urgency=PASS
3. category=PASS | urgency=PASS
4. category=PASS | urgency=PASS
5. category=PASS | urgency=PASS
6. category=PASS | urgency=PASS
7. category=PASS | urgency=PASS
8. category=PASS | urgency=PASS
9. category=PASS | urgency=FAIL
10. category=PASS | urgency=PASS

==============================
EVALUATION RESULT
==============================
Category accuracy: 9/10 (90%)
Urgency accuracy:  8/10 (80%)

```

---

## 📜 Commit History

This repository was developed incrementally:

```text
72699d1 feat: add LLM timeout and retry policy
0c1ac3a feat: add versioned triage prompt
4a77c92 feat: add versioned triage prompt and llm kill switch
c157d0b chore: ignore local database
1ef9f08 feat: add LLM triage endpoint
6ca7ba1 readme
318c91e Implement authentication, widget management, and submission API
9070dd7 Implementation JWT Authentication
ab69854 setup database and SQLAlchemy models
2d60d0e add API design and system flow

```

```

```