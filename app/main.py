from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from .db import init_db, get_session, engine
from .models import Project, Ticket
from .scoring import recalc_scores

app = FastAPI(title="ATILA — Adaptive Ticket Intelligence Layer")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    projects = session.exec(select(Project)).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "projects": projects})

@app.post("/create_project")
def create_project(name: str = Form(...), description: str = Form(""), session: Session = Depends(get_session)):
    p = Project(name=name, description=description)
    session.add(p)
    session.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/project/{project_id}", response_class=HTMLResponse)
def project_detail(request: Request, project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    tickets = session.exec(select(Ticket).where(Ticket.project_id==project_id)).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "project": project, "tickets": tickets})

@app.post("/add_ticket/{project_id}")
def add_ticket(project_id: int, title: str = Form(...), description: str = Form(""), priority: str = Form("Medium"), session: Session = Depends(get_session)):
    t = Ticket(project_id=project_id, title=title, description=description, priority=priority)
    session.add(t)
    session.commit()
    return RedirectResponse(f"/project/{project_id}", status_code=303)
