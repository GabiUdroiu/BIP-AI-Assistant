import re
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "knowledge"


class RagService:
    """Minimal retrieval over local .md files. Keyword-overlap scoring —
    no embedding model needed for a knowledge base this small."""

    def __init__(self, knowledge_dir: Path = KNOWLEDGE_DIR) -> None:
        self._chunks: list[str] = []
        self._load(knowledge_dir)

    def _load(self, knowledge_dir: Path) -> None:
        if not knowledge_dir.exists():
            return
        for path in knowledge_dir.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for paragraph in text.split("\n\n"):
                paragraph = paragraph.strip()
                if paragraph:
                    self._chunks.append(paragraph)
        print(f"✓ RAG loaded {len(self._chunks)} chunk(s) from {knowledge_dir}")

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        query_words = set(re.findall(r"\w+", query.lower()))
        scored = []
        for chunk in self._chunks:
            chunk_words = set(re.findall(r"\w+", chunk.lower()))
            overlap = len(query_words & chunk_words)
            if overlap > 0:
                scored.append((overlap, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]
