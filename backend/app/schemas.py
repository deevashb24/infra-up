from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from .models import AuthorityEnum, ProjectTypeEnum, StatusEnum, ImpactEnum

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    permit_type: ProjectTypeEnum
    status: StatusEnum
    project_authority: AuthorityEnum
    district: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    impact_level: ImpactEnum
    longitude: float
    latitude: float
    budget: Optional[float] = None
    contractor: Optional[str] = None
    completion_percent: Optional[float] = 0
    division: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: UUID
    is_verified: bool = False
    model_config = ConfigDict(from_attributes=True)

class ReportCreate(BaseModel):
    description: str
    longitude: float
    latitude: float

class ReportResponse(ReportCreate):
    id: UUID
    created_at: Optional[datetime] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class DashboardStats(BaseModel):
    total_projects: int
    active_projects: int
    delayed_count: int
    total_budget: float
    total_reports: int
    by_type: list
    by_authority: list

class ReportListItem(BaseModel):
    id: UUID
    description: str
    category: Optional[str] = None
    severity: Optional[str] = None
    created_at: Optional[datetime] = None
    longitude: float
    latitude: float
    model_config = ConfigDict(from_attributes=True)
