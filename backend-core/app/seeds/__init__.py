"""Database seeding utilities for populating initial data."""

from .populate_medical_scenarios import seed_medical_scenarios, seed_system_prompt

__all__ = ["seed_medical_scenarios", "seed_system_prompt"]
