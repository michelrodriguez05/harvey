from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel
from backend.assistant import chat
from backend.voice.stt import transcribe_audio_file
from backend.voice.tts import text_to_speech_bytes

router = APIRouter(prefix="/api", tags=["chat"])

conversation_history: list[dict] = []


class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=MessageResponse)
def send_message(req: MessageRequest):
    """Envía un mensaje de texto al asistente."""
    global conversation_history
    conversation_history.append({"role": "user", "content": req.message})

    try:
        reply = chat(conversation_history)
        conversation_history.append({"role": "assistant", "content": reply})
        if len(conversation_history) > 40:
            conversation_history = conversation_history[-40:]
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/transcribe")
async def transcribe_voice(audio: UploadFile = File(...)):
    """Recibe un archivo de audio y retorna el texto transcrito."""
    audio_bytes = await audio.read()
    try:
        text = transcribe_audio_file(audio_bytes, content_type=audio.content_type)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/speak")
def speak(req: MessageRequest):
    """Convierte texto a audio MP3 y lo retorna."""
    try:
        audio_bytes = text_to_speech_bytes(req.message)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/chat")
async def voice_chat(audio: UploadFile = File(...)):
    """Pipeline completo: audio → texto → asistente → audio de respuesta."""
    global conversation_history
    audio_bytes = await audio.read()

    try:
        text = transcribe_audio_file(audio_bytes, content_type=audio.content_type)
        if not text:
            raise HTTPException(status_code=400, detail="No se entendió el audio")

        conversation_history.append({"role": "user", "content": text})
        reply = chat(conversation_history)
        conversation_history.append({"role": "assistant", "content": reply})

        if len(conversation_history) > 40:
            conversation_history = conversation_history[-40:]

        audio_response = text_to_speech_bytes(reply)
        return Response(
            content=audio_response,
            media_type="audio/mpeg",
            headers={"X-Transcript": text, "X-Reply": reply},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def get_history():
    """Retorna el historial de la conversación."""
    return {"messages": conversation_history}


@router.delete("/history")
def clear_history():
    """Limpia el historial de la conversación."""
    global conversation_history
    conversation_history = []
    return {"cleared": True}
