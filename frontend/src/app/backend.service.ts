import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class BackendService {
  private apiUrl = 'http://localhost:8080/api';

  constructor(private http: HttpClient) {}

  sendVoiceMessage(audioBlob: Blob): Observable<any> {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    return this.http.post(`${this.apiUrl}/voice/process`, formData);
  }
}
