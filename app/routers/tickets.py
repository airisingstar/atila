
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel import Session
from typing import Optional
from ..db import get_session
from ..services.models import Ticket, Project
from ..services.scoring import recalc_scores

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.get("")
def list_tickets(project_id: Optional[int] = None, session: Session = Depends(get_session)):
    query = select(Ticket)
    if project_id is not None:
        query = query.where(Ticket.project_id == project_id)
    return session.exec(query).all()

@router.post("")
def create_ticket(ticket: Ticket, session: Session = Depends(get_session)):
    # validate project exists
    project = session.get(Project, ticket.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    recalc_scores(session)
    return ticket

@router.patch("/{ticket_id}")
def update_ticket(ticket_id: int, payload: dict, session: Session = Depends(get_session)):
    t = session.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for k, v in payload.items():
        if hasattr(t, k):
            setattr(t, k, v)
    session.add(t)
    session.commit()
    recalc_scores(session)
    session.refresh(t)
    return t

@router.post("/recalc")
def force_recalc(session: Session = Depends(get_session)):
    recalc_scores(session)
    return {"ok": True}
