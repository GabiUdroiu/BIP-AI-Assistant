import { Injectable, inject } from '@angular/core';
import { Observable, firstValueFrom } from 'rxjs';
import { BackendService } from './backend.service';

const RECORDING_DURATION_MS = 5000;

@Injectable({ providedIn: 'root' })
export class AudioService {
  private readonly backendService = inject(BackendService);

  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private isRecording = false;
  private mimeType = 'audio/webm';

  startSpeechRecognition(): Observable<string> {
    return new Observable(observer => {
      this.recordAudio()
        .then(audioBlob => firstValueFrom(this.backendService.sendVoiceMessage(audioBlob)))
        .then(res => {
          observer.next(res?.data?.message || '[No speech detected]');
          observer.complete();
        })
        .catch(e => {
          console.error('Voice processing error:', e);
          observer.error(e);
        });
    });
  }

  private recordAudio(): Promise<Blob> {
    return new Promise(async (resolve, reject) => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/ogg';
        this.mediaRecorder = new MediaRecorder(stream, { mimeType: this.mimeType });
        this.audioChunks = [];
        this.isRecording = true;

        console.log('✓ Listening... (up to 5 seconds)');

        this.mediaRecorder.ondataavailable = (event) => {
          this.audioChunks.push(event.data);
        };

        this.mediaRecorder.onstop = () => {
          const audioBlob = new Blob(this.audioChunks, { type: this.mimeType });
          stream.getTracks().forEach(track => track.stop());
          this.isRecording = false;
          resolve(audioBlob);
        };

        this.mediaRecorder.start();

        setTimeout(() => {
          if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
          }
        }, RECORDING_DURATION_MS);
      } catch (e) {
        reject(e);
      }
    });
  }

  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
    }
  }

  speak(text: string) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  }
}
