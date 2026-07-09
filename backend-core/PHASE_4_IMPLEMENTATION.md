# Phase 4: Presentation Layer Implementation

## Overview

Phase 4 completes the Clean Architecture refactoring by implementing the Presentation Layer. All API routes now use application services instead of directly calling business logic, with centralized error handling and API schemas.

---

## Files Created

### 1. API Schemas (`app/presentation/api/v1/schemas.py`)

**Purpose:** Centralized request/response Pydantic models for input validation and response typing.

**Key Models:**
- `ApiResponse[T]` - Generic response wrapper
- `VoiceProcessRequest/Response` - Voice transcription
- `ChatRequest/Response` - Chat messages
- `ConversationHistoryResponse` - Conversation history
- `StreamVoiceResponse` - WebSocket messages
- `ErrorResponse`, `ValidationErrorResponse` - Error responses

**Benefits:**
- Single source of truth for API contracts
- Automatic request validation by FastAPI
- Type-safe response generation
- Better API documentation

### 2. Dependency Injection (`app/presentation/deps.py`)

**Purpose:** Factory functions that create and wire use cases and application services.

**Key Functions:**
- `get_process_voice_use_case()` - Voice transcription use case
- `get_chat_use_case(db)` - Chat with context use case
- `get_stream_voice_use_case(chat_use_case)` - Combined streaming use case
- `get_voice_service()` - Voice application service
- `get_chat_service()` - Chat application service
- `log_request_start/success/error()` - Request logging utilities

**Design:**
- Proper handling of request-scoped dependencies (database sessions)
- Stateless services (only `get_process_voice_use_case()` is cached)
- Clear dependency chains for maintainability

### 3. Centralized Error Handler (`app/presentation/error_handler.py`)

**Purpose:** Unified exception handling that converts domain exceptions to HTTP responses.

**Handled Exceptions:**
- `VoiceProcessingError` → HTTP 400
- `AudioProcessingError` → HTTP 400
- `ChatError` → HTTP 503
- `ContextRetrievalError` → HTTP 503
- `ConfigurationError` → HTTP 500
- `ExternalServiceError` → HTTP 503
- `DatabaseError` → HTTP 503
- `ConversationNotFoundError` → HTTP 404
- `RequestValidationError` → HTTP 422
- General `Exception` → HTTP 500

**Benefits:**
- Consistent error responses across all endpoints
- Proper HTTP status codes
- Error codes for client-side handling
- Automatic Pydantic validation error formatting

### 4. Voice Routes (`app/presentation/api/v1/routes/voice.py`)

**Endpoints:**
- `POST /api/voice/process` - Transcribe audio file

**Flow:**
1. Accept audio file from client
2. Inject `VoiceApplicationService` via dependency injection
3. Call `voice_service.process_voice_message(audio_bytes)`
4. Handle domain exceptions → HTTP errors
5. Return standardized response

**Key Improvement:**
- Routes only handle HTTP concerns
- All business logic delegated to use cases
- Clean error handling with proper HTTP codes

### 5. Chat Routes (`app/presentation/api/v1/routes/chat.py`)

**Endpoints:**
- `POST /api/chat` - Send message, receive response
- `GET /api/chat/history` - Get conversation history

**Flow:**
1. Validate request against `ChatRequest` schema
2. Inject `ChatApplicationService`
3. Call `chat_service.send_message()`
4. Use case handles: RAG retrieval, conversation history, LLM call
5. Return standardized response

**Key Improvement:**
- Single endpoint for all chat operations
- Centralized RAG and history logic in use case
- Graceful error handling

### 6. WebSocket Streaming Routes (`app/presentation/api/v1/routes/streaming.py`)

**Endpoints:**
- `WS /ws/voice` - Real-time audio streaming

**Flow:**
1. Accept WebSocket connection
2. Inject `VoiceApplicationService`
3. Loop: receive audio → process → send response
4. Handle `WebSocketDisconnect` gracefully

**Messages:**
```json
// Transcript from Whisper
{"type": "transcript", "text": "...", "interim": true}

// Chat response from LLM
{"type": "chat_response", "text": "...", "original_transcript": "..."}

// Errors
{"type": "error", "message": "..."}
```

### 7. Admin Routes (`app/presentation/api/v1/routes/admin.py`)

**Endpoints:**
- `GET /api/admin/tables` - List tables
- `GET /api/admin/tables/{table}/columns` - Get columns
- `GET /api/admin/tables/{table}/rows` - Read rows
- `POST /api/admin/tables/{table}/rows` - Insert row
- `PATCH /api/admin/tables/{table}/rows/{pk}/{value}` - Update row
- `DELETE /api/admin/tables/{table}/rows/{pk}/{value}` - Delete row

**Improvements:**
- Unified request/response format via `ApiResponse`
- Consistent error handling
- Admin service injected by FastAPI

---

## Request Flow Example: Chat Message

```
1. Client sends POST /api/chat
   {
     "message": "hello",
     "session_id": "user123"
   }

2. FastAPI validates against ChatRequest schema

3. FastAPI injects ChatApplicationService:
   - ChatService needs ChatWithContextUseCase
   - UseCase needs: chat_provider, conversation_service, rag_service, prompt_service
   - conversation_service needs: database session
   - Database session injected via get_db()

4. Route calls: chat_service.send_message()

5. Use Case executes:
   - Get system prompt from PromptService
   - Retrieve RAG context via RagService
   - Get conversation history via ConversationService
   - Build messages for LLM
   - Call ChatProvider (OpenRouter/Groq)
   - Save user & assistant messages to database
   - Return reply

6. Route returns ApiResponse[ChatResponse]

7. Error Handler catches any exceptions:
   - ChatError → HTTP 503
   - DatabaseError → HTTP 503
   - etc.

8. Client receives standardized response:
   {
     "data": {
       "reply": "hello! how can I help?",
       "session_id": "user123"
     },
     "error": null,
     "error_code": null
   }
```

---

## Layer Separation

### Domain Layer (Business Rules)
- Entities: `Message`, `Conversation`, `VoiceStreamSession`
- Exceptions: Domain-specific exceptions
- No dependencies on other layers

### Infrastructure Layer (Technical Details)
- Database: SQLAlchemy ORM, connection pooling
- External Services: Whisper, OpenRouter, Groq wrappers
- No business logic here

### Application Layer (Business Logic)
- Use Cases: `ProcessVoiceUseCase`, `ChatWithContextUseCase`, `StreamVoiceUseCase`
- Services: `VoiceApplicationService`, `ChatApplicationService`
- Orchestrates domain entities and infrastructure
- Depends on: Domain, Infrastructure

### Presentation Layer (API Interface) ← **Phase 4**
- Routes: HTTP endpoints
- Schemas: Request/response models
- Dependency Injection: Service factory
- Error Handler: Exception → HTTP conversion
- Depends on: Application, Domain

---

## Integration with main.py

```python
# Register error handlers
register_error_handlers(app)

# Include old routes (backward compatibility)
app.include_router(voice.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(streaming.router)

# Include new v1 routes
app.include_router(voice_v1.router, prefix="/api")
app.include_router(chat_v1.router, prefix="/api")
app.include_router(admin_v1.router, prefix="/api")
app.include_router(streaming_v1.router)
```

**Note:** Both old and new routes coexist for gradual migration.

---

## Benefits of This Architecture

### 1. **Testability**
Each layer can be tested independently:
- Routes can be tested without database
- Use cases can be tested without HTTP
- Domain logic is pure functions

### 2. **Maintainability**
- Clear separation of concerns
- Easy to locate and modify code
- Each component has single responsibility

### 3. **Scalability**
- Add new endpoints without modifying existing code
- Reuse use cases across different routes
- Add new providers without changing routes

### 4. **Robustness**
- Centralized error handling
- Consistent HTTP responses
- Proper error codes and logging

### 5. **Professional**
- Industry best practices (Clean Architecture)
- Clear folder structure
- Well-documented APIs

---

## Summary

Phase 4 implements the Presentation Layer to complete the Clean Architecture refactoring. The new v1 API:

✅ **Uses application services** instead of raw dependencies
✅ **Centralized error handling** with proper HTTP codes
✅ **Standardized request/response** format
✅ **Dependency injection** for clean component wiring
✅ **Backward compatible** with existing routes
✅ **Production-ready** with logging and error codes

The entire backend now follows a professional, scalable, maintainable architecture! 🚀
