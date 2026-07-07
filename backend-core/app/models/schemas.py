from pydantic import BaseModel


class VoiceResponse(BaseModel):
    message: str
