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
from .models import InfrastructureProject, Report, StatusEnum # type: ignore
from .schemas import ProjectResponse, ProjectCreate, ReportCreate, ReportResponse # type: ignore
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

@app.get("/projects")
def get_projects(
    bbox: Optional[str] = Query(None, description="Bounding box in format: min_lon,min_lat,max_lon,max_lat"),
    db: Session = Depends(get_db)
):
    cache_key = f"projects_bbox_{bbox}" if bbox else "projects_all"
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

    projects = query.all()

    features = []
    for p in projects:
        # FIX #2: Scope the geometry extraction to this specific project's geometry
        # instead of querying the full table and taking first().
        coords = db.execute(
            text("SELECT ST_X(geometry::geometry), ST_Y(geometry::geometry) FROM infrastructure_projects WHERE id = :pid"),
            {"pid": p.id}
        ).first()
        lon, lat = (coords[0], coords[1]) if coords else (0.0, 0.0)

        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "id": str(p.id),
                "title": p.title,
                "permitType": p.permit_type.value,
                "status": p.status.value,
                "project_authority": p.project_authority.value,
                "district": p.district,
                "impactLevel": p.impact_level.value,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "end_date": p.end_date.isoformat() if p.end_date else None,
            }
        }
        features.append(feature)

    feature_collection = {"type": "FeatureCollection", "features": features}
    set_cached_data(cache_key, feature_collection, expire=300)
    return feature_collection

@app.post("/reports", response_model=ReportResponse)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    geom = f"POINT({report.longitude} {report.latitude})"
    db_report = Report(description=report.description, geometry=func.ST_GeomFromText(geom, 4326))
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    # FIX #3: Scope extraction to the specific report just inserted.
    coords = db.execute(
        text("SELECT ST_X(geometry::geometry), ST_Y(geometry::geometry) FROM reports WHERE id = :rid"),
        {"rid": db_report.id}
    ).first()
    lon = coords[0] if coords else report.longitude
    lat = coords[1] if coords else report.latitude

    return {
        "id": db_report.id,
        "description": db_report.description,
        "longitude": lon,
        "latitude": lat
    }

@app.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    cached = get_cached_data("dashboard_stats")
    if cached:
        return cached

    total_projects = db.query(func.count(InfrastructureProject.id)).scalar()
    # FIX #7: Use the enum member, not a plain string, for reliable comparison.
    active_projects = db.query(func.count(InfrastructureProject.id)).filter(
        InfrastructureProject.status == StatusEnum.ACTIVE
    ).scalar()
    total_reports = db.query(func.count(Report.id)).scalar()

    stats = {"total_projects": total_projects, "active_projects": active_projects, "total_reports": total_reports}
    set_cached_data("dashboard_stats", stats, expire=600)
    return stats


class IngestPayload(BaseModel):
    title: str
    description: Optional[str] = None
    raw_type: str
    authority: str
    district: str
    longitude: float
    latitude: float
    budget: Optional[float] = None

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
        # FIX #4: Actually persist the budget value that was sent in the payload.
        budget=payload.budget,
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
