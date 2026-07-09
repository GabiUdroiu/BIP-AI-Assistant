export type ListeningMode = 'wake-word-api' | 'websocket-streaming';

const getBackendHost = () => {
  // Use environment variables if set
  if (import.meta.env.VITE_BACKEND_HOST) {
    const host = import.meta.env.VITE_BACKEND_HOST;
    // If it's a full URL with protocol, use as-is
    if (host.includes('http://') || host.includes('https://') || host.includes('ws://') || host.includes('wss://')) {
      return host;
    }
    // If it's a ngrok domain, use https
    if (host.includes('ngrok')) {
      return `https://${host}`;
    }
    // Otherwise assume http with port 8000
    return `http://${host}:8000`;
  }
  // Otherwise use the same host as the frontend (allows phone access)
  const protocol = window.location.protocol === 'https:' ? 'https' : 'http';
  return `${protocol}://${window.location.hostname}:8000`;
};

const backendHost = getBackendHost();

const formatApiUrl = (host: string) => {
  if (host.startsWith('http://') || host.startsWith('https://')) {
    return `${host}/api`;
  }
  return host; // Already formatted
};

const formatWebSocketUrl = (host: string) => {
  if (host.startsWith('https://')) {
    return `wss://${host.replace('https://', '')}/ws/voice`;
  }
  if (host.startsWith('http://')) {
    return `ws://${host.replace('http://', '')}/ws/voice`;
  }
  return host; // Already formatted
};

export const CONFIG = {
  // Choose listening mode:
  // 'wake-word-api' - Web Speech API continuous listening with "hey abubakar" trigger
  // 'websocket-streaming' - Continuous WebSocket streaming to backend
  LISTENING_MODE: 'wake-word-api' as ListeningMode, // Click-to-record mode (no WebSocket)

  WAKE_WORD: 'hey abubakar',
  WAKE_WORD_CONFIDENCE: 0.6, // 0-1, higher = more strict

  API_URL: import.meta.env.VITE_API_URL || formatApiUrl(backendHost),
  WEBSOCKET_URL: import.meta.env.VITE_WEBSOCKET_URL || formatWebSocketUrl(backendHost),
};

console.log('🎙️ Listening Mode:', CONFIG.LISTENING_MODE);
console.log('🔌 Backend Host:', backendHost);
console.log('📡 API URL:', CONFIG.API_URL);
console.log('🔗 WebSocket URL:', CONFIG.WEBSOCKET_URL);
