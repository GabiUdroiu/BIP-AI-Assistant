"""
Voice processing routes.
Transcribe audio files to text using the voice application service.
"""

from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.presentation.deps import get_voice_service, log_request_start, log_request_error
from app.application.services.voice_service import VoiceApplicationService
from app.domain.exceptions import VoiceProcessingError, AudioProcessingError
from app.presentation.api.v1.schemas import VoiceProcessResponse, ApiResponse

router = APIRouter(tags=["voice"])


@router.post("/voice/process", response_model=ApiResponse[VoiceProcessResponse])
async def process_voice_message(
    audio: UploadFile = File(...),
    voice_service: VoiceApplicationService = Depends(get_voice_service),
):
    """
    Process audio file and return transcription.

    Receives an audio file and transcribes it to text using the voice service.
    """
    log_request_start("POST /voice/process")

    audio_bytes = await audio.read()
    if not audio_bytes:
        error_msg = "No audio file received"
        log_request_error("POST /voice/process", error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    try:
        transcript = voice_service.process_voice_message(audio_bytes)
        return ApiResponse(data=VoiceProcessResponse(message=transcript))
    except (VoiceProcessingError, AudioProcessingError) as e:
        log_request_error("POST /voice/process", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        log_request_error("POST /voice/process", str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e
