from sqlalchemy import MetaData, Table, delete, insert, select, update
from sqlalchemy.engine import Engine

from app.services.embedding_service import EmbeddingService


class AdminService:
    """Generic reflection-based CRUD over any table in the connected database."""

    # Tables with embedding columns and the field to embed
    EMBEDDING_TABLES = {
        "knowledge_chunks": "content",
        "symptom_reference": "description",
        "medical_information_entries": "general_usage_info",
    }

    def __init__(self, engine: Engine, embedding_service: EmbeddingService | None = None) -> None:
        self._engine = engine
        self._embedding_service = embedding_service
        self._metadata = MetaData()
        self._metadata.reflect(bind=engine)

    def list_tables(self) -> list[str]:
        return sorted(self._metadata.tables.keys())

    def _get_table(self, table_name: str) -> Table:
        if table_name not in self._metadata.tables:
            raise ValueError(f"Table '{table_name}' not found")
        return self._metadata.tables[table_name]

    def get_columns(self, table_name: str) -> list[dict]:
        table = self._get_table(table_name)
        return [
            {
                "name": c.name,
                "type": str(c.type),
                "nullable": c.nullable,
                "primary_key": c.primary_key,
            }
            for c in table.columns
        ]

    def list_rows(self, table_name: str, limit: int = 50) -> list[dict]:
        table = self._get_table(table_name)
        stmt = select(table).limit(limit)

        if "created_at" in table.c:
            stmt = stmt.order_by(table.c.created_at.desc())
        else:
            pk_cols = [c for c in table.c if c.primary_key]
            if pk_cols:
                stmt = stmt.order_by(pk_cols[0].desc())

        with self._engine.connect() as conn:
            result = conn.execute(stmt)
            return [dict(row._mapping) for row in result]

    def insert_row(self, table_name: str, data: dict) -> dict:
        table = self._get_table(table_name)

        # Auto-generate embedding if table supports it
        if table_name in self.EMBEDDING_TABLES and self._embedding_service:
            text_field = self.EMBEDDING_TABLES[table_name]
            if "embedding" not in data and text_field in data:
                try:
                    embedding = self._embedding_service.embed(data[text_field])
                    data["embedding"] = embedding
                except Exception as e:
                    print(f"Warning: Could not generate embedding for {table_name}: {e}")

        with self._engine.begin() as conn:
            result = conn.execute(insert(table).values(**data).returning(table))
            row = result.fetchone()
            return dict(row._mapping) if row else {}

    def update_row(self, table_name: str, pk_column: str, pk_value: str, data: dict) -> dict:
        table = self._get_table(table_name)

        # Validate column name to prevent injection
        if pk_column not in [c.name for c in table.columns]:
            raise ValueError(f"Invalid column: {pk_column}")

        with self._engine.begin() as conn:
            result = conn.execute(
                update(table).where(table.c[pk_column] == pk_value).values(**data).returning(table)
            )
            row = result.fetchone()
            return dict(row._mapping) if row else {}

    def delete_row(self, table_name: str, pk_column: str, pk_value: str) -> None:
        table = self._get_table(table_name)

        # Validate column name to prevent injection
        if pk_column not in [c.name for c in table.columns]:
            raise ValueError(f"Invalid column: {pk_column}")

        with self._engine.begin() as conn:
            conn.execute(delete(table).where(table.c[pk_column] == pk_value))
