export interface ApiResponse<T> {
  data?: T;
  error?: string | null;
  error_code?: string | null;
}

export interface VoiceResponse {
  message: string;
  confidence?: number;
  duration_ms?: number;
}

export interface ChatResponse {
  reply: string;
}

export interface ColumnInfo {
  name: string;
  type: string;
  nullable: boolean;
  primary_key: boolean;
}

export interface DashboardRow {
  [key: string]: any;
}
