# pyre-ignore-all-errors[21]
from fastapi import FastAPI, Depends, HTTPException, Query # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from starlette.responses import StreamingResponse # type: ignore
from starlette.requests import Request # type: ignore
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy import func, text # type: ignore
from pydantic import BaseModel # type: ignore
from typing import List, Optional
import psycopg2 # type: ignore
import select
import json
import os
import asyncio

from .database import engine, Base, get_db, RAW_DATABASE_URL # type: ignore
from .models import InfrastructureProject, Report, StatusEnum, ProjectTypeEnum # type: ignore
from .schemas import ( # type: ignore
    ProjectResponse, ProjectCreate, ReportCreate, ReportResponse,
    DashboardStats, ReportListItem,
)
from .redis_client import get_cached_data, set_cached_data # type: ignore

# Automatically create all tables and apply Postgres Triggers
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Civic Tech API - Phase 4 Alerts")

# FIX #13: CORS — allow_credentials=True is incompatible with allow_origins=["*"].
# Use explicit origins or disable credentials.
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Helper: extract lon/lat from a PostGIS geometry ─────────────────────────
def _extract_coords(db: Session, table: str, pk_col: str, pk_val) -> tuple:
    """Return (lon, lat) for a given row's geometry column."""
    row = db.execute(
        text(f"SELECT ST_X(geometry::geometry), ST_Y(geometry::geometry) FROM {table} WHERE {pk_col} = :pk"),
        {"pk": pk_val},
    ).first()
    return (row[0], row[1]) if row else (0.0, 0.0)


# ── SSE Alert Stream ────────────────────────────────────────────────────────
async def db_listen(request: Request):
    """
    FIX #1: Generator now checks client disconnect on each iteration to avoid
    connection leaks and thread exhaustion. Uses RAW_DATABASE_URL (always psycopg2
    compatible — stripped of any +asyncpg prefix).
    """
    conn = None
    try:
        conn = psycopg2.connect(RAW_DATABASE_URL)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        curs = conn.cursor()
        curs.execute("LISTEN new_up_alert;")

        while True:
            # Check client disconnect before blocking
            if await request.is_disconnected():
                break

            if select.select([conn], [], [], 5) == ([], [], []):
                yield "data: keep-alive\n\n"
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    yield f"data: {notify.payload}\n\n"

            # Yield control back to event loop so disconnect check is responsive
            await asyncio.sleep(0)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

@app.get("/api/alerts/stream")
async def stream_alerts(request: Request):
    """SSE Endpoint broadcasting real-time DB pushes."""
    return StreamingResponse(db_listen(request), media_type="text/event-stream")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "FastAPI is running Phase 4 Alerts"}


# ── GET /projects — GeoJSON FeatureCollection ────────────────────────────────
@app.get("/projects")
def get_projects(
    bbox: Optional[str] = Query(None, description="Bounding box in format: min_lon,min_lat,max_lon,max_lat"),
    district: Optional[str] = Query(None),
    division: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    cache_key = f"projects_{bbox}_{district}_{division}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached

    query = db.query(InfrastructureProject)

    if bbox:
        try:
            min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
            bbox_polygon = f"POLYGON(({min_lon} {min_lat}, {min_lon} {max_lat}, {max_lon} {max_lat}, {max_lon} {min_lat}, {min_lon} {min_lat}))"
            query = query.filter(func.ST_Intersects(
                InfrastructureProject.geometry,
                func.ST_GeomFromText(bbox_polygon, 4326)
            ))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid bbox format. Use min_lon,min_lat,max_lon,max_lat")

    if district:
        query = query.filter(InfrastructureProject.district == district)
    if division:
        query = query.filter(InfrastructureProject.division == division)

    projects = query.all()

    features = []
    for p in projects:
        lon, lat = _extract_coords(db, "infrastructure_projects", "id", p.id)

        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "id": str(p.id),
                "title": p.title,
                "permitType": p.permit_type.value if p.permit_type else "CONSTRUCTION",
                "status": p.status.value if p.status else "PENDING",
                "project_authority": p.project_authority.value if p.project_authority else "",
                "contractor": p.contractor or (p.project_authority.value if p.project_authority else ""),
                "district": p.district or "",
                "division": p.division or "",
                "impactLevel": p.impact_level.value if p.impact_level else "MEDIUM",
                "budget": p.budget or 0,
                "completion_percent": p.completion_percent or 0,
                "startDate": p.start_date.isoformat() if p.start_date else None,
                "endDate": p.end_date.isoformat() if p.end_date else None,
                "is_verified": p.is_verified or False,
            }
        }
        features.append(feature)

    feature_collection = {"type": "FeatureCollection", "features": features}
    set_cached_data(cache_key, feature_collection, expire=300)
    return feature_collection


# ── GET /projects/{id} — single project detail ──────────────────────────────
@app.get("/projects/{project_id}")
def get_project_detail(project_id: str, db: Session = Depends(get_db)):
    project = db.query(InfrastructureProject).filter(
        InfrastructureProject.id == project_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    lon, lat = _extract_coords(db, "infrastructure_projects", "id", project.id)

    # Count citizen reports within 500m of this project
    report_count = 0
    try:
        geom_text = f"POINT({lon} {lat})"
        report_count = db.query(func.count(Report.id)).filter(
            func.ST_DWithin(
                Report.geometry,
                func.ST_GeomFromText(geom_text, 4326),
                0.005  # ~500m
            )
        ).scalar() or 0
    except Exception:
        pass

    return {
        "id": str(project.id),
        "title": project.title,
        "description": project.description,
        "permitType": project.permit_type.value if project.permit_type else "CONSTRUCTION",
        "status": project.status.value if project.status else "PENDING",
        "project_authority": project.project_authority.value if project.project_authority else "",
        "contractor": project.contractor or (project.project_authority.value if project.project_authority else ""),
        "district": project.district or "",
        "division": project.division or "",
        "impactLevel": project.impact_level.value if project.impact_level else "MEDIUM",
        "budget": project.budget or 0,
        "completion_percent": project.completion_percent or 0,
        "startDate": project.start_date.isoformat() if project.start_date else None,
        "endDate": project.end_date.isoformat() if project.end_date else None,
        "is_verified": project.is_verified or False,
        "longitude": lon,
        "latitude": lat,
        "report_count": report_count,
    }


# ── POST /reports ────────────────────────────────────────────────────────────
@app.post("/reports", response_model=ReportResponse)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    geom = f"POINT({report.longitude} {report.latitude})"
    db_report = Report(description=report.description, geometry=func.ST_GeomFromText(geom, 4326))
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    lon, lat = _extract_coords(db, "reports", "id", db_report.id)

    return {
        "id": db_report.id,
        "description": db_report.description,
        "longitude": lon or report.longitude,
        "latitude": lat or report.latitude,
        "created_at": db_report.created_at,
        "category": db_report.category,
        "severity": db_report.severity,
    }


# ── GET /reports — list all citizen reports ──────────────────────────────────
@app.get("/reports")
def list_reports(
    division: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    cached_key = f"reports_{division}"
    cached = get_cached_data(cached_key)
    if cached:
        return cached

    reports = db.query(Report).order_by(Report.created_at.desc()).limit(100).all()

    result = []
    for r in reports:
        lon, lat = _extract_coords(db, "reports", "id", r.id)
        result.append({
            "id": str(r.id),
            "description": r.description,
            "category": r.category or "Safety Hazard",
            "severity": r.severity or "High",
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "longitude": lon,
            "latitude": lat,
        })

    set_cached_data(cached_key, result, expire=120)
    return result


# ── GET /dashboard/stats — expanded dashboard statistics ─────────────────────
@app.get("/dashboard/stats")
def get_dashboard_stats(
    division: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    cache_key = f"dashboard_stats_{division}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached

    base_q = db.query(InfrastructureProject)
    if division and division != "All Divisions":
        base_q = base_q.filter(InfrastructureProject.division == division)

    all_projects = base_q.all()

    total = len(all_projects)
    active = sum(1 for p in all_projects if p.status == StatusEnum.ACTIVE)
    delayed = sum(1 for p in all_projects if p.status == StatusEnum.PENDING)
    total_budget = sum((p.budget or 0) for p in all_projects)

    # Type breakdown
    type_counts = {}
    for p in all_projects:
        t = p.permit_type.value if p.permit_type else "CONSTRUCTION"
        type_counts[t] = type_counts.get(t, 0) + 1
    by_type = [{"name": k, "value": v} for k, v in type_counts.items()]

    # Authority breakdown
    authority_counts: dict = {}
    for p in all_projects:
        a = p.project_authority.value if p.project_authority else "Unknown"
        if a not in authority_counts:
            authority_counts[a] = {"Active": 0, "Delayed": 0}
        if p.status == StatusEnum.ACTIVE:
            authority_counts[a]["Active"] += 1
        else:
            authority_counts[a]["Delayed"] += 1
    by_authority = [{"name": k, **v} for k, v in authority_counts.items()]

    total_reports = db.query(func.count(Report.id)).scalar() or 0

    stats = {
        "total_projects": total,
        "active_projects": active,
        "delayed_count": delayed,
        "total_budget": total_budget,
        "total_reports": total_reports,
        "by_type": by_type,
        "by_authority": by_authority,
    }
    set_cached_data(cache_key, stats, expire=300)
    return stats


# ── POST /admin/ingest ───────────────────────────────────────────────────────
class IngestPayload(BaseModel):
    title: str
    description: Optional[str] = None
    raw_type: str
    authority: str
    district: str
    longitude: float
    latitude: float
    budget: Optional[float] = None
    contractor: Optional[str] = None
    division: Optional[str] = None
    completion_percent: Optional[float] = 0

@app.post("/admin/ingest")
def ingest_project(payload: IngestPayload, db: Session = Depends(get_db)):
    """
    Endpoint for scrapers. Automatically standardises Hindi titles and dedupes geospatially.
    """
    from .standardize import transliterate_and_classify, standardize_authority # type: ignore

    classified_type = transliterate_and_classify(payload.title, payload.raw_type)
    std_authority = standardize_authority(payload.authority)

    geom_text = f"POINT({payload.longitude} {payload.latitude})"
    search_geom = func.ST_GeomFromText(geom_text, 4326)

    potential_duplicates = db.query(InfrastructureProject).filter(
        func.ST_DWithin(
            InfrastructureProject.geometry,
            search_geom,
            0.0005
        )
    ).all()

    is_verified = True
    for dup in potential_duplicates:
        tokens_new = set(payload.title.lower().split())
        tokens_dup = set(dup.title.lower().split())
        if len(tokens_new.intersection(tokens_dup)) > 1:
            return {"status": "rejected", "reason": "duplicate_detected", "merged_with_id": str(dup.id)}

    if len(potential_duplicates) > 0:
        is_verified = False

    db_project = InfrastructureProject(
        title=payload.title,
        description=payload.description,
        permit_type=classified_type,
        project_authority=std_authority,
        district=payload.district,
        geometry=search_geom,
        is_verified=is_verified,
        budget=payload.budget,
        contractor=payload.contractor,
        division=payload.division,
        completion_percent=payload.completion_percent or 0,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return {
        "status": "success_ingested",
        "id": str(db_project.id),
        "standardized_type": classified_type,
        "is_verified": is_verified
    }
