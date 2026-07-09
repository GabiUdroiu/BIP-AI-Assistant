# Medical Database Setup Guide

This guide walks you through populating your Neon database with medical scenarios and system prompts.

## What Gets Added

✅ **Medical Scenarios** (10 scenarios, all vectorially searchable)
- Mild Cold
- Allergy
- Mild Headache
- Diarrhea
- Sore Throat
- Cough
- Urinary Tract Symptoms
- Post-Exercise Muscle Pain
- Medicine Safety Questions
- Chest Pain (Emergency)

✅ **System Prompt** - Comprehensive medical education prompt that:
- Limits bot to medical domain only
- Includes safety-first protocols
- Teaches medical students systematically
- Prevents off-topic questions
- Enforces emergency escalation

## Prerequisites

1. **Database URL Set**: Make sure `DATABASE_URL` is set in your `.env` file
   ```
   DATABASE_URL=postgresql://user:password@host/dbname
   ```

2. **Dependencies Installed**:
   ```bash
   cd backend-core
   pip install -r requirements.txt
   ```

## Setup Steps

### Option 1: Run Python Script Directly

```bash
cd backend-core
python -m app.seeds.populate_medical_scenarios
```

**Output:**
```
🏥 Medical Database Seeding Script
==================================================

1️⃣  Initializing database...
✅ Database connection successful

2️⃣  Populating medical scenarios...
  ✓ Added: Mild Cold
  ✓ Added: Allergy
  [... 8 more scenarios ...]
✅ Successfully added 10 medical scenarios

3️⃣  Setting up system prompt...
✅ Successfully added and activated Medical Assistant system prompt

==================================================
✅ Database seeding complete!
```

### Option 2: Run from FastAPI Startup (Auto-seed)

Add this to your `app/main.py` startup:

```python
from app.seeds.populate_medical_scenarios import seed_medical_scenarios, seed_system_prompt

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        if settings.database_url:
            Base.metadata.create_all(bind=get_engine())
            logger.info("✓ Database tables ready")
            
            # Auto-seed medical data
            engine = get_engine()
            seed_medical_scenarios(engine)
            seed_system_prompt(engine)
    except Exception as exc:
        logger.error(f"Failed to initialize: {exc}", exc_info=True)
        raise
    
    yield
    # Shutdown...
```

## Verify Setup

Check that data is in your database:

```bash
# Connect to your Neon database
psql $DATABASE_URL

# List medical scenarios
SELECT scenario_name, category FROM medical_scenarios;

# Check active system prompt
SELECT name, active FROM system_prompts WHERE active = true;
```

## How RAG Makes It Searchable

The medical scenarios are **vectorially searchable** through your RAG (Retrieval-Augmented Generation) system:

1. **When user sends a message**, the RAG system:
   - Converts message to embedding vector
   - Searches `medical_scenarios` table for similar scenarios
   - Retrieves relevant scenarios as context
   - Passes context to LLM for better responses

2. **Example flow:**
   ```
   User: "My throat hurts"
   ↓
   RAG Search: "sore throat" matches "Sore Throat" scenario
   ↓
   Context Injected: "Relevant facts: Patient with throat pain... 
                     can swallow fluids, mild fever..."
   ↓
   LLM Response: Uses scenario knowledge + system prompt
   ```

3. **Embedding Storage:**
   - Each scenario's content is embedded via OpenRouter
   - Embeddings stored in your RAG cache
   - Enables semantic search (similar meaning, not exact match)

## System Prompt Behavior

Once active, the system prompt ensures:

✅ **Medical Domain Only**: "I only help with medical topics"
✅ **Safety First**: Emergency symptoms → "Call 911"
✅ **Educational**: Teaches reasoning, not just answers
✅ **No Professional Diagnosis**: "I'm educational, not a doctor"
✅ **Transparent Limits**: "Always consult professionals"

### Example conversation with new system prompt:

```
User: Can you help with my homework on Python?
Bot: I'm specifically trained for medical education. I can only help 
     with medical topics, health conditions, and medical student 
     learning. Would you like to ask about a medical scenario?

User: I have chest pain and can't breathe
Bot: Stop using this app. Call emergency services immediately. 
     Do not wait. Do not drive yourself.

User: I have a mild sore throat
Bot: I'm sorry you feel unwell. Let me check safety first.
     Can you breathe easily? [Continues assessment following protocol]
```

## Troubleshooting

### "DATABASE_URL not configured"
- Check `.env` file has `DATABASE_URL`
- Restart terminal to load env vars

### "Table does not exist"
- Database tables haven't been created
- Ensure `Base.metadata.create_all()` runs first
- Check database connection

### "Scenarios already exist"
- If you run the script twice, it skips adding duplicates
- To re-seed, manually delete from `medical_scenarios` table:
  ```sql
  DELETE FROM medical_scenarios;
  ```

### RAG not retrieving scenarios
- Check embedding service is configured (OpenRouter API key)
- Verify scenarios are in database
- Check RAG service is initialized in your endpoints

## Next Steps

1. **Run the seed script** to populate your database
2. **Test in Postman**: Send a medical question to `/api/chat`
3. **Verify RAG**: Check that scenarios appear in `system_prompt` context
4. **Monitor logs**: Watch for safety protocol enforcement

## Files Added

- `app/db/models.py` - Updated with `MedicalScenario` model
- `app/seeds/__init__.py` - Seeding package
- `app/seeds/medical_system_prompt.py` - Comprehensive medical prompt
- `app/seeds/populate_medical_scenarios.py` - Seeding script

## System Prompt Content

The system prompt (100+ lines) includes:

- Core safety rules
- Domain restrictions
- Emergency protocols
- 10 detailed scenario walkthroughs
- Medical student teaching points
- Tone and language guidelines
- Constraints and what NOT to do

See `app/seeds/medical_system_prompt.py` for full content.

---

**Questions?** Check the scenario implementations in `populate_medical_scenarios.py` or the prompt guidelines in `medical_system_prompt.py`.
