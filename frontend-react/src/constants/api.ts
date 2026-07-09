/**
 * API Configuration & Constants
 * Centralized place for all API-related hardcoded values
 */

// API Endpoints
export const API_ENDPOINTS = {
  VOICE: {
    PROCESS: '/voice/process',
  },
  CHAT: '/chat',
  ADMIN: {
    TABLES: '/admin/tables',
  },
} as const;

// WebSocket Endpoints
export const WS_ENDPOINTS = {
  VOICE: '/ws/voice',
} as const;

// Audio Configuration
export const AUDIO_CONFIG = {
  MIME_TYPES: ['audio/webm', 'audio/ogg'] as const,
  DEFAULT_SAMPLE_RATE: 16000,
  CHUNK_DURATION_MS: 5000,
} as const;

// Wake Word Configuration
export const WAKE_WORD_CONFIG = {
  WAKE_WORD: 'hey abubakar',
  CONFIDENCE_THRESHOLD: 0.6,
  LANGUAGE: 'en-US',
} as const;

// Error Messages
export const API_ERRORS = {
  NO_AUDIO: 'No audio file received',
  CHAT_FAILED: 'Chat error',
  VOICE_FAILED: 'Voice processing error',
  NETWORK_ERROR: 'Network error',
  TIMEOUT: 'Request timeout',
} as const;

// Timeouts (in ms)
export const TIMEOUTS = {
  WEBSOCKET_CONNECTION: 10000,
  API_REQUEST: 30000,
  VOICE_RECORDING: 300000, // 5 minutes max
} as const;
