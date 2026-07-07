import { Component, ElementRef, NgZone, ViewChild, inject, signal } from '@angular/core';
import { AudioService } from '../audio.service';
import { BackendService } from '../backend.service';

interface ChatMessage {
  role: 'user' | 'ai';
  text: string;
  timestamp: string;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent {
  @ViewChild('chatBox') readonly chatBox!: ElementRef<HTMLDivElement>;

  private readonly audioService = inject(AudioService);
  private readonly backendService = inject(BackendService);
  private readonly ngZone = inject(NgZone);

  protected readonly isRecording = signal(false);
  protected readonly status = signal('Ready');
  protected readonly currentTranscript = signal('');
  protected readonly isProcessing = signal(false);
  protected readonly chatMessages = signal<ChatMessage[]>([]);

  private transcriptSubscription: any;
  private readonly sessionId = crypto.randomUUID();

  protected toggleRecording() {
    if (!this.isRecording()) {
      this.status.set('Listening...');
      this.isRecording.set(true);
      this.currentTranscript.set('');

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
            this.status.set('Ready');
            if (this.currentTranscript()) {
              this.processMessage(this.currentTranscript());
            }
          });
        },
        error: () => {
          this.ngZone.run(() => {
            this.isRecording.set(false);
            this.status.set('Error - try again');
          });
        }
      });
    } else {
      this.audioService.stopRecording();
      this.isRecording.set(false);
    }
  }

  private processMessage(transcript: string) {
    this.chatMessages.update((messages) => [
      ...messages,
      { role: 'user', text: transcript, timestamp: new Date().toLocaleTimeString() }
    ]);
    this.scrollToBottom();
    this.isProcessing.set(true);
    this.status.set('Thinking...');

    this.backendService.sendChatMessage(transcript, this.sessionId).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          const reply = res?.data?.reply || '[No reply]';
          this.chatMessages.update((messages) => [
            ...messages,
            { role: 'ai', text: reply, timestamp: new Date().toLocaleTimeString() }
          ]);
          this.audioService.speak(reply);
          this.isProcessing.set(false);
          this.status.set('Ready');
          this.scrollToBottom();
        });
      },
      error: () => {
        this.ngZone.run(() => {
          this.chatMessages.update((messages) => [
            ...messages,
            { role: 'ai', text: '[Chat backend unavailable]', timestamp: new Date().toLocaleTimeString() }
          ]);
          this.isProcessing.set(false);
          this.status.set('Error - try again');
          this.scrollToBottom();
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
