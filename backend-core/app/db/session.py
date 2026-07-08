from functools import lru_cache
import os

from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.logging import logger


def _normalize_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


@lru_cache
def get_engine():
    """Create and configure the database engine with connection pooling."""
    settings = get_settings()

    if not settings.database_url:
        logger.warning("No DATABASE_URL configured - using in-memory SQLite for testing")
        return create_engine("sqlite:///:memory:", poolclass=NullPool)

    # Configuration from environment or defaults
    pool_size = int(os.getenv("DB_POOL_SIZE", 5))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", 10))
    pool_recycle = int(os.getenv("DB_POOL_RECYCLE", 3600))
    echo_sql = os.getenv("SQL_ECHO", "false").lower() == "true"

    logger.info(f"Database pool configuration: size={pool_size}, overflow={max_overflow}, recycle={pool_recycle}s")

    engine = create_engine(
        _normalize_url(settings.database_url),
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,  # Test connections before using
        pool_recycle=pool_recycle,  # Recycle connections after this many seconds
        echo=echo_sql,  # Log SQL statements if enabled
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Enable foreign keys for SQLite."""
        if "sqlite" in str(dbapi_conn):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


@lru_cache
def get_session_factory() -> sessionmaker:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_db() -> Session:
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
