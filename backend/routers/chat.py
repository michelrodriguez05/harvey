from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel

from backend.services.conversation import conversation_service, format_user_error, get_llm_status
from backend.voice.stt import transcribe_audio_file
from backend.voice.tts import text_to_speech_bytes

router = APIRouter(prefix="/api", tags=["chat"])


class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    reply: str
    agent: str = "orchestrator"
    tools_used: list[str] = []
    youtube_video_id: str | None = None
    youtube_title: str | None = None


@router.get("/health")
def health_check():
    status = get_llm_status()
    return {
        "status": "ok" if status["ok"] else "misconfigured",
        "api_key_ok": status["ok"],
        "llm_provider": status["provider"],
        "llm_model": status["model"],
        "api_key_message": status.get("message"),
    }


@router.post("/chat", response_model=MessageResponse)
def send_message(req: MessageRequest):
    try:
        result = conversation_service.chat(req.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=format_user_error(e))


@router.post("/voice/transcribe")
async def transcribe_voice(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    try:
        text = transcribe_audio_file(audio_bytes, content_type=audio.content_type)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/speak")
def speak(req: MessageRequest):
    try:
        audio_bytes = text_to_speech_bytes(req.message)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/chat")
async def voice_chat(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    try:
        text = transcribe_audio_file(audio_bytes, content_type=audio.content_type)
        if not text:
            raise HTTPException(status_code=400, detail="No se entendió el audio")

        result = conversation_service.chat(text)
        audio_response = text_to_speech_bytes(result["reply"])
        return Response(
            content=audio_response,
            media_type="audio/mpeg",
            headers={"X-Transcript": text, "X-Reply": result["reply"]},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def get_history():
    messages = conversation_service.get_messages()
    return {"messages": messages}


@router.delete("/history")
def clear_history():
    conversation_service.clear()
    return {"cleared": True}
