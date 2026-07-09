export type ListeningMode = 'wake-word-api' | 'websocket-streaming';

export const CONFIG = {
  // Choose listening mode:
  // 'wake-word-api' - Web Speech API continuous listening with "hey abubakar" trigger
  // 'websocket-streaming' - Continuous WebSocket streaming to backend
  LISTENING_MODE: (import.meta.env.VITE_LISTENING_MODE || 'wake-word-api') as ListeningMode,

  WAKE_WORD: 'hey abubakar',
  WAKE_WORD_CONFIDENCE: 0.6, // 0-1, higher = more strict

  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8080/api',
  WEBSOCKET_URL: import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8080/ws/voice',
};

console.log('🎙️ Listening Mode:', CONFIG.LISTENING_MODE);
