# Phase 6: Government Dashboard & Final Polish

## Overview
Develop a secure interface for municipal administrators to manage the lifecycle of permits, moderate citizen reports, and view macro-level statistics. Add system-wide polish and error handling.

## File Structure
```text
frontend/
├── app/
│   └── admin/
│       ├── layout.tsx
│       ├── page.tsx (Analytics Dashboard)
│       ├── permits/
│       │   └── page.tsx (Data Grid)
│       └── reports/
│           └── page.tsx (Moderation Queue)
└── components/
    └── Admin/
        ├── Analytics/
        │   ├── StatCard.tsx
        │   ├── HeatmapWidget.tsx
        │   └── ActivityChart.tsx
        └── Tables/
            ├── PermitDataGrid.tsx
            └── ReportModerationTable.tsx
```

## Component Names
- `PermitDataGrid`: Advanced frontend table with sorting, filtering, exporting, and bulk actions.
- `HeatmapWidget`: Dashboard visualization showing high-concentration areas of permits or citizen complaints.
- `StatusToggle`: Quick action UI component to approve/reject permits.

## API Endpoints
- `GET /api/v1/admin/analytics`: Return aggregated metrics (e.g., active permits per category, average report resolution time).
- `PUT /api/v1/admin/permits/{id}/status`: Approve or close a permit.
- `PUT /api/v1/admin/reports/{id}/status`: Escalate, resolve, or dismiss a citizen report.

## Database Schema Update (Access Control)
- RBAC mechanisms enforced on backend: `MUNICIPALITY` or `ADMIN` roles verified via FastAPI Security Dependencies.
- **`audit_logs`** (Optional compliance addition)
  - `id` (UUID)
  - `admin_id` (UUID, FK -> users.id)
  - `action` (String)
  - `target_record` (String)
  - `timestamp` (Timestamp)
```
