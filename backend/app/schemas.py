from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
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
    model_config = ConfigDict(from_attributes=True)
