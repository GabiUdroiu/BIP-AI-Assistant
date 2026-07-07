import { useState, useEffect, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { Mic, Square } from 'lucide-react';
import { useAudioRecorder } from './hooks/useAudioRecorder';
import { TechNodeSphere } from './components/TechNodeSphere';
import './index.css';

interface ChatMessage {
  role: 'user' | 'ai';
  text: string;
  timestamp: string;
}

function App() {
  const { isRecording, volumeLevel, startSpeechRecognition, stopRecording, speak } = useAudioRecorder();
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [status, setStatus] = useState('Ready');
  const chatBoxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [chatMessages]);

  const handleToggleRecording = async () => {
    if (!isRecording) {
      setStatus('Listening...');
      try {
        const transcript = await startSpeechRecognition();
        
        setStatus('Ready');
        if (transcript) {
          processMessage(transcript);
        }
      } catch (err) {
        setStatus('Error - try again');
      }
    } else {
      stopRecording();
      setStatus('Ready');
    }
  };

  const processMessage = (transcript: string) => {
    const newUserMsg: ChatMessage = {
      role: 'user',
      text: transcript,
      timestamp: new Date().toLocaleTimeString(),
    };
    
    setChatMessages((prev) => [...prev, newUserMsg]);

    const responses = [
      'That sounds great!',
      'I hear you!',
      'Interesting, tell me more.',
      'Got it!',
      'Nice!',
      'Understood!',
      'Processing your request...'
    ];
    const reply = responses[Math.floor(Math.random() * responses.length)];

    const newAiMsg: ChatMessage = {
      role: 'ai',
      text: reply,
      timestamp: new Date().toLocaleTimeString(),
    };

    setChatMessages((prev) => [...prev, newAiMsg]);
    speak(reply);
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
          <span className={`status-badge ${isRecording ? 'recording' : ''}`}>
            {status}
          </span>
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

        {isRecording && volumeLevel > 0 && (
          <div className="transcript-indicator">
            Listening...
          </div>
        )}

        <div className="controls-wrapper">
          <div className="controls">
            <button className="btn-clear" onClick={clearChat}>
              Clear
            </button>
            
            <button 
              className={`btn-mic ${isRecording ? 'recording' : ''}`}
              onClick={handleToggleRecording}
              title={isRecording ? 'Stop Recording' : 'Start Recording'}
            >
              {isRecording ? <Square size={24} /> : <Mic size={24} />}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
