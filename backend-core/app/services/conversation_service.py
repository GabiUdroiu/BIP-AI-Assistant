from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models import Message


class ConversationService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save_message(self, session_id: str, role: str, content: str) -> None:
        self._db.add(Message(session_id=session_id, role=role, content=content))
        self._db.commit()

    def get_history(self, session_id: str, limit: int = 50) -> list[dict]:
        stmt = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = self._db.execute(stmt).scalars().all()
        return [{"role": m.role, "content": m.content} for m in reversed(messages)]
