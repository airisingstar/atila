from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum

# --------------------------------------
# Enums
# --------------------------------------
class Methodology(str, Enum):
    agile = "agile"
    scrum = "scrum"
    classic = "classic"
    custom = "custom"

# --------------------------------------
# Models
# --------------------------------------
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    type: str = "Business"
    priority: str = "Medium"
    status: str = "Planned"
    methodology: Methodology = Field(default=Methodology.scrum)
    requirement: Optional[str] = None
    planned_start_date: datetime = Field(default_factory=lambda: datetime(2025,10,1))
    planned_end_date: str = "Continuous"
    sprint_length_days: int = 14
    current_sprint_name: Optional[str] = None
    tickets: List["Ticket"] = Relationship(back_populates="project")

class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    title: str
    description: Optional[str] = None
    priority: str = "Medium"
    status: str = "Building"
    queue: Optional[str] = None
    etl_validated: bool = False
    activated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    pscore: float = 0.0
    display_score: int = 0
    project: Optional[Project] = Relationship(back_populates="tickets")
