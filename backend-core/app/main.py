import sys
from contextlib import asynccontextmanager

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin, chat, voice, streaming
from app.core.config import get_settings
from app.core.logging import logger
from app.db.models import Base
from app.db.session import get_engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    try:
        if settings.database_url:
            Base.metadata.create_all(bind=get_engine())
            logger.info("✓ Database tables ready")
        else:
            logger.warning("No DATABASE_URL configured - chat memory will not persist")
    except Exception as exc:
        logger.error(f"Failed to initialize database: {exc}", exc_info=True)
        raise

    yield

    # Shutdown - cleanup if needed
    logger.info("✓ Application shutdown")


app = FastAPI(title="Voice Chat API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
# WebSocket endpoints (no /api prefix, they handle their own routes)
app.include_router(streaming.router)
