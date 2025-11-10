from __future__ import annotations
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    Float,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel

Base = declarative_base()


# ---------------------------
# SQLAlchemy ORM Tables
# ---------------------------
class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)

    type = Column(String, default="business")
    priority = Column(String, default="Medium")
    status = Column(String, default="Created")

    tags = Column(String, default="Score:[0.00], Ticket_ID:0")

    planned_start_date = Column(Date, default=date.today)
    planned_end_date = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    tickets = relationship("Ticket", back_populates="project")


class Ticket(Base):
    __tablename__ = "ticket"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String, nullable=True)

    priority = Column(String, default="Medium")
    status = Column(String, default="Backlog")
    category = Column(String, default="Product Management")

    pscore = Column(Float, default=0.0, index=True)
    display_score = Column(Integer, default=0)
    ticket_order_id = Column(Integer, default=0)

    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="tickets")

    planned_start_date = Column(Date, nullable=True)
    planned_end_date = Column(Date, nullable=True)

    assignee = Column(String, nullable=True)
    integration_source = Column(String, nullable=True)
    integration_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


# ---------------------------
# Pydantic Models for API I/O
# ---------------------------
class ProjectSchema(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str]
    type: str = "business"
    priority: str = "Medium"
    status: str = "Created"
    tags: str = "Score:[0.00], Ticket_ID:0"

    class Config:
        orm_mode = True


class TicketSchema(BaseModel):
    id: Optional[int]
    title: str
    description: Optional[str]
    priority: str = "Medium"
    status: str = "Backlog"
    category: str = "Product Management"
    pscore: float = 0.0
    display_score: int = 0
    project_id: Optional[int]

    class Config:
        orm_mode = True
