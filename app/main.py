from __future__ import annotations
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Session, create_engine, select

from .models import Project, Ticket
from .scoring import recalc_scores, assign_all_scores_for_project

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
    SQLModel.metadata.create_all(engine)


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
    """Simple inline HTML render (placeholder until templates are added)."""
    if not projects:
        return "<h2>No projects yet — create one using the Add + tab.</h2>"
    out = f"<h1>{active_project.name if active_project else 'No Active Project'}</h1><ul>"
    for t in tickets:
        out += f"<li>[{t.priority}] {t.title} — {t.status}</li>"
    out += "</ul>"
    return out


# ---------------------------
# Routes
# ---------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    with Session(engine) as session:
        projects = session.exec(select(Project)).all()
        projects.sort(key=lambda p: p.name.lower())

        active_project: Optional[Project] = projects[0] if projects else None
        tickets: list[Ticket] = []
        if active_project:
            tickets = session.exec(
                select(Ticket).where(Ticket.project_id == active_project.id)
            ).all()
            tickets.sort(key=lambda t: t.display_score)

        html = render_dashboard(projects, active_project, tickets)
        return HTMLResponse(html)


@app.post("/create_project")
def create_project(
    name: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
):
    with Session(engine) as session:
        if session.exec(select(Project).where(Project.name == name)).first():
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
