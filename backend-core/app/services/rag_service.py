import re

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.services.embedding_service import EmbeddingService

# cosine distance (0 = identical, 2 = opposite); rows farther than this from
# the query are treated as irrelevant rather than force-fit into context.
MAX_DISTANCE = 0.8

DB_QUERIES = [
    (
        "SELECT title, content, embedding <=> (:vec)::vector AS distance FROM knowledge_chunks "
        "ORDER BY distance LIMIT :k",
        lambda row: f"{row.title}: {row.content}",
    ),
    (
        "SELECT name, description, severity_level, embedding <=> (:vec)::vector AS distance "
        "FROM symptom_reference ORDER BY distance LIMIT :k",
        lambda row: f"Symptom - {row.name} (severity: {row.severity_level}): {row.description}",
    ),
    (
        "SELECT name, general_usage_info, general_precautions, "
        "embedding <=> (:vec)::vector AS distance FROM medical_information_entries "
        "ORDER BY distance LIMIT :k",
        lambda row: f"{row.name}: {row.general_usage_info} Precautions: {row.general_precautions}",
    ),
]


class RagService:
    """Retrieval over the knowledge tables in Postgres (pgvector cosine
    similarity, via OpenRouter embeddings). Falls back to DB keyword-overlap
    if no embedding service is configured or a query embedding call fails."""

    def __init__(self, engine: Engine | None = None, embedding_service: EmbeddingService | None = None) -> None:
        self._engine = engine
        self._embedding_service = embedding_service

    def _keyword_search(self, candidates: list[str], query: str, top_k: int) -> list[str]:
        query_words = {w for w in re.findall(r"\w+", query.lower()) if len(w) > 2}
        scored = []
        for chunk in candidates:
            chunk_words = set(re.findall(r"\w+", chunk.lower()))
            overlap = len(query_words & chunk_words)
            if overlap > 0:
                scored.append((overlap, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]

    def _load_db_chunks(self) -> list[str]:
        if self._engine is None:
            return []
        chunks: list[str] = []
        try:
            with self._engine.connect() as conn:
                rows = conn.execute(text("SELECT title, content FROM knowledge_chunks"))
                for title, content in rows:
                    chunks.append(f"{title}: {content}")

                rows = conn.execute(text("SELECT name, description, severity_level FROM symptom_reference"))
                for name, description, severity in rows:
                    chunks.append(f"Symptom - {name} (severity: {severity}): {description}")

                rows = conn.execute(
                    text(
                        "SELECT name, general_usage_info, general_precautions "
                        "FROM medical_information_entries"
                    )
                )
                for name, usage_info, precautions in rows:
                    chunks.append(f"{name}: {usage_info} Precautions: {precautions}")
        except Exception as exc:
            print(f"⚠ RAG could not load DB chunks: {exc}")
        return chunks

    def _vector_search(self, query: str, top_k: int) -> list[str]:
        try:
            query_vec = self._embedding_service.embed(query)
        except Exception as exc:
            print(f"⚠ RAG embedding call failed, falling back to keyword search: {exc}")
            return self._keyword_search(self._load_db_chunks(), query, top_k)

        vec_literal = "[" + ",".join(str(x) for x in query_vec) + "]"
        scored: list[tuple[float, str]] = []
        try:
            with self._engine.connect() as conn:
                for sql, formatter in DB_QUERIES:
                    rows = conn.execute(text(sql), {"vec": vec_literal, "k": top_k})
                    for row in rows:
                        if row.distance <= MAX_DISTANCE:
                            scored.append((row.distance, formatter(row)))
        except Exception as exc:
            print(f"⚠ RAG vector search failed, falling back to keyword search: {exc}")
            return self._keyword_search(self._load_db_chunks(), query, top_k)
        scored.sort(key=lambda item: item[0])
        result = [chunk for _, chunk in scored[:top_k]]
        if result:
            print(f"🔎 RAG matched for '{query}':")
            for distance, chunk in scored[:top_k]:
                print(f"   [{distance:.3f}] {chunk[:100]}")
        else:
            print(f"🔎 RAG found no match above the relevance threshold for '{query}'")
        return result

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        if self._embedding_service is not None and self._engine is not None:
            return self._vector_search(query, top_k)
        return self._keyword_search(self._load_db_chunks(), query, top_k)
