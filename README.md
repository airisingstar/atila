🧠 ATILA — Adaptive Ticket Intelligence Layer for Automation

ATILA (Adaptive Ticket Intelligence Layer for Ticketing & Lifecycle Automation) is an AI-powered project intelligence system that transforms raw tickets into intelligent, time-aware workflows.
It unifies and normalizes data from multiple platforms — Jira, GitHub, ServiceNow, and Azure DevOps — then calculates dynamic priority scores, ranks tasks by urgency, and powers automated dashboards or exports.

⚙️ Architecture Overview
User / Project
   │
   ▼
FastAPI  ──►  SQLAlchemy / SQLite
   │
   ▼
ATILA Scoring + Normalization Engine
   │
   ├─ Normalizes tickets from Jira / GitHub / ServiceNow / Azure
   ├─ Computes weighted scores by priority and age
   ├─ Ranks items across Active / Backlog / Completed
   └─ Generates structured display scores for dashboards and exports

🚀 Run Locally
# clone repo
git clone https://github.com/YOUR_USERNAME/atila-api.git
cd atila-api

# install dependencies
pip install -r requirements.txt

# run server
uvicorn app.main:app --reload


Then open → http://127.0.0.1:8000

☁️ Deploy to Render

This repo includes a production-ready render.yaml:

services:
  - type: web
    name: atila-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT


To deploy:

Push this repo to GitHub.

Go to Render → New Web Service → From Existing Repo.

Render automatically builds and runs ATILA.

🧩 Core Modules
Module	Description
app/main.py	FastAPI entrypoint + dashboard (projects, tickets, scoring)
app/services/models.py	SQLAlchemy + Pydantic models for Projects & Tickets
app/services/scoring.py	Scoring engine — computes weighted priority and age scores
app/services/normalizers.py	Golden Standard Normalizer — unifies Jira, GitHub, SNOW, Azure fields
config/platform_map.yaml	Cross-platform mapping config (4 vendor standard)
app/routers/normalize.py	/normalize/{source} API endpoint for real-time normalization
app/exporters/	Outbound data exporters (S3, CSV, etc.)
app/integrations/	Inbound data connectors for Jira, GitHub, ServiceNow, Azure
🧠 Normalizer API

ATILA’s Normalizer API converts raw JSON from any platform into a clean, unified Smart Ticket schema.

Example

Request

POST /normalize/github
Content-Type: application/json

{
  "id": 101,
  "title": "Bug: login failure",
  "body": "Users cannot login after update",
  "state": "open",
  "assignee": {"login": "david"},
  "labels": [{"name": "bug"}, {"name": "auth"}],
  "repository": {"name": "ai-pipeline"}
}


Response

{
  "id": 101,
  "title": "Bug: login failure",
  "description": "Users cannot login after update",
  "status": "open",
  "priority": null,
  "assignee": "david",
  "labels": ["bug", "auth"],
  "project": "ai-pipeline",
  "source": "github"
}


✅ Supports: Jira, GitHub, ServiceNow, Azure DevOps
✅ Ensures consistent fields for scoring, analytics, and exports.

📊 Scoring Logic

Each ticket receives a calculated priority score based on:

Factor	Description
Priority Weight	Highest (4) → Low (1)
Age Multiplier	Older tickets automatically gain weight
Status Bucket	Active / Backlog / Completed

This creates a live-ranking board that evolves over time.
ATILA doesn’t just store tickets — it understands them.

🧩 Project Goals

Build a lightweight, modular alternative to Jira for smart prioritization.

Enable AI-driven scoring and lifecycle management.

Provide clean integration hooks for the MyAiToolset ecosystem.

Support multi-source ticket unification under one schema.

🛠️ Tech Stack

FastAPI

SQLAlchemy / SQLite

Jinja2 Templates

Uvicorn

PyYAML

Render Cloud Deployment

📅 Future Roadmap
Phase	Focus	Description
1. MVP (Current)	Local FastAPI app with scoring + dashboard + normalizer API	
2. Integration	Add live Jira / GitHub / ServiceNow / Azure imports	
3. Export & SaaS Layer	Multi-tenant Render deployment + S3/Snowflake exports	
4. Intelligence	Adaptive AI ticket scoring and model-training pipeline	
🧾 License

© 2025 MyAiToolset LLC — All Rights Reserved.