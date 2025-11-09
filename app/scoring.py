from datetime import datetime, timezone
from sqlmodel import select
from .models import Ticket

BASE_WEIGHTS = {"Highest":4,"High":3,"Medium":2,"Low":1,"Backlog":0,"Completed":0}
AGE_MULTIPLIER = {"Highest":2.0,"High":2.0,"Medium":1.0,"Low":1.0,"Backlog":5.0,"Completed":0.0}

def compute_pscore(ticket: Ticket, now: datetime) -> float:
    priority = ticket.priority if ticket.priority in BASE_WEIGHTS else "Medium"
    base = BASE_WEIGHTS[priority]
    mult = AGE_MULTIPLIER[priority]
    age_days = max(0.0, (now - ticket.created_at.replace(tzinfo=None)).total_seconds() / 86400.0)
    return base + mult * age_days

def recalc_scores(session):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    tickets = session.exec(select(Ticket)).all()
    for t in tickets:
        t.pscore = compute_pscore(t, now)
    session.add_all(tickets)
    session.commit()
