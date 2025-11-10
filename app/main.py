from __future__ import annotations
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from .services.models import Base, Project, Ticket
from .services.scoring import recalc_scores, assign_all_scores_for_project

app = FastAPI(title="ATILA — Adaptive Ticket Intelligence Layer")

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "atila.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}", echo=False, connect_args={"check_same_thread": False}
)

# Ensure static + templates directories exist
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates_dir = BASE_DIR / "templates"
templates_dir.mkdir(exist_ok=True)


# ---------------------------
# DB Init
# ---------------------------
def init_db():
    Base.metadata.create_all(engine)


@app.on_event("startup")
def startup():
    init_db()
    with Session(engine) as s:
        recalc_scores(s)


# ---------------------------
# Helpers
# ---------------------------
def normalize_tags(raw: str | None) -> str:
    """Ensure our two required defaults exist in the tag string."""
    base_defaults = ["Score:[0.00]", "Ticket_ID:0"]
    existing = [t.strip() for t in (raw or "").split(",") if t.strip()]
    for d in base_defaults:
        if d not in existing:
            existing.append(d)
    return ", ".join(existing)


def render_dashboard(projects: list[Project], active_project: Optional[Project], tickets: list[Ticket]) -> str:
    """Basic but usable HTML dashboard for ATILA."""
    html = """
    <html>
      <head>
        <title>ATILA Dashboard</title>
        <style>
          body { font-family: Arial, sans-serif; background: #f7f9fb; margin: 40px; }
          h1 { color: #2563eb; }
          form { margin-bottom: 30px; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.05); }
          input, textarea, select { width: 100%; padding: 8px; margin: 5px 0 10px 0; border: 1px solid #ccc; border-radius: 6px; }
          button { background: #2563eb; color: white; border: none; padding: 10px 18px; border-radius: 6px; cursor: pointer; }
          button:hover { background: #1d4ed8; }
          .card { background: #fff; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 0 6px rgba(0,0,0,0.05); }
        </style>
      </head>
      <body>
        <h1>🚀 ATILA — Adaptive Ticket Intelligence Layer</h1>
        
        <form action="/create_project" method="post">
          <h2>Create Project</h2>
          <input type="text" name="name" placeholder="Project Name" required>
          <input type="text" name="description" placeholder="Description">
          <input type="text" name="tags" placeholder="Tags (comma separated)">
          <button type="submit">Create Project</button>
        </form>
    """

    if not projects:
        html += "<h3>No projects yet. Add your first project above!</h3></body></html>"
        return html

    html += "<h2>Existing Projects</h2>"
    for p in projects:
        html += f"<div class='card'><b>{p.name}</b> — {p.status}<br>{p.description or ''}</div>"

    if active_project:
        html += f"<h2>Active Project: {active_project.name}</h2>"
        html += f"<form action='/add_ticket' method='post'>"
        html += f"<input type='hidden' name='project_id' value='{active_project.id}'>"
        html += f"<h3>Add Ticket to {active_project.name}</h3>"
        html += "<input name='title' placeholder='Ticket title' required>"
        html += "<textarea name='description' placeholder='Description'></textarea>"
        html += "<select name='priority'><option>Highest</option><option>High</option><option>Medium</option><option>Low</option><option>Backlog</option></select>"
        html += "<select name='status'><option>Backlog</option><option>Active</option><option>Completed</option></select>"
        html += "<select name='category'><option>Product Management</option><option>Product Quality</option><option>Product Scaling</option><option>Other</option></select>"
        html += "<button type='submit'>Add Ticket</button></form>"

        html += "<h3>Tickets</h3>"
        for t in tickets:
            html += f"<div class='card'>[{t.priority}] {t.title} — {t.status}</div>"

    html += "</body></html>"
    return html



# ---------------------------
# Routes
# ---------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    with Session(engine) as session:
        projects = session.execute(select(Project)).scalars().all()
        projects.sort(key=lambda p: p.name.lower())

        active_project: Optional[Project] = projects[0] if projects else None
        tickets: list[Ticket] = []
        if active_project:
            tickets = session.execute(
                select(Ticket).where(Ticket.project_id == active_project.id)
            ).scalars().all()
            tickets.sort(key=lambda t: t.display_score or 0)

        html = render_dashboard(projects, active_project, tickets)
        return HTMLResponse(html)


@app.post("/create_project")
def create_project(
    name: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
):
    with Session(engine) as session:
        existing = session.execute(select(Project).where(Project.name == name)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Project name already exists.")

        project = Project(
            name=name,
            description=description or None,
            status="Created",
            tags=normalize_tags(tags),
        )
        session.add(project)
        session.commit()
        session.refresh(project)

        assign_all_scores_for_project(session, project.id)

    return RedirectResponse(url="/", status_code=303)


@app.post("/add_ticket")
def add_ticket(
    project_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
    status: str = Form("Backlog"),
    category: str = Form("Product Management"),
):
    with Session(engine) as session:
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        t = Ticket(
            title=title,
            description=description or None,
            priority=priority,
            status=status,
            category=category,
            project_id=project_id,
        )
        session.add(t)
        session.commit()
        session.refresh(t)

        assign_all_scores_for_project(session, project_id)

    return RedirectResponse(url="/", status_code=303)


@app.post("/set_project_active")
def set_project_active(project_id: int = Form(...)):
    with Session(engine) as session:
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        project.status = "Active"
        session.add(project)
        session.commit()

        assign_all_scores_for_project(session, project_id)

    return RedirectResponse(url="/", status_code=303)

# ==========================================================
# Routers
# ==========================================================
from fastapi.middleware.cors import CORSMiddleware
from app.routers import normalize

# Enable CORS (optional but helpful for local testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(normalize.router)

