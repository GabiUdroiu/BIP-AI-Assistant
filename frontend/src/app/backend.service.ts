import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class BackendService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8080/api';

  sendVoiceMessage(audioBlob: Blob): Observable<any> {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    return this.http.post(`${this.apiUrl}/voice/process`, formData);
  }

  sendChatMessage(message: string, sessionId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/chat`, { message, session_id: sessionId });
  }
}
