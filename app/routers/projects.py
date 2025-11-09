
from fastapi import APIRouter, Depends
from sqlmodel import SQLModel, select
from sqlmodel import Session
from ..db import get_session
from ..models import Project

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("")
def list_projects(session: Session = Depends(get_session)):
    return session.exec(select(Project)).all()

@router.post("")
def create_project(project: Project, session: Session = Depends(get_session)):
    session.add(project)
    session.commit()
    session.refresh(project)
    return project
