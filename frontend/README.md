# Robot Arm AI Control Frontend

Angular frontend with:
- 🎤 Voice input (microphone recording)
- 🤖 AI response (text-to-speech)
- 👁️ Face detection (TensorFlow.js)
- 🎯 Face centering detection
- 🦾 Robot arm control integration

## Installation

```bash
cd frontend
npm install
```

## Development Server

```bash
npm start
```

Navigate to `http://localhost:4200/`. The app will auto-reload when you modify files.

## How It Works

1. **Camera Feed** - Shows real-time video with face detection
2. **Center Square** - Yellow square in center; turns green when face is centered
3. **Microphone** - Click "Talk" button to record voice
4. **Backend Processing** - Sends audio to Spring Boot API
5. **AI Response** - Gets response and plays via speaker
6. **Face Tracking** - If face is off-center, sends coordinates to arm controller
7. **Arm Control** - Arm moves to track your face position

## Build

```bash
npm run build
```

Output will be in `dist/robot-arm-ui/`
