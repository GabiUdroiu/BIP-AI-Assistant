import io

from faster_whisper import WhisperModel


class SpeechService:
    """Offline speech-to-text via faster-whisper. No API key, no network calls."""

    def __init__(self, model_size: str, device: str, compute_type: str) -> None:
        print(f"Loading Whisper model '{model_size}' ({device}/{compute_type})...")
        self._model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("✓ Whisper model ready")

    def transcribe(self, audio_bytes: bytes) -> str:
        buffer = io.BytesIO(audio_bytes)
        segments, _ = self._model.transcribe(buffer, language="en")
        return " ".join(segment.text.strip() for segment in segments).strip()
