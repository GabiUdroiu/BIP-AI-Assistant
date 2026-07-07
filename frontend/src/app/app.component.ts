import { Component, ViewChild, ElementRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AudioService } from './audio.service';

interface ChatMessage {
  role: 'user' | 'ai';
  text: string;
  timestamp: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  @ViewChild('chatBox') chatBox!: ElementRef<HTMLDivElement>;

  isRecording = false;
  status = 'Ready';
  currentTranscript = '';
  chatMessages: ChatMessage[] = [];
  private transcriptSubscription: any;

  constructor(
    private audioService: AudioService,
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

    const responses = [
      'That sounds great!',
      'I hear you!',
      'Interesting, tell me more.',
      'Got it!',
      'Nice!',
      'Understood!'
    ];
    const reply = responses[Math.floor(Math.random() * responses.length)];

    this.chatMessages.push({
      role: 'ai',
      text: reply,
      timestamp: new Date().toLocaleTimeString()
    });
    this.audioService.speak(reply);
    this.scrollToBottom();
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
