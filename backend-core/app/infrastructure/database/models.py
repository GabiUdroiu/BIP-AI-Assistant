"""
SQLAlchemy ORM models.
Database schema definitions for the application.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Index, String, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Message(Base):
    """
    Chat message entity.
    Represents a message in a conversation.
    """
    __tablename__ = "robot_messages"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="Unique message identifier"
    )
    session_id: Mapped[str] = mapped_column(
        String,
        index=True,
        doc="Session ID for grouping messages"
    )
    role: Mapped[str] = mapped_column(
        String,
        doc="Message role: 'user' or 'assistant'"
    )
    content: Mapped[str] = mapped_column(
        Text,
        doc="Message content/text"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        doc="Message creation timestamp"
    )


class SystemPrompt(Base):
    """
    System prompt entity.
    Stores system prompts with versioning and activation.
    """
    __tablename__ = "system_prompts"
    __table_args__ = (
        Index(
            "ix_system_prompts_one_active",
            "active",
            unique=True,
            postgresql_where=text("active")
        ),
    )

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="Unique prompt identifier"
    )
    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        doc="Unique prompt name"
    )
    content: Mapped[str] = mapped_column(
        Text,
        doc="Prompt content/template"
    )
    active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Whether this prompt is currently active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        doc="Prompt creation timestamp"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        doc="Last update timestamp"
    )


class MedicalScenario(Base):
    """
    Medical scenario entity.
    Stores medical scenario information for RAG retrieval.
    """
    __tablename__ = "medical_scenarios"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="Unique scenario identifier"
    )
    scenario_name: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        doc="Unique scenario name"
    )
    description: Mapped[str] = mapped_column(
        Text,
        doc="Scenario description"
    )
    symptoms: Mapped[str] = mapped_column(
        Text,
        doc="Symptoms associated with scenario"
    )
    safety_checks: Mapped[str] = mapped_column(
        Text,
        doc="Safety checks to perform"
    )
    guidance: Mapped[str] = mapped_column(
        Text,
        doc="Medical guidance for scenario"
    )
    medications: Mapped[str] = mapped_column(
        Text,
        doc="Suggested medications/treatments"
    )
    emergency_signs: Mapped[str] = mapped_column(
        Text,
        doc="Signs requiring emergency care"
    )
    category: Mapped[str] = mapped_column(
        String,
        index=True,
        doc="Scenario category"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        doc="Creation timestamp"
    )
