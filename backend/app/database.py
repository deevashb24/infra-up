from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# FIX #10: Expose a psycopg2-safe URL for the raw LISTEN/NOTIFY connection.
# Strips any async driver prefix (e.g. postgresql+asyncpg://) so psycopg2.connect()
# never receives an incompatible URL.
SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

def _make_psycopg2_url(url: str) -> str:
    """Normalise any SQLAlchemy async-driver URL to a plain psycopg2-compatible one."""
    for prefix in ("postgresql+asyncpg://", "postgres+asyncpg://"):
        if url.startswith(prefix):
            return "postgresql://" + url[len(prefix):]
    # Also handle 'postgres://' shorthand (e.g. Heroku / Railway)
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url

RAW_DATABASE_URL = _make_psycopg2_url(SQLALCHEMY_DATABASE_URL)

engine = create_engine(RAW_DATABASE_URL)
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
