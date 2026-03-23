# Phase 1: Foundation Setup & Database Architecture

## Overview
Initialize the project workspace, define the monorepo structure, set up Docker environments, and establish the core PostgreSQL + PostGIS database schema.

## File Structure
```text
/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── app/
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── app/
```

## Database Schema (PostgreSQL + PostGIS)
- **`users`**
  - `id` (UUID, PK)
  - `email` (String, Unique)
  - `password_hash` (String)
  - `role` (Enum: CITIZEN, ADMIN, MUNICIPALITY)
  - `created_at` (Timestamp)
- **`permits`**
  - `id` (UUID, PK)
  - `title` (String)
  - `type` (Enum: CONSTRUCTION, ROAD, UTILITY)
  - `status` (Enum: PENDING, ACTIVE, COMPLETED)
  - `geometry` (Geometry: Point/Polygon)
  - `start_date` (Timestamp)
  - `end_date` (Timestamp)
  - `impact_level` (Enum: LOW, MEDIUM, HIGH)
- **`reports`**
  - `id` (UUID, PK)
  - `user_id` (UUID, FK -> users.id)
  - `category` (Enum: POTHOLE, SAFETY_HAZARD, NOISE)
  - `geometry` (Geometry: Point)
  - `description` (Text)
  - `status` (Enum: OPEN, IN_PROGRESS, RESOLVED)
- **`user_routes`**
  - `id` (UUID, PK)
  - `user_id` (UUID, FK -> users.id)
  - `route_line` (Geometry: LineString)
```
