from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import get_speech_service
from app.models.api_response import ApiResponse
from app.models.schemas import VoiceResponse
from app.services.speech_service import SpeechService

router = APIRouter(tags=["voice"])


@router.post("/voice/process", response_model=ApiResponse[VoiceResponse])
async def process_voice_message(
    audio: UploadFile = File(...),
    speech_service: SpeechService = Depends(get_speech_service),
):
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="No audio file received")

    print(f"Received audio file: {audio.filename} (size: {len(audio_bytes)} bytes)")

    transcript = speech_service.transcribe(audio_bytes)
    print(f"✓ Transcript: {transcript}")

    return ApiResponse.ok(VoiceResponse(message=transcript or "[No speech detected]"))
