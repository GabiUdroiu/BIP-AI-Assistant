export type ListeningMode = 'wake-word-api' | 'websocket-streaming';

const getBackendHost = () => {
  // Use environment variables if set
  if (import.meta.env.VITE_BACKEND_HOST) {
    return import.meta.env.VITE_BACKEND_HOST;
  }
  // Otherwise use the same host as the frontend (allows phone access)
  return `${window.location.hostname}:8080`;
};

const backendHost = getBackendHost();

export const CONFIG = {
  // Choose listening mode:
  // 'wake-word-api' - Web Speech API continuous listening with "hey abubakar" trigger
  // 'websocket-streaming' - Continuous WebSocket streaming to backend
  LISTENING_MODE: 'wake-word-api' as ListeningMode, // Click-to-record mode (no WebSocket)

  WAKE_WORD: 'hey abubakar',
  WAKE_WORD_CONFIDENCE: 0.6, // 0-1, higher = more strict

  API_URL: import.meta.env.VITE_API_URL || `http://${backendHost}/api`,
  WEBSOCKET_URL: import.meta.env.VITE_WEBSOCKET_URL || `ws://${backendHost}/ws/voice`,
};

console.log('🎙️ Listening Mode:', CONFIG.LISTENING_MODE);
console.log('🔌 Backend Host:', backendHost);
