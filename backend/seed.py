"""
Seed script — populates the database with 15 realistic Lucknow infrastructure
projects so the frontend has real data to display.

Usage:
    cd backend
    python -m seed          # (requires DATABASE_URL env var or defaults to localhost)
"""
import os, sys, uuid
from datetime import datetime, timedelta

# Allow running as `python -m seed` from the backend directory
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models import (
    InfrastructureProject, AuthorityEnum, ProjectTypeEnum,
    StatusEnum, ImpactEnum,
)
from sqlalchemy import func, text

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

PROJECTS = [
    {
        "title": "Shaheed Path Six-Lane Widening",
        "description": "Widening Shaheed Path from 4 to 6 lanes between Gomti Nagar Extension and Mohan Road. Includes central median, drainage, and new streetlights.",
        "permit_type": ProjectTypeEnum.ROAD,
        "project_authority": AuthorityEnum.LDA,
        "contractor": "Larsen & Toubro Ltd.",
        "district": "Lucknow",
        "division": "Lucknow Division",
        "lng": 81.0050, "lat": 26.8350,
        "budget": 185.0,
        "status": StatusEnum.ACTIVE,
        "impact_level": ImpactEnum.HIGH,
        "completion_percent": 42,
        "start_date": datetime(2025, 6, 1),
        "end_date": datetime(2027, 3, 31),
    },
    {
        "title": "Gomti Nagar Sewerage Upgrade",
        "description": "Complete overhaul of the underground sewerage network in Gomti Nagar sectors 1-12, including new treatment plant connection.",
        "permit_type": ProjectTypeEnum.UTILITY,
        "project_authority": AuthorityEnum.JAL_NIGAM,
        "contractor": "SPML Infra Ltd.",
        "district": "Lucknow",
        "division": "Lucknow Division",
        "lng": 80.9960, "lat": 26.8560,
        "budget": 92.0,
        "status": StatusEnum.ACTIVE,
        "impact_level": ImpactEnum.MEDIUM,
        "completion_percent": 68,
        "start_date": datetime(2025, 1, 15),
        "end_date": datetime(2026, 8, 30),
    },
    {
        "title": "Hazratganj Heritage Walk Renovation",
        "description": "Pedestrianisation and heritage restoration of Hazratganj main street: cobblestone pavement, LED heritage lamps, benches.",
        "permit_type": ProjectTypeEnum.CONSTRUCTION,
        "project_authority": AuthorityEnum.SMART_CITY,
        "contractor": "Shapoorji Pallonji & Co.",
        "district": "Lucknow",
        "division": "Lucknow Division",
        "lng": 80.9505, "lat": 26.8540,
        "budget": 65.0,
        "status": StatusEnum.ACTIVE,
        "impact_level": ImpactEnum.MEDIUM,
        "completion_percent": 85,
        "start_date": datetime(2025, 3, 1),
        "end_date": datetime(2026, 6, 30),
    },
    {
        "title": "Lucknow Metro Phase-2 Extension (Airport Line)",
        "description": "12.5 km elevated metro corridor from Charbagh to Amausi Airport with 11 stations.",
        "permit_type": ProjectTypeEnum.CONSTRUCTION,
        "project_authority": AuthorityEnum.UPLCL,
        "contractor": "Tata Projects Ltd.",
        "district": "Lucknow",
        "division": "Lucknow Division",
        "lng": 80.8840, "lat": 26.8465,
        "budget": 4500.0,
        "status": StatusEnum.ACTIVE,
        "impact_level": ImpactEnum.HIGH,
        "completion_percent": 23,
        "start_date": datetime(2025, 9, 1),
        "end_date": datetime(2029, 12, 31),
    },
    {
        "title": "Indira Nagar Water Pipeline Replacement",
        "description": "Replacing 40-year-old cast iron mains with HDPE pipes across Indira Nagar A-F sectors.",
        "permit_type": ProjectTypeEnum.UTILITY,
        "project_authority": AuthorityEnum.JAL_NIGAM,
        "contractor": "Welspun Corp.",
        "district": "Lucknow",
        "division": "Lucknow Division",
        "lng": 80.9820, "lat": 26.8730,
        "budget": 38.0,
        "status": StatusEnum.PENDING,
        "impact_level": ImpactEnum.LOW,
        "completion_percent": 12,
        "start_date": datetime(2026, 1, 10),
        "end_date": datetime(2026, 11, 30),
    },
    {
        "title": "Alambagh Flyover Reconstruction",
        "description": "Demolition and reconstruction of the deteriorating Alambagh overpass; new 4-lane design with service roads.",
        "permit_type": ProjectTypeEnum.ROAD,
        "project_authority": AuthorityEnum.PWD_UP,
        "contractor": "Dilip Buildcon Ltd.",
        "district": "Lucknow",
        "division": "Lucknow Division",
        "lng": 80.9115, "lat": 26.8180,
        "budget": 220.0,
        "status": StatusEnum.ACTIVE,
        "impact_level": ImpactEnum.HIGH,
        "completion_percent": 55,
        "start_date": datetime(2025, 4, 15),
        "end_date": datetime(2027, 1, 31),
    },
    {
        "title": "Vikas Nagar Community Park & Sports Complex",
        "description": "Construction of a 5-acre park with jogging track, synthetic cricket pitch, basketball court, and children's play area.",
        "permit_type": ProjectTypeEnum.CONSTRUCTION,
        "project_authority": AuthorityEnum.LMC,
        "contractor": "NCC Ltd.",
        "district": "Lucknow",
        "division": "Lucknow Division",
        "lng": 80.9240, "lat": 26.8620,
        "budget": 28.0,
        "status": StatusEnum.ACTIVE,
        "impact_level": ImpactEnum.LOW,
        "completion_percent": 91,
        "start_date": datetime(2025, 7, 1),
        "end_date": datetime(2026, 4, 30),
    },
    {
        "title": "Ring Road NH-230 Capacity Enhancement",
        "description": "Expansion of Lucknow Ring Road from 4 to 8 lanes with grade-separated interchanges at Sitapur Road and Faizabad Road junctions.",
        "permit_type": ProjectTypeEnum.ROAD,
        "project_authority": AuthorityEnum.NHAI,
        "contractor": "IRB Infrastructure Developers",
        "district": "Lucknow",
        "division": "Lucknow Division",
        "lng": 80.8695, "lat": 26.8900,
        "budget": 780.0,
        "status": StatusEnum.ACTIVE,
        "impact_level": ImpactEnum.HIGH,
        "completion_percent": 35,
        "start_date": datetime(2025, 11, 1),
        "end_date": datetime(2028, 6, 30),
    },
    {
        "title": "Chinhat Industrial Area Power Substation",
        "description": "New 220/33 kV substation to serve the Chinhat industrial corridor and reduce load-shedding in eastern Lucknow.",
        "permit_type": ProjectTypeEnum.UTILITY,
        "project_authority": AuthorityEnum.UPLCL,
        "contractor": "Siemens India Ltd.",
        "district": "Lucknow",
        "division": "Lucknow Division",
        "lng": 81.0310, "lat": 26.8700,
        "budget": 45.0,
        "status": StatusEnum.PENDING,
        "impact_level": ImpactEnum.MEDIUM,
        "completion_percent": 5,
        "start_date": datetime(2026, 3, 1),
        "end_date": datetime(2027, 2, 28),
    },
    {
        "title": "Mahanagar Storm Drain Modernisation",
        "description": "Upgrading the open-channel storm drains in Mahanagar to enclosed RCC box drains with outfall to the Gomti.",
        "permit_type": ProjectTypeEnum.UTILITY,
        "project_authority": AuthorityEnum.LMC,
        "contractor": "HCC Ltd.",
        "district": "Lucknow",
        "division": "Lucknow Division",
        "lng": 80.9380, "lat": 26.8680,
        "budget": 55.0,
        "status": StatusEnum.ACTIVE,
        "impact_level": ImpactEnum.MEDIUM,
        "completion_percent": 47,
        "start_date": datetime(2025, 8, 15),
        "end_date": datetime(2026, 12, 31),
    },
    {
        "title": "Kanpur Expressway Missing Link (Lucknow Spur)",
        "description": "14 km greenfield access-controlled expressway connecting Lucknow outer ring road to the Agra-Lucknow Expressway.",
        "permit_type": ProjectTypeEnum.ROAD,
        "project_authority": AuthorityEnum.UPSIDA,
        "contractor": "Apco Infratech Pvt. Ltd.",
        "district": "Lucknow",
        "division": "Lucknow Division",
        "lng": 80.8150, "lat": 26.7900,
        "budget": 1200.0,
        "status": StatusEnum.ACTIVE,
        "impact_level": ImpactEnum.HIGH,
        "completion_percent": 18,
        "start_date": datetime(2025, 12, 1),
        "end_date": datetime(2028, 11, 30),
    },
    {
        "title": "Amausi Airport Terminal Expansion",
        "description": "New integrated terminal building with expanded domestic and international concourses.",
        "permit_type": ProjectTypeEnum.CONSTRUCTION,
        "project_authority": AuthorityEnum.PWD_UP,
        "contractor": "Tata Projects Ltd.",
        "district": "Lucknow",
        "division": "Lucknow Division",
        "lng": 80.8830, "lat": 26.7605,
        "budget": 3200.0,
        "status": StatusEnum.ACTIVE,
        "impact_level": ImpactEnum.HIGH,
        "completion_percent": 10,
        "start_date": datetime(2026, 1, 1),
        "end_date": datetime(2029, 6, 30),
    },
    # -- Projects outside Lucknow for wider coverage --
    {
        "title": "Kanpur Outer Ring Road Phase-1",
        "description": "48 km ring road around Kanpur city with 6 interchanges.",
        "permit_type": ProjectTypeEnum.ROAD,
        "project_authority": AuthorityEnum.NHAI,
        "contractor": "Dilip Buildcon Ltd.",
        "district": "Kanpur",
        "division": "Kanpur Division",
        "lng": 80.3319, "lat": 26.4499,
        "budget": 950.0,
        "status": StatusEnum.ACTIVE,
        "impact_level": ImpactEnum.HIGH,
        "completion_percent": 30,
        "start_date": datetime(2025, 5, 1),
        "end_date": datetime(2028, 3, 31),
    },
    {
        "title": "Varanasi Kashi Vishwanath Corridor Phase-II",
        "description": "Extension of the Kashi Vishwanath Corridor with heritage walk, ghats restoration, and public amenities.",
        "permit_type": ProjectTypeEnum.CONSTRUCTION,
        "project_authority": AuthorityEnum.SMART_CITY,
        "contractor": "Shapoorji Pallonji & Co.",
        "district": "Varanasi",
        "division": "Varanasi Division",
        "lng": 83.0065, "lat": 25.3109,
        "budget": 320.0,
        "status": StatusEnum.ACTIVE,
        "impact_level": ImpactEnum.HIGH,
        "completion_percent": 62,
        "start_date": datetime(2025, 2, 1),
        "end_date": datetime(2027, 6, 30),
    },
    {
        "title": "Agra-Lucknow Expressway Service Road",
        "description": "Service road construction along the 302 km expressway for local traffic access.",
        "permit_type": ProjectTypeEnum.ROAD,
        "project_authority": AuthorityEnum.NHAI,
        "contractor": "IRB Infrastructure Developers",
        "district": "Agra",
        "division": "Agra Division",
        "lng": 78.0081, "lat": 27.1767,
        "budget": 450.0,
        "status": StatusEnum.PENDING,
        "impact_level": ImpactEnum.MEDIUM,
        "completion_percent": 0,
        "start_date": datetime(2026, 6, 1),
        "end_date": datetime(2028, 12, 31),
    },
]


def main():
    db = SessionLocal()
    try:
        inserted = 0
        for proj in PROJECTS:
            # Check for existing project with same title to avoid duplicates on re-run
            existing = db.query(InfrastructureProject).filter(
                InfrastructureProject.title == proj["title"]
            ).first()
            if existing:
                print(f"  ⏭  Already exists: {proj['title']}")
                continue

            geom = func.ST_GeomFromText(f"POINT({proj['lng']} {proj['lat']})", 4326)
            db_project = InfrastructureProject(
                title=proj["title"],
                description=proj["description"],
                permit_type=proj["permit_type"],
                project_authority=proj["project_authority"],
                contractor=proj["contractor"],
                district=proj["district"],
                division=proj["division"],
                geometry=geom,
                budget=proj["budget"],
                status=proj["status"],
                impact_level=proj["impact_level"],
                completion_percent=proj["completion_percent"],
                start_date=proj["start_date"],
                end_date=proj["end_date"],
                is_verified=True,
            )
            db.add(db_project)
            inserted += 1
            print(f"  ✅  Inserted: {proj['title']}")

        db.commit()
        print(f"\n🎉 Seeded {inserted} projects successfully.")
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
