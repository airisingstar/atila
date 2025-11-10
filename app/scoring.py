from datetime import datetime, timezone
from typing import List, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Ticket, Project


# ---------------------------
# Priority Weights
# ---------------------------
BASE_WEIGHTS = {
    "Highest": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
    "Backlog": 0,
    "Completed": 0,
}
AGE_MULTIPLIER = {
    "Highest": 2.0,
    "High": 2.0,
    "Medium": 1.0,
    "Low": 1.0,
    "Backlog": 5.0,      # backlog ages more aggressively
    "Completed": 0.0,
}


# ---------------------------
# Core Scoring
# ---------------------------
def compute_pscore(ticket: Ticket, now: datetime) -> float:
    """Compute a weighted priority score based on age and base weight."""
    priority = str(ticket.priority or "Medium")
    base = BASE_WEIGHTS.get(priority, 2)
    mult = AGE_MULTIPLIER.get(priority, 1.0)

    if isinstance(ticket.created_at, datetime):
        age_days = max(
            0.0,
            (now - ticket.created_at.replace(tzinfo=None)).total_seconds() / 86400.0,
        )
    else:
        age_days = 0.0

    return round(base + mult * age_days, 4)


def rank_and_assign_display_scores(tickets: List[Ticket]) -> Tuple[List[Ticket], List[Ticket], List[Ticket]]:
    """Rank tickets and assign display and ticket_order IDs."""
    active = [t for t in tickets if t.status == "Active"]
    backlog = [t for t in tickets if t.status == "Backlog"]
    completed = [t for t in tickets if t.status == "Completed"]

    # Active: highest first
    active.sort(key=lambda t: (-t.pscore, t.created_at, t.id or 0))
    for i, t in enumerate(active, start=1):
        t.display_score = i
        t.ticket_order_id = i

    # Backlog: lower weight but aging
    backlog.sort(key=lambda t: (-t.pscore, t.created_at, t.id or 0))
    for i, t in enumerate(backlog, start=1):
        t.display_score = 1000 + i
        t.ticket_order_id = 10000 + i

    # Completed: oldest first
    completed.sort(key=lambda t: (t.created_at, t.id or 0))
    for i, t in enumerate(completed, start=1):
        t.display_score = 10000 + i
        t.ticket_order_id = 100000 + i

    return active, backlog, completed


# ---------------------------
# Assignment per Project
# ---------------------------
def assign_all_scores_for_project(session: Session, project_id: int):
    """Recalculate scores and display order for all tickets in a project."""
    now = datetime.now(timezone.utc).astimezone().replace(tzinfo=None)

    tickets = session.execute(
        select(Ticket).where(Ticket.project_id == project_id)
    ).scalars().all()

    for t in tickets:
        t.pscore = compute_pscore(t, now)

    a, b, c = rank_and_assign_display_scores(tickets)
    session.add_all(a + b + c)
    session.commit()


def recalc_scores(session: Session):
    """Recalculate scores for all projects."""
    projects = session.execute(select(Project)).scalars().all()
    for p in projects:
        assign_all_scores_for_project(session, p.id)
