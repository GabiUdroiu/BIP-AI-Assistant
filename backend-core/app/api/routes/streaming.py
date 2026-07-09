import json
import tempfile
from pathlib import Path
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.api.deps import (
    get_speech_service, get_conversation_service, get_rag_service,
    get_prompt_service, get_chat_provider, get_db
)
from app.services.speech_service import SpeechService
from app.services.conversation_service import ConversationService
from app.services.rag_service import RagService
from app.services.prompt_service import PromptService
from app.core.logging import logger

router = APIRouter(tags=["streaming"])


@router.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    """WebSocket endpoint for continuous audio streaming with wake word detection."""
    await websocket.accept()
    logger.info("📡 WebSocket client connected")

    # Initialize services inside the endpoint
    try:
        from app.db.session import get_db
        speech_service = get_speech_service()
        rag_service = get_rag_service()
        prompt_service = get_prompt_service()

        # For conversation service, we need a DB session
        db = next(get_db())
        conversation_service = ConversationService(db)
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        await websocket.send_text(json.dumps({"type": "error", "message": f"Service initialization failed: {str(e)}"}))
        await websocket.close(code=1011)
        return

    WAKE_WORD = "hey abubakar".lower()
    session_id = "ws_" + str(websocket.client[1]) if websocket.client else "ws_default"

    try:
        logger.info(f"🎙️ WebSocket client connected: {session_id}")
        while True:
            # Receive complete audio blob from client (5-second recording)
            audio_data = await websocket.receive_bytes()

            if audio_data:
                logger.info(f"📥 Received audio: {len(audio_data)} bytes")

                try:
                    # Save audio blob to temporary file
                    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as tmp_file:
                        tmp_file.write(audio_data)
                        tmp_path = tmp_file.name

                    logger.info(f"💾 Saved to temp file: {tmp_path} ({len(audio_data)} bytes)")

                    # Read file back and transcribe
                    with open(tmp_path, 'rb') as f:
                        file_data = f.read()

                    transcript = speech_service.transcribe(file_data)
                    logger.info(f"✓ Transcript: {transcript}")

                    # Clean up temp file
                    Path(tmp_path).unlink(missing_ok=True)

                    if transcript:
                        logger.info(f"🎤 Transcribed: {transcript}")

                        # Send transcript to client
                        await websocket.send_text(
                            json.dumps({
                                "type": "transcript",
                                "text": transcript,
                                "interim": True
                            })
                        )

                        # Respond to all transcripts (no wake word gate)
                        # Get chat response using the same logic as /chat endpoint
                        try:
                            chat_provider = get_chat_provider()
                            facts = rag_service.retrieve(transcript)
                            system_prompt = prompt_service.get_system_prompt()
                            if facts:
                                system_prompt += "\n\nRelevant facts:\n" + "\n".join(facts)

                            history = conversation_service.get_history("ws_default")
                            messages = [
                                {"role": "system", "content": system_prompt},
                                *history,
                                {"role": "user", "content": transcript}
                            ]

                            reply = chat_provider.reply(messages)
                            conversation_service.save_message("ws_default", "user", transcript)
                            conversation_service.save_message("ws_default", "assistant", reply)

                            await websocket.send_text(
                                json.dumps({
                                    "type": "chat_response",
                                    "text": reply,
                                    "original_transcript": transcript
                                })
                            )
                        except Exception as e:
                            logger.error(f"❌ Chat error: {e}")
                            await websocket.send_text(
                                json.dumps({
                                    "type": "error",
                                    "message": f"Chat error: {str(e)}"
                                })
                            )

                except Exception as e:
                    logger.error(f"❌ Processing error: {e}")
                    await websocket.send_text(
                        json.dumps({
                            "type": "error",
                            "message": str(e)
                        })
                    )

    except WebSocketDisconnect:
        logger.info("📴 WebSocket client disconnected")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))
