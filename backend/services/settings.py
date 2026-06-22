import json

from backend.core.config import settings
from backend.memory.store import MemoryStore

_store = MemoryStore()


def get_assistant_settings() -> dict:
    ctx = _store.get_context()
    prefs = ctx.preferences or {}
    return {
        "assistant_name": prefs.get("assistant_name") or settings.assistant_name,
        "wake_word": prefs.get("wake_word") or settings.wake_word,
        "user_name": ctx.user_name or settings.user_name,
        "always_listen": prefs.get("always_listen", True),
        "voice_first": prefs.get("voice_first", True),
    }


def update_assistant_settings(
    assistant_name: str | None = None,
    wake_word: str | None = None,
    user_name: str | None = None,
    always_listen: bool | None = None,
    voice_first: bool | None = None,
) -> dict:
    current = get_assistant_settings()
    if assistant_name is not None:
        current["assistant_name"] = assistant_name.strip()
        current["wake_word"] = wake_word.strip() if wake_word else assistant_name.strip()
    elif wake_word is not None:
        current["wake_word"] = wake_word.strip()
    if user_name is not None:
        current["user_name"] = user_name.strip()
        _store.set_user_name(current["user_name"])
    if always_listen is not None:
        current["always_listen"] = always_listen
    if voice_first is not None:
        current["voice_first"] = voice_first

    _store.set_preference("assistant_name", current["assistant_name"])
    _store.set_preference("wake_word", current["wake_word"])
    _store.set_preference("always_listen", current["always_listen"])
    _store.set_preference("voice_first", current["voice_first"])
    return current
