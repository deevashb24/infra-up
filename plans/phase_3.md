# Phase 3: Frontend Scaffolding & Map Integration 

## Overview
Set up Next.js app router, configure Tailwind CSS, and integrate MapLibre GL JS for the highly interactive map interface serving as the primary user view.

## File Structure
```text
frontend/
├── tailwind.config.ts
├── app/
│   ├── layout.tsx
│   ├── page.tsx (Landing Page)
│   └── map/
│       └── page.tsx (Interactive Map Page)
├── components/
│   ├── Map/
│   │   ├── InteractiveMap.tsx
│   │   ├── MapControls.tsx
│   │   └── Layers/
│   │       ├── PermitLayer.tsx
│   │       └── ReportLayer.tsx
│   ├── UI/
│   │   ├── Button.tsx
│   │   ├── Modal.tsx
│   │   └── Navigation.tsx
└── lib/
    ├── api.ts
    └── map-utils.ts
```

## Component Names
- `InteractiveMap`: The main MapLibre map container instance.
- `PermitLayer`: Source and layer management for rendering permit geojson data.
- `FilterSidebar`: Slide-out panel for filtering the map by date, type, and status.
- `PopupCard`: Click-to-reveal card displaying basic permit or report info on the map.

## API Endpoints Handled By Map
- Map fetches dynamic GeoJSON via `GET /api/v1/permits?bbox={viewport}` during panning and zooming.
- Map fetches report GeoJSON via `GET /api/v1/reports?bbox={viewport}`.

## Database Schema Additions
- None necessary during frontend scaffolding layer. Schema established in phase 1 supports mapping.
```
