🧠 ATILA — Adaptive Ticket Intelligence Layer for Automation

ATILA (Adaptive Ticket Intelligence Layer for Ticketing & Lifecycle Automation) is an AI-powered priority and scoring system that transforms raw tickets into intelligent, time-aware workflows.
It calculates dynamic priority scores, ranks tasks, and structures projects using timeline-based logic that can plug into existing tools such as Jira, ServiceNow, or internal MyAiToolset boards.

⚙️ Architecture Overview
User / Project
   │
   ▼
FastAPI  ──►  SQLModel / SQLite
   │
   ▼
ATILA Scoring Engine (pscore)
   │
   ├─ Computes weighted scores by priority and age
   ├─ Ranks items across Active / Backlog / Completed
   └─ Generates structured display scores for dashboards

🚀 Run Locally
# clone repo
git clone https://github.com/YOUR_USERNAME/atila-api.git
cd atila-api

# install dependencies
pip install -r requirements.txt

# run server
uvicorn app.main:app --reload


Then visit → http://127.0.0.1:8000

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

📊 Core Logic — Priority & Scoring

Each ticket receives a calculated score based on:

Priority weight: Highest (4) → Low (1)

Age multiplier: Older tickets gain weight automatically

Status bucket: Active, Backlog, Completed

This creates a live-ranking board that evolves over time —
ATILA doesn’t just store tickets; it understands them.

🧩 Project Goals

Build a lightweight alternative to Jira for smart prioritization.

Enable AI-driven scoring across departments or projects.

Provide clean integration hooks for MyAiToolset’s ecosystem.

🛠️ Tech Stack

FastAPI

SQLModel / SQLite

Uvicorn

Jinja2 templates

Render cloud deployment

📅 Future Roadmap
Phase	Focus	Description
1	MVP (Current)	Local FastAPI app with scoring + dashboard
2	Integration	Jira / ServiceNow plug-ins + auto import
3	SaaS Layer	Multi-tenant Render hosting + project clusters
4	Intelligence	Customizable AI ticket models + tuning
🧾 License

© 2025 MyAiToolset LLC – All Rights Reserved.