from sqlalchemy import text
from sqlalchemy.engine import Engine

DEFAULT_PROMPT = (
    "You are a helpful voice assistant.\n"
    "Rules:\n"
    "- Keep replies short (1-2 sentences), since they get spoken aloud via text-to-speech.\n"
    "- Use the facts provided below when relevant.\n"
    "- Be direct and casual, no markdown formatting in replies."
)


class PromptService:
    """Loads the active system prompt from the system_prompts table on every
    call, so edits made via the dashboard take effect on the next request
    with no restart. Falls back to a hardcoded default if the DB is
    unreachable or has no active row."""

    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine

    def get_system_prompt(self) -> str:
        if self._engine is not None:
            try:
                with self._engine.connect() as conn:
                    row = conn.execute(
                        text("SELECT content FROM system_prompts WHERE active = true LIMIT 1")
                    ).fetchone()
                    if row:
                        return row[0]
            except Exception as exc:
                print(f"⚠ Prompt service could not load from DB, using default: {exc}")
        return DEFAULT_PROMPT
