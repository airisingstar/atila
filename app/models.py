from __future__ import annotations
from datetime import datetime, date
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


# ---------------------------
# Constants (string enums)
# ---------------------------
PROJECT_TYPES = ["business", "technical", "research"]
PROJECT_STATUSES = ["Created", "Building", "Active", "Archived"]
PRIORITIES = ["Highest", "High", "Medium", "Low", "Backlog", "Completed"]
TICKET_STATUSES = ["Active", "Backlog", "Completed"]
TICKET_CATEGORIES = [
    "Product Management",
    "Product Quality",
    "Product Scaling",
    "Other",
]


# ---------------------------
# Models
# ---------------------------
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None

    # plain strings instead of Enum types
    type: str = Field(default="business", description="Project type")
    priority: str = Field(default="Medium", description="Priority level")
    status: str = Field(default="Created", description="Project status")

    tags: str = Field(default="Score:[0.00], Ticket_ID:0")

    planned_start_date: Optional[date] = Field(default_factory=date.today)
    planned_end_date: Optional[date] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    tickets: List["Ticket"] = Relationship(back_populates="project")


class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    description: Optional[str] = None

    priority: str = Field(default="Medium")
    status: str = Field(default="Backlog")
    category: str = Field(default="Product Management")

    pscore: float = Field(default=0.0, index=True)
    display_score: int = Field(default=0)
    ticket_order_id: int = Field(default=0)

    project_id: int = Field(foreign_key="project.id")
    project: Optional[Project] = Relationship(back_populates="tickets")

    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None

    assignee: Optional[str] = None
    integration_source: Optional[str] = None
    integration_id: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
