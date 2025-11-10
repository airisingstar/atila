from __future__ import annotations
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import String, Float, Integer, DateTime
from sqlmodel import SQLModel, Field


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
    name: str = Field(sa_column=String, index=True)
    description: Optional[str] = Field(default=None, sa_column=String)

    # plain strings instead of Enum types
    type: str = Field(default="business", description="Project type", sa_column=String)
    priority: str = Field(default="Medium", description="Priority level", sa_column=String)
    status: str = Field(default="Created", description="Project status", sa_column=String)

    tags: str = Field(default="Score:[0.00], Ticket_ID:0", sa_column=String)

    planned_start_date: Optional[date] = Field(default_factory=date.today)
    planned_end_date: Optional[date] = None

    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=DateTime)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=DateTime)

    # ✅ SQLAlchemy 2.x relationship syntax
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="project")


class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str = Field(sa_column=String)
    description: Optional[str] = Field(default=None, sa_column=String)

    priority: str = Field(default="Medium", sa_column=String)
    status: str = Field(default="Backlog", sa_column=String)
    category: str = Field(default="Product Management", sa_column=String)

    pscore: float = Field(default=0.0, index=True, sa_column=Float)
    display_score: int = Field(default=0, sa_column=Integer)
    ticket_order_id: int = Field(default=0, sa_column=Integer)

    project_id: int = Field(foreign_key="project.id")

    # ✅ SQLAlchemy 2.x relationship syntax
    project: Mapped[Optional["Project"]] = relationship(back_populates="tickets")

    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None

    assignee: Optional[str] = Field(default=None, sa_column=String)
    integration_source: Optional[str] = Field(default=None, sa_column=String)
    integration_id: Optional[str] = Field(default=None, sa_column=String)

    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=DateTime)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=DateTime)
