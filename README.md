# Urban Infrastructure Intelligence Platform

A civic tech startup platform letting citizens, logistics companies, and municipal governments see verified construction permits on an interactive map.

## Core Features
1. Interactive map with construction/road/utility markers
2. Smart alerts for route-affecting work
3. Permit transparency pages
4. Citizen reporting
5. Government dashboard

## Tech Stack
* **Frontend:** Next.js, Tailwind CSS, MapLibre GL JS
* **Backend:** FastAPI, Python
* **Database:** PostgreSQL + PostGIS, Redis

## Structure
* `/frontend`: Next.js web application
* `/backend`: FastAPI Python server
* `/shared`: Shared definitions and constants
* `/plans`: Phase-by-phase implementation plans

## Getting Started

### Database Services
Ensure you have Docker installed. Run the following to start PostgreSQL with PostGIS and Redis:
```bash
docker-compose up -d
```

### Backend Setup
Navigate to `/backend`, create a virtual environment, and install dependencies.
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
Navigate to `/frontend` and run the development server.
```bash
cd frontend
npm install
npm run dev
```
