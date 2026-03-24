from sqlalchemy import Column, String, Enum, DateTime, Float, func, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
import uuid
import enum
from .database import Base

class AuthorityEnum(str, enum.Enum):
    LDA = 'LDA'
    LMC = 'LMC'
    NHAI = 'NHAI'
    PWD_UP = 'PWD_UP'
    UPLCL = 'UPLCL'
    JAL_NIGAM = 'Jal Nigam'
    UPSIDA = 'UPSIDA'
    SMART_CITY = 'Smart City Lucknow'

class ProjectTypeEnum(str, enum.Enum):
    CONSTRUCTION = 'CONSTRUCTION'
    ROAD = 'ROAD'
    UTILITY = 'UTILITY'

class StatusEnum(str, enum.Enum):
    PENDING = 'PENDING'
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'

class ImpactEnum(str, enum.Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'

class InfrastructureProject(Base):
    __tablename__ = "infrastructure_projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    permit_type = Column(Enum(ProjectTypeEnum))
    status = Column(Enum(StatusEnum), default=StatusEnum.PENDING)
    project_authority = Column(Enum(AuthorityEnum))
    district = Column(String, index=True)
    geometry = Column(Geometry('POINT', srid=4326))
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    impact_level = Column(Enum(ImpactEnum), default=ImpactEnum.MEDIUM)
    is_verified = Column(Boolean, default=False)
    # FIX #4: Add budget column so ingested budget values are actually stored.
    budget = Column(Float, nullable=True)

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String)
    geometry = Column(Geometry('POINT', srid=4326))
    category = Column(String, default='Safety Hazard')
    severity = Column(String, default='High')
    created_at = Column(DateTime, default=func.now())

# -- Phase 4 Alert System Corridors & Subscriptions --

class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    geometry = Column(Geometry('GEOMETRY', srid=4326))
    created_at = Column(DateTime, default=func.now())

class UPHighwayCorridor(Base):
    __tablename__ = 'up_highway_corridors'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    geometry = Column(Geometry('LINESTRING', srid=4326))

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('infrastructure_projects.id'))
    message = Column(String)
    trigger_type = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
