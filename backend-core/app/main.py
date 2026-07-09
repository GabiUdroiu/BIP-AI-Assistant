import sys
from contextlib import asynccontextmanager

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.api.v1.routes import voice, chat, streaming, admin
from app.presentation.error_handler import register_error_handlers
from app.core.config import get_settings
from app.core.logging import logger
from app.infrastructure.database.models import Base
from app.infrastructure.database.session import get_engine
from app.seeds.populate_medical_scenarios import seed_medical_scenarios, seed_system_prompt
from app.seeds.populate_system_prompt_rules import seed_system_prompt_rules

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    try:
        if settings.database_url:
            engine = get_engine()

            # Create all tables
            Base.metadata.create_all(bind=engine)
            logger.info("✓ Database tables ready")

            # Auto-seed medical scenarios, system prompt, and prompt rules
            try:
                seed_medical_scenarios(engine)
                seed_system_prompt(engine)
                from app.infrastructure.database.session import SessionLocal
                db = SessionLocal()
                seed_system_prompt_rules(db)
                db.close()
                logger.info("✓ Medical knowledge base ready")
            except Exception as e:
                logger.warning(f"Medical seeding info: {e}")
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
    allow_origins=["*"],  # Temporarily allow all for debugging
    allow_credentials=False,  # Can't use True with "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register centralized error handlers
register_error_handlers(app)

# ============ Debug Endpoint ============
@app.get("/health")
async def health_check():
    """Health check endpoint for CORS testing."""
    return {"status": "ok", "message": "Backend is running!"}


# ============ Presentation Layer v1 Routes ============
app.include_router(voice.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(streaming.router)
