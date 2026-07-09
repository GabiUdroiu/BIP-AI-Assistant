import { useState, useRef, useCallback, useEffect } from 'react';
import { CONFIG } from '../config';

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  isFinal: boolean;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
}

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export const useWakeWordDetection = (onWakeWord: () => void) => {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);
  const listeningTimeoutRef = useRef<number | null>(null);

  const startListening = useCallback(() => {
    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        console.error('❌ Web Speech API not supported');
        return;
      }

      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = false;
      recognition.language = 'en-US';
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        console.log('🎙️ Wake word listener started');
        setIsListening(true);
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        if (event.isFinal) {
          const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
          console.log('🎤 Detected:', transcript);

          // Check for wake word
          if (transcript.includes(CONFIG.WAKE_WORD.toLowerCase())) {
            console.log('✨ WAKE WORD DETECTED!');
            onWakeWord();
            return;
          }
        }
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error('❌ Speech error:', event.error);
        // Restart on error
        listeningTimeoutRef.current = window.setTimeout(() => {
          recognition.start();
        }, 1000);
      };

      recognition.onend = () => {
        console.log('⏹️ Recognition ended, restarting...');
        // Restart automatically when it stops
        listeningTimeoutRef.current = window.setTimeout(() => {
          try {
            recognition.start();
          } catch (e) {
            console.log('Restarting recognition...');
          }
        }, 300);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error('❌ Failed to start wake word detection:', err);
    }
  }, [onWakeWord]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.abort();
      recognitionRef.current = null;
      setIsListening(false);
      if (listeningTimeoutRef.current) {
        clearTimeout(listeningTimeoutRef.current);
      }
    }
  }, []);

  useEffect(() => {
    startListening();
    return () => stopListening();
  }, [startListening, stopListening]);

  return { isListening, stopListening, startListening };
};
