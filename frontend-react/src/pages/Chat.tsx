import { useState, useEffect, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { Mic, Square } from 'lucide-react';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
import { useWakeWordDetection } from '../hooks/useWakeWordDetection';
import { useWebSocketStreaming } from '../hooks/useWebSocketStreaming';
import { TechNodeSphere } from '../components/TechNodeSphere';
import { API_URL } from '../services/backendAPI';
import { CONFIG } from '../config';
import { API_ENDPOINTS } from '../constants/api';
import '../index.css';

interface ChatMessage {
  role: 'user' | 'ai';
  text: string;
  timestamp: string;
}

function ChatPage() {
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [status, setStatus] = useState('Ready');
  const chatBoxRef = useRef<HTMLDivElement>(null);

  // Mode 1: Wake Word Detection (only active in wake-word-api mode)
  const [isAwaitingWakeWord, setIsAwaitingWakeWord] = useState(CONFIG.LISTENING_MODE === 'wake-word-api');
  const { isRecording, volumeLevel, startSpeechRecognition, stopRecording, speak } = useAudioRecorder();

  // Wake word detection disabled - using simple click-to-record instead

  // Mode 2: WebSocket Streaming
  const { isStreaming, volumeLevel: wsVolumeLevel, startStreaming, stopStreaming } = useWebSocketStreaming(
    (transcript: string) => {
      console.log('📨 Transcript from WebSocket:', transcript);
      processMessage(transcript, true);
    },
    (response: string) => {
      console.log('📨 Response from WebSocket:', response);
      handleWebSocketResponse(response);
    }
  );

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [chatMessages]);

  const handleStartRecording = async () => {
    setStatus('Recording...');
    try {
      const transcript = await startSpeechRecognition();
      console.log('✓ Got transcript:', transcript);

      setStatus('Ready');
      if (transcript) {
        processMessage(transcript);
      }
    } catch (err) {
      console.error('✗ Recording error:', err);
      setStatus('Error - try again');
    }
  };

  const handleToggleRecording = async () => {
    // Simple click-to-record mode
    if (!isRecording) {
      setStatus('Recording...');
      try {
        await handleStartRecording();
      } catch (err) {
        console.error('✗ Recording error:', err);
        setStatus('Error - try again');
      }
    }
  };

  const handleWebSocketResponse = async (reply: string) => {
    console.log('💭 Handling WebSocket response:', reply);
    const newAiMsg: ChatMessage = {
      role: 'ai',
      text: reply,
      timestamp: new Date().toLocaleTimeString(),
    };

    setChatMessages((prev) => [...prev, newAiMsg]);
    setStatus('Speaking...');

    // Stop WebSocket streaming while bot speaks (prevents hearing itself)
    console.log('🔇 Pausing stream during TTS...');
    stopStreaming();

    // Speak and wait for it to finish
    await new Promise<void>((resolve) => {
      const utterance = new SpeechSynthesisUtterance(reply);
      utterance.onend = () => {
        console.log('✅ TTS finished');
        resolve();
      };
      window.speechSynthesis.speak(utterance);
    });

    // Resume WebSocket streaming after bot finishes speaking
    console.log('🔊 Resuming stream...');
    await startStreaming();

    setStatus('Listening...');
  };

  const processMessage = async (transcript: string, fromWebSocket: boolean = false) => {
    const newUserMsg: ChatMessage = {
      role: 'user',
      text: transcript,
      timestamp: new Date().toLocaleTimeString(),
    };

    setChatMessages((prev) => [...prev, newUserMsg]);

    // In WebSocket streaming mode, response comes from WebSocket, so just wait for it
    if (fromWebSocket && CONFIG.LISTENING_MODE === 'websocket-streaming') {
      console.log('⏳ Waiting for WebSocket response...');
      setStatus('Listening...');
      return;
    }

    // For wake-word mode, fetch the response via API
    setStatus('Getting response...');

    try {
      const response = await fetch(`${API_URL}${API_ENDPOINTS.CHAT}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: transcript }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const result = await response.json();
      console.log('✓ Chat response:', result);
      const reply = result.data?.reply || 'Sorry, I could not understand that.';
      console.log('Reply text:', reply);

      const newAiMsg: ChatMessage = {
        role: 'ai',
        text: reply,
        timestamp: new Date().toLocaleTimeString(),
      };

      setChatMessages((prev) => [...prev, newAiMsg]);
      setStatus('Speaking...');

      // Speak and wait for it to finish
      await new Promise<void>((resolve) => {
        const utterance = new SpeechSynthesisUtterance(reply);
        utterance.onend = () => {
          console.log('✅ TTS finished');
          resolve();
        };
        window.speechSynthesis.speak(utterance);
      });

      setStatus('Listening...');
    } catch (err) {
      setStatus('Error getting response');
      console.error('✗ Chat error:', err);
      console.error('Error details:', err instanceof Error ? err.message : String(err));
    }
  };

  const clearChat = () => {
    setChatMessages([]);
    setStatus('Ready');
  };

  return (
    <>
      <div className="canvas-container">
        <Canvas camera={{ position: [0, 0, 5], fov: 60 }}>
          <TechNodeSphere volumeLevel={volumeLevel} />
        </Canvas>
      </div>

      <div className="ui-overlay">
        <div className="header">
          <h1>Voice AI</h1>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span className="status-badge" style={{ fontSize: '11px', opacity: 0.6 }}>
              {CONFIG.LISTENING_MODE === 'wake-word-api' ? '🎤 Wake Word' : '📡 WebSocket'}
            </span>
            <span className={`status-badge ${isRecording || isStreaming ? 'recording' : ''}`}>
              {status}
            </span>
          </div>
        </div>

        <div className="main-content">
          <div className="chat-box" ref={chatBoxRef}>
            {chatMessages.length === 0 ? (
              <div className="empty-state">Press the mic and start talking.</div>
            ) : (
              chatMessages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="bubble">{msg.text}</div>
                  <span className="timestamp">{msg.timestamp}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {(isRecording || isStreaming) && (volumeLevel > 0 || wsVolumeLevel > 0) && (
          <div className="transcript-indicator">
            {CONFIG.LISTENING_MODE === 'wake-word-api' ? 'Recording...' : 'Streaming...'}
          </div>
        )}

        <div className="controls-wrapper">
          <div className="controls">
            <button className="btn-clear" onClick={clearChat}>
              Clear
            </button>

            <button
              className={`btn-mic ${isRecording || isStreaming ? 'recording' : ''}`}
              onClick={handleToggleRecording}
              title={CONFIG.LISTENING_MODE === 'wake-word-api'
                ? (isAwaitingWakeWord ? 'Disable listening' : 'Enable listening')
                : (isStreaming ? 'Stop streaming' : 'Start streaming')}
            >
              {isRecording || isStreaming ? <Square size={24} /> : <Mic size={24} />}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default ChatPage;
