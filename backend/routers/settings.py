from pydantic import BaseModel, Field

from fastapi import APIRouter

from backend.services.conversation import get_llm_status
from backend.services.settings import get_assistant_settings, update_assistant_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    assistant_name: str | None = Field(None, min_length=1, max_length=32)
    wake_word: str | None = Field(None, min_length=1, max_length=32)
    user_name: str | None = Field(None, min_length=1, max_length=64)
    always_listen: bool | None = None
    voice_first: bool | None = None


@router.get("")
def get_settings():
    s = get_assistant_settings()
    llm = get_llm_status()
    return {**s, "llm_provider": llm["provider"], "llm_ready": llm["ok"]}


@router.patch("")
def patch_settings(req: SettingsUpdate):
    updated = update_assistant_settings(
        assistant_name=req.assistant_name,
        wake_word=req.wake_word,
        user_name=req.user_name,
        always_listen=req.always_listen,
        voice_first=req.voice_first,
    )
    return updated
