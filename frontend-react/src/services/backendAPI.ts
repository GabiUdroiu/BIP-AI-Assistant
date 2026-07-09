// Use dynamic backend host to support phone access
const backendHost = import.meta.env.VITE_BACKEND_HOST || `${window.location.hostname}:8080`;
export const API_URL = `http://${backendHost}/api`;

export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  error_code: string | null;
}

export const sendVoiceMessage = async (
  audioBlob: Blob,
): Promise<ApiResponse<{ message: string }>> => {
  const formData = new FormData();
  // Ensure the filename is provided so the backend treats it as a file upload
  formData.append("audio", audioBlob, "voice.webm");

  const response = await fetch(`${API_URL}/voice/process`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to send voice message");
  }

  return response.json();
};
