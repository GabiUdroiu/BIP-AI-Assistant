from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


class PromptService:
    def __init__(self, prompts_dir: Path = PROMPTS_DIR, name: str = "system_prompt.md") -> None:
        path = prompts_dir / name
        self._system_prompt = path.read_text(encoding="utf-8").strip() if path.exists() else ""

    def get_system_prompt(self) -> str:
        return self._system_prompt
