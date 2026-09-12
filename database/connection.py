import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from config.settings import settings

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = settings.DATABASE_URL

# Connect args needed for SQLite to avoid thread conflicts
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        DATABASE_URL, 
        connect_args=connect_args,
        echo=False
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    logger.info(f"Database connection initialized successfully for engine: {DATABASE_URL.split('://')[0]}")
except Exception as e:
    logger.error(f"Failed to initialize database engine: {str(e)}", exc_info=True)
    raise e

def get_db():
    """
    FastAPI dependency that provides a transactional database session context.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
