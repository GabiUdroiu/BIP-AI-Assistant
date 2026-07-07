import sys

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, voice
from app.core.config import get_settings
from app.db.models import Base
from app.db.session import get_engine

settings = get_settings()

app = FastAPI(title="Voice Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.on_event("startup")
def create_tables():
    if settings.database_url:
        Base.metadata.create_all(bind=get_engine())
        print("✓ Database tables ready")
    else:
        print("⚠ No DATABASE_URL configured - chat memory will not persist")
