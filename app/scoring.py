from datetime import datetime, timezone
from typing import List, Tuple

from sqlmodel import select
from .models import Ticket, Project, Priority, TicketStatus


# Base priority weights & age multipliers
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


def compute_pscore(ticket: Ticket, now: datetime) -> float:
    pr = ticket.priority.value if isinstance(ticket.priority, Priority) else str(ticket.priority)
    priority = pr if pr in BASE_WEIGHTS else "Medium"
    base = BASE_WEIGHTS[priority]
    mult = AGE_MULTIPLIER[priority]
    # Ensure naive arithmetic (SQLite stores naive UTC via default)
    age_days = max(
        0.0,
        (now - ticket.created_at.replace(tzinfo=None)).total_seconds() / 86400.0
        if isinstance(ticket.created_at, datetime) else 0.0
    )
    return round(base + mult * age_days, 4)


def rank_and_assign_display_scores(tickets: List[Ticket]) -> Tuple[List[Ticket], List[Ticket], List[Ticket]]:
    # Split groups
    active = [t for t in tickets if t.status == TicketStatus.Active]
    backlog = [t for t in tickets if t.status == TicketStatus.Backlog]
    completed = [t for t in tickets if t.status == TicketStatus.Completed]

    # Active: sort by pscore desc, then created_at asc (older first), assign 1..n
    active.sort(key=lambda t: (-t.pscore, t.created_at, t.id or 0))
    for i, t in enumerate(active, start=1):
        t.display_score = i
        t.ticket_order_id = i  # Ticket_ID range for active

    # Backlog: order by pscore desc, created_at asc, assign 10000+
    backlog.sort(key=lambda t: (-t.pscore, t.created_at, t.id or 0))
    for i, t in enumerate(backlog, start=1):
        t.display_score = 1000 + i
        t.ticket_order_id = 10000 + i

    # Completed: oldest first, assign 100000+
    completed.sort(key=lambda t: (t.created_at, t.id or 0))
    for i, t in enumerate(completed, start=1):
        t.display_score = 10000 + i
        t.ticket_order_id = 100000 + i

    return active, backlog, completed


def assign_all_scores_for_project(session, project_id: int):
    """Recalculate pscore & ticket_order_id for all tickets in a project."""
    now = datetime.now(timezone.utc).astimezone().replace(tzinfo=None)

    tickets = session.exec(select(Ticket).where(Ticket.project_id == project_id)).all()
    for t in tickets:
        t.pscore = compute_pscore(t, now)

    # rank + assign display & ticket IDs
    a, b, c = rank_and_assign_display_scores(tickets)
    session.add_all(a + b + c)
    session.commit()


def recalc_scores(session):
    """Recalculate for ALL projects (used on startup or periodic)."""
    projects = session.exec(select(Project)).all()
    for p in projects:
        assign_all_scores_for_project(session, p.id)
