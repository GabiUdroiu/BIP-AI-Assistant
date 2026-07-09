// Use dynamic backend host to support phone access
let API_URL: string;
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  // Local development - HTTP
  API_URL = 'http://localhost:8080/api';
} else {
  // Production/ngrok - HTTPS
  API_URL = 'https://powdering-junction-verbally.ngrok-free.dev/api';
}

export { API_URL };

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
