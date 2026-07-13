from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from .models import AuthorityEnum, ProjectTypeEnum, StatusEnum, ImpactEnum

class ProjectBase(BaseModel):
    title: str = Field(..., max_length=200, strip_whitespace=True)
    description: Optional[str] = Field(None, max_length=2000, strip_whitespace=True)
    permit_type: ProjectTypeEnum
    status: StatusEnum
    project_authority: AuthorityEnum
    district: str = Field(..., max_length=100, strip_whitespace=True)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    impact_level: ImpactEnum
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    budget: Optional[float] = Field(None, ge=0)
    contractor: Optional[str] = Field(None, max_length=200, strip_whitespace=True)
    completion_percent: Optional[float] = Field(0, ge=0, le=100)
    division: Optional[str] = Field(None, max_length=100, strip_whitespace=True)

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: UUID
    is_verified: bool = False
    model_config = ConfigDict(from_attributes=True)

class ReportCreate(BaseModel):
    description: str = Field(..., max_length=2000, strip_whitespace=True)
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)

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
