# Phase 2: Backend Core (FastAPI & Geospatial Queries)

## Overview
Develop the FastAPI backend architecture, configure SQLAlchemy with GeoAlchemy2 for spatial data handling, and implement core CRUD endpoints.

## File Structure
```text
backend/app/
├── main.py
├── core/
│   ├── config.py
│   ├── security.py
│   └── db.py
├── models/
│   ├── __init__.py
│   ├── permit.py
│   ├── report.py
│   └── user.py
├── schemas/
│   ├── permit.py
│   └── report.py
└── api/
    └── v1/
        ├── api.py
        ├── endpoints/
        │   ├── permits.py
        │   ├── reports.py
        │   └── auth.py
```

## API Endpoints
- **Auth**
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/register`
- **Permits**
  - `GET /api/v1/permits` (Query params: `bbox`, `type`, `status`)
  - `POST /api/v1/permits` (Admin only)
- **Reports**
  - `GET /api/v1/reports`
  - `POST /api/v1/reports`

## Component Names (Pydantic Schemas)
- `PermitCreate`, `PermitRead`, `PermitUpdate`
- `ReportCreate`, `ReportRead`, `ReportStatusUpdate`
- `BoundingBoxQuery`, `GeoFeatureCollectionRead`

## Database Schema (No major changes from Phase 1)
- Initializing the Alembic environment and generating the first geospatial migrations for users, permits, reports, and user_routes.
```
