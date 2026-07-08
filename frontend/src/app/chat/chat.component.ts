import { Component, ElementRef, NgZone, ViewChild, inject, signal, OnInit, OnDestroy, DestroyRef } from '@angular/core';
import { Subscription } from 'rxjs';
import { AudioService } from '../audio.service';
import { BackendService } from '../backend.service';

interface ChatMessage {
  role: 'user' | 'ai';
  text: string;
  timestamp: string;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit, OnDestroy {
  @ViewChild('chatBox') readonly chatBox!: ElementRef<HTMLDivElement>;
  @ViewChild('waveform') readonly waveform!: ElementRef<HTMLCanvasElement>;

  private readonly audioService = inject(AudioService);
  private readonly backendService = inject(BackendService);
  private readonly ngZone = inject(NgZone);

  protected readonly isRecording = signal(false);
  protected readonly status = signal('Initializing...');
  protected readonly currentTranscript = signal('');
  protected readonly isProcessing = signal(false);
  protected readonly chatMessages = signal<ChatMessage[]>([]);

  private transcriptSubscription: Subscription | null = null;
  private readonly sessionId = this.getOrCreateSessionId();
  private retryCount = 0;
  private readonly MAX_RETRIES = 5;

  private noiseBaseline = 15;
  private baselineFrames = 0;
  private readonly BASELINE_FRAMES_TARGET = 30;

  ngOnInit() {
    this.startListening();
  }

  ngOnDestroy() {
    this.transcriptSubscription?.unsubscribe();
  }

  private getOrCreateSessionId(): string {
    const stored = sessionStorage.getItem('bip_session_id');
    if (stored) return stored;

    const sessionId = crypto.randomUUID();
    sessionStorage.setItem('bip_session_id', sessionId);
    return sessionId;
  }

  private startListening() {
    this.status.set('Listening...');
    this.isRecording.set(true);
    this.currentTranscript.set('');
    this.baselineFrames = 0;
    this.noiseBaseline = 15;
    this.retryCount = 0;
    setTimeout(() => this.drawWaveform(), 100);

    const transcript$ = this.audioService.startSpeechRecognition();

    this.transcriptSubscription = transcript$.subscribe({
      next: (text) => {
        this.ngZone.run(() => {
          if (text) {
            this.currentTranscript.set(text);
          }
        });
      },
      complete: () => {
        this.ngZone.run(() => {
          this.isRecording.set(false);
          if (this.currentTranscript()) {
            this.processMessage(this.currentTranscript());
          } else {
            setTimeout(() => this.startListening(), 500);
          }
        });
      },
      error: () => {
        this.ngZone.run(() => {
          this.isRecording.set(false);
          this.status.set('Error - retrying...');
          setTimeout(() => this.startListening(), 1000);
        });
      }
    });
  }

  private drawWaveform() {
    const canvas = this.waveform?.nativeElement;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const animate = () => {
      if (!this.isRecording()) return;

      const data = this.audioService.getFrequencyData();
      if (!data) {
        requestAnimationFrame(animate);
        return;
      }

      ctx.fillStyle = '#f4f4f5';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const radius = Math.min(centerX, centerY) - 8;

      const avgFrequency = Array.from(data).reduce((a, b) => a + b, 0) / data.length;
      const maxFrequency = Math.max(...Array.from(data));

      // Adaptive baseline calibration - first 30 frames establish noise floor
      if (this.baselineFrames < this.BASELINE_FRAMES_TARGET) {
        this.noiseBaseline = Math.min(this.noiseBaseline, avgFrequency);
        this.baselineFrames++;
      }

      const signalAboveNoise = avgFrequency - this.noiseBaseline;
      const maxAboveNoise = maxFrequency - this.noiseBaseline;
      const relativeIntensity = (signalAboveNoise + maxAboveNoise) / 2 / 100;

      let color = '#4ade80';
      if (relativeIntensity > 0.6) color = '#fbbf24';
      if (relativeIntensity > 1.2) color = '#ef4444';

      // Draw circle
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.stroke();

      ctx.fillStyle = color + '22';
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius * 0.95, 0, Math.PI * 2);
      ctx.fill();

      // Draw microphone
      this.drawMicrophone(ctx, centerX, centerY, radius * 0.25);

      // Draw frequency bars around circle
      const barCount = 32;
      for (let i = 0; i < barCount; i++) {
        const angle = (i / barCount) * Math.PI * 2;
        const dataIndex = Math.floor((i / barCount) * data.length);
        const height = (data[dataIndex] / 255) * (radius * 0.4);

        const x1 = centerX + Math.cos(angle) * radius;
        const y1 = centerY + Math.sin(angle) * radius;
        const x2 = centerX + Math.cos(angle) * (radius + height);
        const y2 = centerY + Math.sin(angle) * (radius + height);

        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      }

      requestAnimationFrame(animate);
    };

    animate();
  }

  private drawMicrophone(ctx: CanvasRenderingContext2D, x: number, y: number, size: number) {
    ctx.fillStyle = '#18181b';
    ctx.beginPath();
    ctx.arc(x, y - size * 0.3, size * 0.5, Math.PI, 0);
    ctx.lineTo(x + size * 0.5, y + size * 0.2);
    ctx.quadraticCurveTo(x, y + size * 0.6, x - size * 0.5, y + size * 0.2);
    ctx.closePath();
    ctx.fill();

    ctx.fillRect(x - size * 0.15, y + size * 0.2, size * 0.3, size * 0.5);
  }

  private async processMessage(transcript: string) {
    this.chatMessages.update((messages) => [
      ...messages,
      { role: 'user', text: transcript, timestamp: new Date().toLocaleTimeString() }
    ]);
    this.scrollToBottom();
    this.isProcessing.set(true);
    this.status.set('Thinking...');

    this.backendService.sendChatMessage(transcript, this.sessionId).subscribe({
      next: async (res) => {
        this.ngZone.run(() => {
          const reply = res?.data?.reply || '[No reply]';
          this.chatMessages.update((messages) => [
            ...messages,
            { role: 'ai', text: reply, timestamp: new Date().toLocaleTimeString() }
          ]);
          this.isProcessing.set(false);
          this.scrollToBottom();
        });

        await this.audioService.speak(res?.data?.reply || '[No reply]');
        this.ngZone.run(() => this.startListening());
      },
      error: () => {
        this.ngZone.run(() => {
          this.chatMessages.update((messages) => [
            ...messages,
            { role: 'ai', text: '[Chat backend unavailable]', timestamp: new Date().toLocaleTimeString() }
          ]);
          this.isProcessing.set(false);
          this.scrollToBottom();

          this.retryCount++;
          const delayMs = Math.min(1000 * Math.pow(2, this.retryCount), 30000);

          if (this.retryCount >= this.MAX_RETRIES) {
            this.status.set('Max retries reached - please refresh');
            return;
          }

          setTimeout(() => this.startListening(), delayMs);
        });
      }
    });
  }

  private scrollToBottom() {
    setTimeout(() => {
      const chatBox = this.chatBox?.nativeElement;
      if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
      }
    }, 100);
  }

  protected clearChat() {
    this.chatMessages.set([]);
    this.status.set('Ready');
  }
}
