import { Component, ViewChild, ElementRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
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
  imports: [CommonModule],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent {
  @ViewChild('chatBox') chatBox!: ElementRef<HTMLDivElement>;

  isRecording = false;
  status = 'Ready';
  currentTranscript = '';
  isProcessing = false;
  chatMessages: ChatMessage[] = [];
  private transcriptSubscription: any;
  private sessionId = crypto.randomUUID();

  constructor(
    private audioService: AudioService,
    private backendService: BackendService,
    private ngZone: NgZone
  ) {}

  toggleRecording() {
    if (!this.isRecording) {
      this.status = 'Listening...';
      this.isRecording = true;
      this.currentTranscript = '';

      const transcript$ = this.audioService.startSpeechRecognition();

      this.transcriptSubscription = transcript$.subscribe({
        next: (text) => {
          this.ngZone.run(() => {
            if (text) {
              this.currentTranscript = text;
            }
          });
        },
        complete: () => {
          this.ngZone.run(() => {
            this.isRecording = false;
            this.status = 'Ready';
            if (this.currentTranscript) {
              this.processMessage(this.currentTranscript);
            }
          });
        },
        error: () => {
          this.ngZone.run(() => {
            this.isRecording = false;
            this.status = 'Error - try again';
          });
        }
      });
    } else {
      this.audioService.stopRecording();
      this.isRecording = false;
    }
  }

  private processMessage(transcript: string) {
    this.chatMessages.push({
      role: 'user',
      text: transcript,
      timestamp: new Date().toLocaleTimeString()
    });
    this.scrollToBottom();
    this.isProcessing = true;
    this.status = 'Thinking...';

    this.backendService.sendChatMessage(transcript, this.sessionId).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          const reply = res?.data?.reply || '[No reply]';
          this.chatMessages.push({
            role: 'ai',
            text: reply,
            timestamp: new Date().toLocaleTimeString()
          });
          this.audioService.speak(reply);
          this.isProcessing = false;
          this.status = 'Ready';
          this.scrollToBottom();
        });
      },
      error: () => {
        this.ngZone.run(() => {
          this.chatMessages.push({
            role: 'ai',
            text: '[Chat backend unavailable]',
            timestamp: new Date().toLocaleTimeString()
          });
          this.isProcessing = false;
          this.status = 'Error - try again';
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

  clearChat() {
    this.chatMessages = [];
    this.status = 'Ready';
  }
}
