export const API_URL = 'http://localhost:8081/api';

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: string | null;
}

export const sendVoiceMessage = async (audioBlob: Blob): Promise<ApiResponse<{ message: string }>> => {
  const formData = new FormData();
  // Ensure the filename is provided so the backend treats it as a file upload
  formData.append('audio', audioBlob, 'voice.webm');

  const response = await fetch(`${API_URL}/voice/process`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to send voice message');
  }

  return response.json();
};
