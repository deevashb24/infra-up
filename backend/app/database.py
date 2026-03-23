from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database connection
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/civic_tech")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_trigger(target, connection, **kw):
    # Phase 4: Create PostgreSQL Trigger for LISTEN/NOTIFY execution
    connection.execute(text("""
    CREATE OR REPLACE FUNCTION notify_new_project() RETURNS TRIGGER AS $$
    DECLARE
        payload JSON;
    BEGIN
        payload = json_build_object(
            'id', NEW.id,
            'title', NEW.title,
            'permit_type', NEW.permit_type,
            'district', NEW.district
        );
        PERFORM pg_notify('new_up_alert', payload::text);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """))
    connection.execute(text("""
    DROP TRIGGER IF EXISTS project_notify_trigger ON infrastructure_projects;
    CREATE TRIGGER project_notify_trigger
    AFTER INSERT ON infrastructure_projects
    FOR EACH ROW EXECUTE PROCEDURE notify_new_project();
    """))

# Attach trigger creation to table creation globally
event.listen(Base.metadata, 'after_create', create_trigger)
