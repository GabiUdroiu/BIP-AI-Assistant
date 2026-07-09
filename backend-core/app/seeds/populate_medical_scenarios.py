"""
Seed script to populate medical scenarios into Neon database.
Makes all scenarios vectorially searchable via RAG.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infrastructure.database.models import Base, SystemPrompt, MedicalScenario
from app.core.config import get_settings
from app.seeds.medical_system_prompt import MEDICAL_SYSTEM_PROMPT


MEDICAL_SCENARIOS = [
    {
        "scenario_name": "Mild Cold",
        "description": "Patient with runny nose and sore throat",
        "symptoms": "Runny nose, sore throat, no fever, no breathing problems",
        "safety_checks": "Is it hard to breathe? Do you have a fever?",
        "guidance": "Rest, drink water, use saline nasal spray",
        "medications": "Paracetamol, Ibuprofen, Saline nasal spray",
        "emergency_signs": "Breathing becomes hard, chest pain, symptoms last >3 days",
        "category": "respiratory",
    },
    {
        "scenario_name": "Allergy",
        "description": "Patient with itchy eyes and sneezing",
        "symptoms": "Itchy eyes, sneezing frequently, no facial swelling, no breathing problems",
        "safety_checks": "Is your face, lips, or tongue swollen? Is it hard to breathe?",
        "guidance": "Identify allergen, avoid contact, antihistamines, eye drops",
        "medications": "Antihistamines, allergy eye drops, nasal spray",
        "emergency_signs": "Facial swelling, lip/tongue swelling, breathing difficulty, severe reaction",
        "category": "allergy",
    },
    {
        "scenario_name": "Mild Headache",
        "description": "Patient with mild headache",
        "symptoms": "Mild headache, not sudden, not severe, no injury, no weakness, no confusion",
        "safety_checks": "Did it start very suddenly? Is it very severe? Any head injury? Weakness? Confusion?",
        "guidance": "Drink water, rest in quiet room, take screen break, cool compress",
        "medications": "Paracetamol, Ibuprofen",
        "emergency_signs": "Sudden severe headache, confusion, weakness/numbness in face/arm/leg, trouble speaking, after injury",
        "category": "neurological",
    },
    {
        "scenario_name": "Diarrhoea",
        "description": "Patient with loose stools",
        "symptoms": "Diarrhea, no blood, no fever, can drink fluids",
        "safety_checks": "Any blood in stool? Do you have fever? Can you keep fluids down?",
        "guidance": "Drink small sips of water, oral rehydration solution, simple foods",
        "medications": "Oral rehydration solution, anti-diarrhea medicine (after pharmacist advice)",
        "emergency_signs": "Cannot keep fluids down, blood in stool, high fever, severe weakness/dizziness",
        "category": "gastrointestinal",
    },
    {
        "scenario_name": "Sore Throat",
        "description": "Patient with throat pain",
        "symptoms": "Sore throat, can swallow fluids, mild fever",
        "safety_checks": "Is it hard to breathe? Can you swallow? Do you have fever?",
        "guidance": "Rest, drink water, warm drinks, throat lozenges, pain relief",
        "medications": "Paracetamol, Ibuprofen, throat lozenges",
        "emergency_signs": "Breathing difficulty, cannot swallow fluids, severe pain, high fever",
        "category": "respiratory",
    },
    {
        "scenario_name": "Cough",
        "description": "Patient with persistent cough",
        "symptoms": "Cough, no chest pain, no breathing problems, no blood in sputum",
        "safety_checks": "Is it hard to breathe? Any chest pain? Coughing up blood?",
        "guidance": "Drink water, avoid smoke, honey in warm water, cough medicine after pharmacist advice",
        "medications": "Cough medicine (after pharmacist advice), Paracetamol/Ibuprofen if fever/pain",
        "emergency_signs": "Breathing becomes hard, coughing up blood, chest pain, cough lasts >3 weeks",
        "category": "respiratory",
    },
    {
        "scenario_name": "Urinary Tract Symptoms",
        "description": "Patient with burning during urination",
        "symptoms": "Burning when urinating, no fever, no back pain, not pregnant",
        "safety_checks": "Do you have fever? Pain in back or side? Are you pregnant? Blood in urine?",
        "guidance": "Drink water, pain relief (paracetamol), see doctor or pharmacist",
        "medications": "Paracetamol for pain, pharmacist/doctor advice for antibiotics",
        "emergency_signs": "Fever, back/side pain, blood in urine, severe weakness/confusion",
        "category": "urological",
    },
    {
        "scenario_name": "Post-Exercise Muscle Pain",
        "description": "Patient with muscle soreness after exercise",
        "symptoms": "Leg soreness, no injury, can walk, not severe pain",
        "safety_checks": "Any injury or fall? Can you walk? Is pain very severe?",
        "guidance": "Rest, hydration, gentle stretching, heat or cold therapy as feels good",
        "medications": "Paracetamol, Ibuprofen",
        "emergency_signs": "Pain worsens, cannot walk, severe swelling, numbness/weakness, discolored limb",
        "category": "musculoskeletal",
    },
    {
        "scenario_name": "Medicine Safety Question",
        "description": "Patient asking about medication dosage and safety",
        "symptoms": "Uncertain about medication safety, interactions, contraindications",
        "safety_checks": "Any existing conditions? Taking other medicines? Pregnant? Allergies?",
        "guidance": "Always read label, ask pharmacist, check for contraindications",
        "medications": "Varies by condition, never give exact doses, always defer to pharmacist",
        "emergency_signs": "Adverse reactions, overdose signs, allergic reaction",
        "category": "pharmacology",
    },
    {
        "scenario_name": "Chest Pain - EMERGENCY",
        "description": "Patient with chest pain and shortness of breath",
        "symptoms": "Chest pain, shortness of breath, may radiate to left arm",
        "safety_checks": "STOP - This is potentially life-threatening",
        "guidance": "CALL EMERGENCY SERVICES IMMEDIATELY. Do not wait. Do not drive yourself.",
        "medications": "None - emergency care only",
        "emergency_signs": "ANY chest pain with breathing difficulty is EMERGENCY",
        "category": "emergency",
    },
]


def init_db():
    """Initialize database connection and create tables."""
    settings = get_settings()
    if not settings.database_url:
        print("❌ DATABASE_URL not configured. Cannot seed database.")
        return False

    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    return engine


def seed_medical_scenarios(engine):
    """Populate medical scenarios into database."""
    with Session(engine) as session:
        # Check if scenarios already exist
        existing_count = session.query(MedicalScenario).count()
        if existing_count > 0:
            print(f"⚠️  Database already has {existing_count} scenarios. Skipping scenario population.")
            return

        print("📝 Adding medical scenarios to database...")
        for scenario in MEDICAL_SCENARIOS:
            db_scenario = MedicalScenario(**scenario)
            session.add(db_scenario)
            print(f"  ✓ Added: {scenario['scenario_name']}")

        session.commit()
        print(f"✅ Successfully added {len(MEDICAL_SCENARIOS)} medical scenarios")


def seed_system_prompt(engine):
    """Set the medical system prompt as active."""
    with Session(engine) as session:
        # Check if prompt already exists
        existing = session.query(SystemPrompt).filter_by(name="Medical Assistant").first()

        if existing:
            print("⚠️  Medical Assistant prompt already exists.")
            if not existing.active:
                print("  Activating existing prompt...")
                # Deactivate any other active prompts
                session.query(SystemPrompt).update({"active": False})
                existing.active = True
                session.commit()
                print("  ✓ Activated Medical Assistant prompt")
            return

        print("📝 Adding Medical Assistant system prompt...")
        prompt = SystemPrompt(
            name="Medical Assistant",
            content=MEDICAL_SYSTEM_PROMPT,
            active=True,
        )

        # Deactivate any other active prompts
        session.query(SystemPrompt).update({"active": False})
        session.add(prompt)
        session.commit()
        print("✅ Successfully added and activated Medical Assistant system prompt")


def main():
    """Main seeding function."""
    print("\n🏥 Medical Database Seeding Script")
    print("=" * 50)

    # Initialize database
    print("\n1️⃣  Initializing database...")
    engine = init_db()
    if not engine:
        return

    # Seed scenarios
    print("\n2️⃣  Populating medical scenarios...")
    seed_medical_scenarios(engine)

    # Seed system prompt
    print("\n3️⃣  Setting up system prompt...")
    seed_system_prompt(engine)

    print("\n" + "=" * 50)
    print("✅ Database seeding complete!")
    print("\n📌 Next steps:")
    print("   1. Scenarios are now in the database and vectorially searchable")
    print("   2. System prompt is active and will be used for all chat responses")
    print("   3. RAG system can retrieve relevant scenarios for user queries")
    print("   4. Bot will only answer medical questions and enforce safety protocols")


if __name__ == "__main__":
    main()
