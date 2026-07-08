import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { EnvironmentService } from './environment.service';
import { ApiResponse, VoiceResponse, ChatResponse } from './models/api-response';

@Injectable({ providedIn: 'root' })
export class BackendService {
  private readonly http = inject(HttpClient);
  private readonly env = inject(EnvironmentService);

  sendVoiceMessage(audioBlob: Blob): Observable<ApiResponse<VoiceResponse>> {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    return this.http.post<ApiResponse<VoiceResponse>>(
      `${this.env.getApiUrl()}/voice/process`,
      formData
    );
  }

  sendChatMessage(message: string, sessionId: string): Observable<ApiResponse<ChatResponse>> {
    return this.http.post<ApiResponse<ChatResponse>>(
      `${this.env.getApiUrl()}/chat`,
      { message, session_id: sessionId }
    );
  }
}
