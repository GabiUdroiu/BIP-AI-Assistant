import { useState, useRef, useCallback, useEffect } from 'react';

export const useWebSocketStreaming = (
  onTranscript: (text: string) => void,
  onResponse?: (text: string) => void
) => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [volumeLevel, setVolumeLevel] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const requestRef = useRef<number | undefined>(undefined);
  const isStoppingRef = useRef(false);

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
    const normalized = Math.min(average / 128, 1.0);
    setVolumeLevel(normalized);

    requestRef.current = requestAnimationFrame(processAudioVolume);
  }, []);

  const startStreaming = useCallback(() => {
    return new Promise<void>(async (resolve, reject) => {
      isStoppingRef.current = false;
      try {
        // Smart WebSocket URL - use localhost for local dev, ngrok for production
        let wsUrl: string;
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
          // Local development
          wsUrl = 'ws://localhost:8080/ws/voice';
        } else {
          // Production/ngrok
          wsUrl = 'wss://powdering-junction-verbally.ngrok-free.dev/ws/voice';
        }
        console.log('📡 Connecting to WebSocket:', wsUrl);
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        // Set a timeout for connection
        const connectTimeout = setTimeout(() => {
          console.error('❌ WebSocket connection timeout');
          ws.close();
          reject(new Error('WebSocket connection timeout'));
        }, 10000); // 10 seconds timeout

        ws.onopen = () => {
          clearTimeout(connectTimeout);
          console.log('✅ WebSocket connected');
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('📩 Message:', data.type, data);

            if (data.type === 'transcript') {
              console.log('🎤 Transcript:', data.text);
              onTranscript(data.text);
            } else if (data.type === 'wake_word_detected') {
              console.log('✨ Wake word detected!');
            } else if (data.type === 'chat_response') {
              console.log('💬 Response:', data.text);
              if (onResponse) {
                onResponse(data.text);
              }
            }
          } catch (e) {
            console.error('❌ Failed to parse message:', e);
          }
        };

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          if (!isStoppingRef.current) reject(error);
        };

        ws.onclose = () => {
          console.log('📴 WebSocket closed');
          setIsStreaming(false);
        };

        // Get microphone stream
        console.log('🎤 Requesting microphone...');
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: { echoCancellation: true, noiseSuppression: true }
        });
        streamRef.current = stream;
        console.log('✅ Microphone granted');

        // Setup audio analysis
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        audioContextRef.current = audioContext;
        const source = audioContext.createMediaStreamSource(stream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        analyserRef.current = analyser;

        requestRef.current = requestAnimationFrame(processAudioVolume);

        // Setup MediaRecorder to send chunks to WebSocket
        const mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/ogg';
        const mediaRecorder = new MediaRecorder(stream, { mimeType });
        mediaRecorderRef.current = mediaRecorder;

        let chunkCount = 0;
        const recordedChunks: Blob[] = [];
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            recordedChunks.push(event.data);
          }
        };

        mediaRecorder.onstop = () => {
          console.log('⏹️ Recording stopped, sending audio...');
          if (recordedChunks.length > 0 && ws.readyState === WebSocket.OPEN) {
            const audioBlob = new Blob(recordedChunks, { type: mimeType });
            console.log(`📤 Sending complete audio: ${audioBlob.size} bytes`);
            ws.send(audioBlob);
            recordedChunks.length = 0; // Clear for next recording
          }
        };

        mediaRecorder.onerror = (event) => {
          console.error('❌ MediaRecorder error:', event.error);
        };

        // Record in 5-second chunks, auto-restart recording
        mediaRecorder.start();

        // Every 5 seconds, stop recording (triggers onstop), then restart
        const recordingInterval = setInterval(() => {
          if (mediaRecorder.state === 'recording' && !isStoppingRef.current) {
            mediaRecorder.stop();
            // Restart after a short delay
            setTimeout(() => {
              if (!isStoppingRef.current && mediaRecorderRef.current) {
                mediaRecorder.start();
              }
            }, 100);
          }
        }, 5000);
        setIsStreaming(true);
        console.log('🎙️ Streaming started with', mimeType);
        resolve();
      } catch (err) {
        console.error('❌ Failed to start streaming:', err);
        stopStreaming();
        reject(err);
      }
    });
  }, [onTranscript, onResponse, processAudioVolume]);

  const stopStreaming = useCallback(() => {
    isStoppingRef.current = true;
    console.log('⏹️ Stopping stream...');

    try {
      // Stop recording first
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
        console.log('⏹️ MediaRecorder stopped');
      }

      // Close WebSocket
      if (wsRef.current) {
        if (wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.close(1000, 'Client stopping');
        }
        wsRef.current = null;
        console.log('⏹️ WebSocket closed');
      }

      // Stop all audio tracks
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => {
          track.stop();
        });
        streamRef.current = null;
        console.log('⏹️ Audio tracks stopped');
      }

      // Cancel animation frame
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
        requestRef.current = undefined;
      }

      // Close audio context
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close().catch(() => {});
        audioContextRef.current = null;
        console.log('⏹️ Audio context closed');
      }
    } catch (err) {
      console.error('❌ Error stopping stream:', err);
    }

    setIsStreaming(false);
    setVolumeLevel(0);
    console.log('✅ Stream stopped');
  }, []);

  useEffect(() => {
    return () => {
      stopStreaming();
    };
  }, [stopStreaming]);

  return { isStreaming, volumeLevel, startStreaming, stopStreaming };
};
