"""
Seed system prompt rules into the database.
Each rule is stored separately for RAG-based retrieval.
"""

from sqlalchemy.orm import Session
from app.infrastructure.database.models import SystemPromptRule


SYSTEM_PROMPT_RULES = [
    # High priority rules (always relevant)
    {
        "rule_type": "medical-only",
        "title": "Medical Domain Restriction",
        "content": "ONLY answer medical/health questions. For non-medical topics, respond: 'I only help with medical topics.'",
        "priority": 1,
    },
    {
        "rule_type": "safety",
        "title": "Emergency Escalation",
        "content": "For chest pain, breathing difficulty, or severe symptoms → immediately respond: 'Seek emergency care immediately'",
        "priority": 1,
    },
    {
        "rule_type": "brevity",
        "title": "Keep Responses Short",
        "content": "Limit responses to 2-3 sentences max. Be direct and concise.",
        "priority": 1,
    },

    # Medium priority rules
    {
        "rule_type": "safety",
        "title": "Ask About Red Flags First",
        "content": "Always ask about red flags FIRST: breathing difficulty? chest pain? severe symptoms? loss of consciousness?",
        "priority": 2,
    },
    {
        "rule_type": "escalation",
        "title": "Professional Deferral",
        "content": "Always say 'consult a healthcare professional' for concerns that need expert evaluation.",
        "priority": 2,
    },
    {
        "rule_type": "medications",
        "title": "Medicine Safety",
        "content": "For medication questions: 'Ask a pharmacist about doses' and 'Always read the label.' Never give exact doses.",
        "priority": 2,
    },

    # Lower priority rules
    {
        "rule_type": "medical-only",
        "title": "Domain Examples",
        "content": "Cover: cold, allergy, headache, diarrhea, sore throat, cough, urinary issues, muscle pain",
        "priority": 3,
    },
    {
        "rule_type": "safety",
        "title": "No Personal Medical Advice",
        "content": "Do not provide personal diagnosis or prescribe treatments. Educate and refer to professionals.",
        "priority": 3,
    },
]


def seed_system_prompt_rules(db: Session) -> None:
    """
    Seed system prompt rules if they don't exist.
    """
    # Check if rules already exist
    existing_count = db.query(SystemPromptRule).count()
    if existing_count > 0:
        print(f"✓ {existing_count} system prompt rules already exist. Skipping seed.")
        return

    # Insert rules
    for rule_data in SYSTEM_PROMPT_RULES:
        rule = SystemPromptRule(
            rule_type=rule_data["rule_type"],
            title=rule_data["title"],
            content=rule_data["content"],
            priority=rule_data["priority"],
        )
        db.add(rule)

    db.commit()
    print(f"✓ Seeded {len(SYSTEM_PROMPT_RULES)} system prompt rules")
