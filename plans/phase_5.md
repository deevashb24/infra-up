# Phase 5: Smart Alerts & Redis Caching

## Overview
Implement scalable background jobs and caching using Redis to support intelligent route-based alerts (e.g., notifying citizens when construction overlaps their commute).

## File Structure
```text
backend/app/
├── core/
│   └── redis.py
├── services/
│   ├── cache_service.py
│   ├── routing_service.py
│   └── alert_evaluator.py
└── worker.py (Background/Worker Service)

frontend/app/
└── settings/
    └── alerts/
        └── page.tsx
```

## Component Names
- `RouteManager`: Frontend component for users to draw or save their commute routes.
- `AlertInbox`: Dropdown or dashboard page showing active notifications for the user.
- `CacheService` (Backend Class): Wrapper around Redis for map tile/GeoJSON bounding box caching.
- `AlertEvaluator` (Backend Service): Calculates spatial intersections (`ST_Intersects` or strict radii) between `user_routes` and new `permits`.

## API Endpoints
- `POST /api/v1/user/routes`: Save a geometric linestring representing a commute.
- `GET /api/v1/user/alerts`: Retrieve generated smart alerts.
- `POST /api/v1/user/alerts/{id}/read`: Mark alert as read.

## Database Schema Additions
- **`alerts`**
  - `id` (UUID, PK)
  - `user_id` (UUID, FK -> users.id)
  - `message` (String)
  - `related_permit_id` (UUID, FK -> permits.id, nullable)
  - `is_read` (Boolean, default: False)
  - `created_at` (Timestamp)
```
