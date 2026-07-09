"""
WebSocket streaming routes.
Continuous audio streaming with real-time transcription and chat responses.
"""

import json
import tempfile
from pathlib import Path
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.presentation.deps import get_voice_service, log_request_error
from app.application.services.voice_service import VoiceApplicationService
from app.domain.exceptions import VoiceProcessingError, ChatError
from app.core.logging import logger

router = APIRouter(tags=["streaming"])


@router.websocket("/ws/voice")
async def websocket_voice_endpoint(
    websocket: WebSocket,
    voice_service: VoiceApplicationService = Depends(get_voice_service),
):
    """
    WebSocket endpoint for continuous audio streaming.

    Receives audio chunks, transcribes them, and sends back transcripts and chat responses.
    """
    await websocket.accept()
    logger.info("📡 WebSocket client connected")

    session_id = "ws_" + str(websocket.client[1]) if websocket.client else "ws_default"
    logger.info(f"🎙️ WebSocket session: {session_id}")

    try:
        while True:
            # Receive complete audio blob from client
            audio_data = await websocket.receive_bytes()

            if not audio_data:
                continue

            logger.info(f"📥 Received audio: {len(audio_data)} bytes")

            try:
                # Save audio blob to temporary file
                with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_path = tmp_file.name

                logger.info(f"💾 Saved to temp file: {tmp_path}")

                # Read file back and process
                with open(tmp_path, 'rb') as f:
                    file_data = f.read()

                # Process voice chunk (transcribe + chat)
                result = voice_service.stream_voice_chunk(
                    audio_bytes=file_data,
                    session_id=session_id,
                )

                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)

                # Send transcript
                if result.get("transcript"):
                    await websocket.send_text(
                        json.dumps({
                            "type": "transcript",
                            "text": result["transcript"],
                            "interim": True,
                        })
                    )
                    logger.info(f"✓ Sent transcript: {result['transcript']}")

                # Send chat response
                if result.get("response"):
                    await websocket.send_text(
                        json.dumps({
                            "type": "chat_response",
                            "text": result["response"],
                            "original_transcript": result.get("transcript"),
                        })
                    )
                    logger.info(f"✓ Sent chat response")

                # Send any errors
                if result.get("error"):
                    await websocket.send_text(
                        json.dumps({
                            "type": "error",
                            "message": result["error"],
                        })
                    )
                    logger.error(f"❌ Processing error: {result['error']}")

            except (VoiceProcessingError, ChatError) as e:
                logger.error(f"❌ Service error: {e}")
                await websocket.send_text(
                    json.dumps({
                        "type": "error",
                        "message": str(e),
                    })
                )
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                await websocket.send_text(
                    json.dumps({
                        "type": "error",
                        "message": "Internal error: " + str(e),
                    })
                )

    except WebSocketDisconnect:
        logger.info(f"📴 WebSocket client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket fatal error: {e}")
        try:
            await websocket.close(code=1011, reason=str(e))
        except:
            pass
