from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    port: int = 8080
    cors_origins: list[str] = [
        "*",  # Allow all origins (wildcard)
        # Local development
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://localhost:5173",
        "https://localhost:3000",
        # Ngrok tunneling
        "https://donut-cheek-silencer.ngrok-free.dev",
        "https://powdering-junction-verbally.ngrok-free.dev",
    ]

    whisper_model_size: str = "tiny.en"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    # openrouter_model: str = "liquid/lfm-2.5-1.2b-instruct:free"
    openrouter_model: str = "openai/gpt-oss-20b:free"
    embedding_model: str = "openai/text-embedding-3-small"
    embedding_dimensions: int = 768

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = "llama-3.1-8b-instant"

    default_chat_provider: str = "openrouter"

    database_url: str = Field(default="", alias="DATABASE_URL")


@lru_cache
def get_settings() -> Settings:
    return Settings()
