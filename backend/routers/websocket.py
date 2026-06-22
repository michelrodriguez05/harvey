import base64

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.services.conversation import conversation_service, format_user_error
from backend.voice.stt import transcribe_audio_file
from backend.voice.tts import text_to_speech_bytes

router = APIRouter(tags=["websocket"])


async def _process_chat(ws: WebSocket, text: str, session_id: str, with_audio: bool = False) -> None:
    await ws.send_json({"type": "status", "state": "thinking"})

    try:
        result = conversation_service.chat(text, session_id=session_id)
        reply = result["reply"]

        await ws.send_json({
            "type": "reply",
            "text": reply,
            "agent": result["agent"],
            "tools_used": result["tools_used"],
            "youtube_video_id": result.get("youtube_video_id"),
            "youtube_title": result.get("youtube_title"),
        })

        if result.get("youtube_video_id"):
            await ws.send_json({
                "type": "play_youtube",
                "video_id": result["youtube_video_id"],
                "title": result.get("youtube_title"),
            })

        if with_audio and not result.get("youtube_video_id"):
            await ws.send_json({"type": "status", "state": "speaking"})
            audio = text_to_speech_bytes(reply)
            await ws.send_json({
                "type": "audio",
                "data": base64.b64encode(audio).decode(),
                "mime": "audio/mpeg",
            })
    except Exception as e:
        await ws.send_json({"type": "error", "message": format_user_error(e)})
    finally:
        await ws.send_json({"type": "status", "state": "idle"})


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    session_id = "ws"

    try:
        await ws.send_json({"type": "connected", "message": "Conexión establecida"})

        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")

            if msg_type == "ping":
                await ws.send_json({"type": "pong"})
                continue

            if msg_type == "message":
                text = (data.get("content") or "").strip()
                if not text:
                    continue
                await _process_chat(ws, text, session_id, with_audio=data.get("with_audio", False))
                continue

            if msg_type == "audio":
                raw = base64.b64decode(data.get("data", ""))
                mime = data.get("mime", "audio/webm")

                await ws.send_json({"type": "status", "state": "listening"})
                try:
                    text = transcribe_audio_file(raw, content_type=mime)
                except Exception as e:
                    await ws.send_json({"type": "error", "message": format_user_error(e)})
                    await ws.send_json({"type": "status", "state": "idle"})
                    continue

                if not text:
                    await ws.send_json({"type": "error", "message": "No se entendió el audio"})
                    await ws.send_json({"type": "status", "state": "idle"})
                    continue

                await ws.send_json({"type": "transcript", "role": "user", "text": text})
                await _process_chat(ws, text, session_id, with_audio=True)
                continue

            if msg_type == "clear":
                conversation_service.clear(session_id)
                await ws.send_json({"type": "cleared"})
                continue

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "message": format_user_error(e)})
        except Exception:
            pass
