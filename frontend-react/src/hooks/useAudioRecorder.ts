import { useState, useRef, useCallback, useEffect } from 'react';
import { sendVoiceMessage } from '../services/backendAPI';

const RECORDING_DURATION_MS = 5000;

export const useAudioRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [volumeLevel, setVolumeLevel] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const requestRef = useRef<number | undefined>(undefined);

  const processAudioVolume = useCallback(() => {
    if (!analyserRef.current) return;
    const analyser = analyserRef.current;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(dataArray);

    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      sum += dataArray[i];
    }
    const average = sum / dataArray.length;
    // Normalize to 0-1 (roughly, max is 255 but average is lower)
    const normalized = Math.min(average / 128, 1.0); 
    setVolumeLevel(normalized);

    requestRef.current = requestAnimationFrame(processAudioVolume);
  }, []);

  const stopRecordingInternal = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    setVolumeLevel(0);
  }, []);

  const startSpeechRecognition = useCallback((): Promise<string> => {
    return new Promise(async (resolve, reject) => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;

        // Setup audio analysis
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        audioContextRef.current = audioContext;
        const source = audioContext.createMediaStreamSource(stream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        analyserRef.current = analyser;
        
        requestRef.current = requestAnimationFrame(processAudioVolume);

        const mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/ogg';
        const mediaRecorder = new MediaRecorder(stream, { mimeType });
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];
        setIsRecording(true);

        mediaRecorder.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };

        mediaRecorder.onstop = async () => {
          console.log('MediaRecorder stopped. Chunks length:', audioChunksRef.current.length);
          const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
          console.log('Created Blob size:', audioBlob.size, 'type:', mimeType);
          
          if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
          }
          if (requestRef.current) {
            cancelAnimationFrame(requestRef.current);
          }
          if (audioContextRef.current) {
            audioContextRef.current.close();
          }

          try {
            console.log('Sending voice message to backend...');
            const res = await sendVoiceMessage(audioBlob);
            console.log('Backend response:', res);
            if (!res.error && res.data) {
              console.log('✓ Got transcript:', res.data.message);
              resolve(res.data.message || '[No speech detected]');
            } else {
              console.error('✗ Backend error:', res.error);
              reject(new Error(res.error || 'Backend returned an error'));
            }
          } catch (e) {
            console.error('✗ Voice processing error:', e);
            reject(e);
          }
        };

        mediaRecorder.start();

        setTimeout(() => {
          stopRecordingInternal();
        }, RECORDING_DURATION_MS);
      } catch (e) {
        reject(e);
      }
    });
  }, [processAudioVolume, stopRecordingInternal]);

  const stopRecording = useCallback(() => {
    stopRecordingInternal();
  }, [stopRecordingInternal]);

  const speak = useCallback((text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  }, []);

  useEffect(() => {
    return () => {
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
    };
  }, []);

  return {
    isRecording,
    volumeLevel,
    startSpeechRecognition,
    stopRecording,
    speak,
  };
};
