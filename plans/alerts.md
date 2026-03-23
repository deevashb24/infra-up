# Uttar Pradesh Infrastructure Alert System Design

## Overview
A smart alerting engine designed for UP citizens and commuters to receive real-time notifications about infrastructure projects affecting their daily routes or local areas.

## 1. Data Model (PostGIS / SQLAlchemy)

### Users & Subscriptions
```python
class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey('users.id'))
    name = Column(String) # e.g., "Commute to Hazratganj", "Home Area"
    geometry = Column(Geometry('GEOMETRY', srid=4326)) # Supports POLYGON (Areas) or LINESTRING (Routes)
    created_at = Column(DateTime, default=func.now())
```

### High-Impact UP Highway Corridors
We store critical UP state highways and expressways as LineString geometries to auto-tag critical infrastructure works.
```python
class UPHighwayCorridor(Base):
    __tablename__ = 'up_highway_corridors'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True) # e.g., "Agra-Lucknow Expressway", "NH-27"
    geometry = Column(Geometry('LINESTRING', srid=4326))
```

### Generated Alerts
```python
class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey('users.id'), nullable=True) # Null if system-wide broadcast
    project_id = Column(UUID, ForeignKey('infrastructure_projects.id'))
    message = Column(String)
    trigger_type = Column(String) # 'USER_ROUTE_PROXIMITY' | 'HIGHWAY_CORRIDOR_ALERT'
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
```

## 2. Trigger Logic & Geospatial Functions

When a new `InfrastructureProject` is created (or its status changes to ACTIVE), the backend dispatches a background task (e.g., via FastAPI `BackgroundTasks` or Celery) to perform two proximity checks using `ST_DWithin` (which checks if two geometries are within a specified distance, casting to geography for meters calculation natively).

### A. Subscribed Area/Route Check (2km Radius)
Find all subscriptions where the distance between the subscription geometry and the project point is <= 2000 meters.
```sql
SELECT user_id 
FROM user_subscriptions
WHERE ST_DWithin(
  geometry::geography, 
  :new_project_geom::geography, 
  2000 -- 2000 meters (2km)
);
```
**Action:** Generate personalized `Alert` records for the affected `user_id`s notifying them of works near their route/home.

### B. High Impact Highway Corridor Check (500m Radius)
Check if the project directly affects major UP transport arteries. We check against the `up_highway_corridors` table.
```sql
SELECT name 
FROM up_highway_corridors
WHERE ST_DWithin(
  geometry::geography, 
  :new_project_geom::geography, 
  500 -- 500 meters
);
```
**Action:** If a match is found (e.g., "Shaheed Path Lucknow"), automatically tag the project with an internal metadata flag: `High Impact Highway Alert: {corridor_name}`. This triggers a global push notification to authorities (NHAI/PWD_UP) and flags it distinctly with high priority on the government dashboard.

## 3. API Shape

### Subscription Endpoints
- `POST /alerts/subscriptions`: Create a new user commute route or watchlist area.
  - **Body Format:** `{ name: "Kanpur-Lucknow Commute", geojson: { type: "LineString", coordinates: [...] } }`
- `GET /alerts/subscriptions`: List user's active tracked zones.
- `DELETE /alerts/subscriptions/{id}`: Unsubscribe from an area.

### Alerts Endpoints
- `GET /alerts`: Fetch personalized alerts generated for the user's subscriptions.
  - **Response:** `[ { id: "...", message: "New Road Expansion on NH-27 within 2km of your commute", is_read: false } ]`
- `PUT /alerts/{id}/read`: Mark alert as seen.

### Admin/System Endpoints
- `POST /admin/corridors`: Seed `up_highway_corridors` with the official LineStrings for NH-27, NH-19, NH-330, Agra-Lucknow Expressway, Purvanchal Expressway, and Shaheed Path.
