import { API_ENDPOINTS, API_ERRORS } from '../constants/api';

// Determine API URL based on environment
const getApiUrl = (): string => {
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8080/api';
  }
  return 'https://powdering-junction-verbally.ngrok-free.dev/api';
};

export const API_URL = getApiUrl();

export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  error_code: string | null;
}

export interface VoiceResponse {
  message: string;
}

/**
 * Send audio blob to backend for voice processing
 */
export const sendVoiceMessage = async (
  audioBlob: Blob,
): Promise<ApiResponse<VoiceResponse>> => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'voice.webm');

  try {
    const response = await fetch(`${API_URL}${API_ENDPOINTS.VOICE.PROCESS}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(API_ERRORS.VOICE_FAILED);
    }

    return response.json();
  } catch (error) {
    console.error(API_ERRORS.VOICE_FAILED, error);
    throw error;
  }
};
