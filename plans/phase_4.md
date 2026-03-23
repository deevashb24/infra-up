# Phase 4: Core Features (Permit Transparency & Citizen Reporting)

## Overview
Build dedicated pages for deep-diving into individual permits (transparency pages) and a citizen-facing flow for reporting local infrastructure issues.

## File Structure
```text
frontend/
├── app/
│   ├── permits/
│   │   └── [id]/
│   │       └── page.tsx (Permit Details Page)
│   └── report/
│       └── page.tsx (Citizen Reporting Flow)
└── components/
    ├── Permits/
    │   ├── PermitTimeline.tsx
    │   ├── ContractorDetails.tsx
    │   └── ImpactAssessment.tsx
    └── Reports/
        ├── ReportWizard.tsx
        ├── LocationPickerMap.tsx
        └── MediaUploader.tsx
```

## Component Names
- `PermitTimeline`: Visual tracker for permit lifecycles (Pending -> Active -> Completed).
- `ReportWizard`: Multi-step form for citizens (1. Category, 2. Location, 3. Photos).
- `LocationPickerMap`: A mini map instance allowing users to drop a pin for their report.

## API Endpoints
- `GET /api/v1/permits/{id}`: Fetch detailed metadata for a specific permit.
- `POST /api/v1/reports`: Submit a citizen report with a PostGIS point.
- `POST /api/v1/uploads`: Handle image uploads for citizen reports (AWS S3 or Local).

## Database Schema Additions
- **`report_media`**
  - `id` (UUID, PK)
  - `report_id` (UUID, FK -> reports.id)
  - `file_url` (String)
  - `uploaded_at` (Timestamp)
```
