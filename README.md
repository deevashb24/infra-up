<div align="center">
  <img src="https://img.shields.io/badge/Status-Active-success" alt="Status" />
  <img src="https://img.shields.io/badge/License-MIT-blue" alt="License" />
  <img src="https://img.shields.io/badge/Version-1.0.0-orange" alt="Version" />
</div>

<h1 align="center">🏙️ Infra Up — Civic Tech Platform</h1>
<p align="center"><strong>Bridging the Gap Between Citizens, Logistics, and Municipalities</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-14-000000?logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-PostGIS-4169E1?logo=postgresql&logoColor=white" alt="PostGIS" />
  <img src="https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/MapLibre_GL-Maps-4264FB?logo=mapbox&logoColor=white" alt="MapLibre" />
</p>

---

## 📖 Overview

**Infra Up** is a comprehensive civic technology platform designed to make urban infrastructure development fully transparent. 

Instead of citizens guessing why a road is dug up or logistics companies running into unexpected construction delays, this platform visualizes all verified government infrastructure projects (road widening, sewerage upgrades, metro line extensions) on a live, interactive map. 

---

## 📸 Application Screenshots

### Live Density Map & Citizen Reporting
*The main interactive map powered by WebGL (MapLibre), featuring spatial clustering and 3D buildings.*
![Map View](./frontend/public/screenshot_map.png)

### Government Analytics Dashboard
*The real-time admin dashboard tracking project delays, budget utilization, and citizen safety reports.*
![Dashboard View](./frontend/public/screenshot_dashboard.png)

---

## ✨ Core Features

- 🗺️ **Interactive Density Map**: Visualizes projects using heatmaps and cluster bubbles. Users can filter by project type (Road, Utility, Construction).
- 🔔 **Real-Time Smart Alerts**: Powered by Server-Sent Events (SSE) and PostgreSQL Triggers (`pg_notify`), users receive instant popup notifications the exact second a new project is created—no page refreshes required.
- 📋 **Permit Transparency**: See which authority (e.g., NHAI, PWD, Jal Nigam) is responsible, what the budget is, and the exact completion percentage.
- 📸 **Citizen Reporting**: Users can drop pins on the map to report safety hazards or unverified construction. These reports flow instantly into the government dashboard.
- 👨‍💼 **Analytics Dashboard**: Tracks KPIs like Total CapEx, active vs. delayed projects, and provides breakdowns by Authority.
- 🌍 **Multilingual Support**: UI toggles seamlessly between English and Hindi.

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph Frontend["📱 Next.js PWA"]
        Map[Interactive Map<br/>MapLibre GL JS]
        Alerts[Route Alerts]
        Reporting[Citizen Reports]
        AdminUI[Admin Dashboard]
    end

    subgraph Backend["⚙️ FastAPI"]
        API[REST API]
        SSE[SSE Streamer]
        Scrapers[Data Scrapers]
    end

    subgraph Infrastructure["🗄️ Infrastructure"]
        PG[(PostgreSQL<br/>+ PostGIS)]
        Redis[(Redis Cache)]
    end

    Map --> API
    Alerts -.-> SSE
    Reporting --> API
    AdminUI --> API
    API --> PG
    API --> Redis
    SSE -.-> PG
    Scrapers --> PG
```

### The Data Flow
1. **Map Loading**: When the frontend asks for projects, FastAPI checks **Redis**. If cached, it returns instantly. If not, it runs geospatial queries on **PostGIS**, formats the data as a GeoJSON `FeatureCollection`, saves it to Redis, and sends it to the frontend.
2. **Instant Alerts**: If a scraper pushes a new infrastructure project into the database, a Postgres trigger runs natively. It alerts the FastAPI server via a socket, which broadcasts the alert to all connected browsers via SSE.

---

## 🚀 Quick Start

The entire stack is containerized for a frictionless setup.

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### One-Click Run (Recommended)

Start the entire platform (PostGIS, Redis, FastAPI, Next.js) using Docker:

```bash
docker compose up --build
```

- 🌐 **Frontend (UI)**: `http://localhost:3000`
- 📡 **Backend (API)**: `http://localhost:8000`
- 📖 **API Docs (Swagger)**: `http://localhost:8000/docs`

### Seeding the Database
To populate the database with realistic sample projects, run the seeder inside the backend container:

```bash
docker exec civic_backend python -m seed
```

*(Note: If you run this while the app is open, you will need to flush Redis `docker exec civic_redis redis-cli flushall` to bypass the 5-minute cache).*

---

## 🤝 Contributing

We welcome contributions to help make urban infrastructure more transparent!

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  <strong>Making urban infrastructure transparent 🏙️</strong>
</p>
