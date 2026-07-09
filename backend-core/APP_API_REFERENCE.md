# API Reference - Presentation Layer v1

This document describes the v1 API endpoints created in the Presentation Layer as part of the Clean Architecture refactoring.

## Overview

All endpoints follow a standard response format with centralized error handling:

```json
{
  "data": {/* response data */},
  "error": null,
  "error_code": null
}
```

Errors include an error code for programmatic handling:

```json
{
  "data": null,
  "error": "Error description",
  "error_code": "ERROR_CODE"
}
```

---

## Voice Endpoints

### POST /api/voice/process
Transcribe an audio file to text.

**Request:**
- Form data: `audio` (binary file, required)

**Response:**
```json
{
  "data": {
    "message": "transcribed text"
  }
}
```

**Error Codes:**
- `VOICE_PROCESSING_ERROR` - Transcription failed
- `AUDIO_PROCESSING_ERROR` - Audio format invalid

---

## Chat Endpoints

### POST /api/chat
Send a message and receive an AI response.

**Request:**
```json
{
  "message": "user message",
  "session_id": "default"
}
```

**Response:**
```json
{
  "data": {
    "reply": "assistant response",
    "session_id": "default"
  }
}
```

**Error Codes:**
- `CHAT_ERROR` - LLM provider error
- `CONTEXT_RETRIEVAL_ERROR` - RAG retrieval failed
- `DATABASE_ERROR` - Database operation failed

### GET /api/chat/history
Retrieve conversation history for a session.

**Query Parameters:**
- `session_id` (string, default: "default")

**Response:**
```json
{
  "data": {
    "session_id": "default",
    "messages": [
      {
        "role": "user",
        "content": "message text",
        "timestamp": "2026-07-09T10:30:00"
      }
    ]
  }
}
```

---

## WebSocket Streaming Endpoint

### WS /ws/voice
Real-time audio streaming with transcription and chat responses.

**Client → Server:**
- Binary audio data (WebM format)

**Server → Client:**

Transcript message:
```json
{
  "type": "transcript",
  "text": "transcribed text",
  "interim": true
}
```

Chat response:
```json
{
  "type": "chat_response",
  "text": "assistant response",
  "original_transcript": "user transcript"
}
```

Error message:
```json
{
  "type": "error",
  "message": "error description"
}
```

---

## Admin Endpoints

### GET /api/admin/tables
List all database tables.

**Response:**
```json
{
  "data": ["table_name1", "table_name2"]
}
```

### GET /api/admin/tables/{table_name}/columns
Get column information for a table.

**Response:**
```json
{
  "data": [
    {
      "name": "id",
      "type": "INTEGER",
      "nullable": false,
      "primary_key": true
    }
  ]
}
```

### GET /api/admin/tables/{table_name}/rows
Get rows from a table.

**Query Parameters:**
- `limit` (integer, default: 50)

**Response:**
```json
{
  "data": {
    "table": "table_name",
    "rows": [/* row data */],
    "count": 10
  }
}
```

### POST /api/admin/tables/{table_name}/rows
Insert a row into a table.

**Request:**
```json
{
  "data": {
    "column1": "value1",
    "column2": "value2"
  }
}
```

### PATCH /api/admin/tables/{table_name}/rows/{pk_column}/{pk_value}
Update a row in a table.

**Request:**
```json
{
  "data": {
    "column1": "new_value"
  }
}
```

### DELETE /api/admin/tables/{table_name}/rows/{pk_column}/{pk_value}
Delete a row from a table.

**Response:**
```json
{
  "data": {
    "deleted": true
  }
}
```

---

## Error Codes Reference

| Error Code | HTTP Status | Description |
|-----------|------------|-------------|
| `VOICE_PROCESSING_ERROR` | 400 | Audio transcription failed |
| `AUDIO_PROCESSING_ERROR` | 400 | Audio format or processing error |
| `CHAT_ERROR` | 503 | LLM provider error |
| `CONTEXT_RETRIEVAL_ERROR` | 503 | RAG context retrieval failed |
| `CONFIGURATION_ERROR` | 500 | Missing configuration |
| `EXTERNAL_SERVICE_ERROR` | 503 | External service unavailable |
| `DATABASE_ERROR` | 503 | Database operation failed |
| `CONVERSATION_NOT_FOUND` | 404 | Session not found |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error |

---

## Architecture

The v1 API routes are organized in the Presentation Layer following Clean Architecture:

```
Domain Layer
    ↓ (business entities & rules)
Application Layer
    ↓ (use cases & business logic)
Infrastructure Layer
    ↓ (external services & data access)
Presentation Layer ← Routes, Schemas, Error Handling
```

**Key Components:**

- **Routes** (`app/presentation/api/v1/routes/`): HTTP endpoints
- **Schemas** (`app/presentation/api/v1/schemas.py`): Request/response models
- **Dependency Injection** (`app/presentation/deps.py`): Service factory
- **Error Handler** (`app/presentation/error_handler.py`): Centralized error handling

**Backward Compatibility:**

The old routes (`app/api/routes/`) continue to work alongside the new v1 routes, allowing gradual migration.
