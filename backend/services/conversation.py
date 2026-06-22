import httpx

from backend.agents.orchestrator import Orchestrator
from backend.core.config import settings
from backend.memory.store import MemoryStore
import os


def format_user_error(exc: Exception) -> str:
    msg = str(exc)
    lower = msg.lower()
    if "authentication" in lower or "api-key" in lower or "x-api-key" in lower:
        if settings.llm_provider == "groq":
            return "API key de Groq inválida. Obtén una gratis en console.groq.com y ponla en GROQ_API_KEY."
        return (
            "API key de Anthropic inválida. Abre tu archivo .env, coloca una clave real en "
            "ANTHROPIC_API_KEY (desde console.anthropic.com) y reinicia el backend."
        )
    if "credit balance" in lower or "billing" in lower or "purchase credits" in lower:
        return (
            "Tu cuenta de Anthropic no tiene créditos suficientes. "
            "Cambia a LLM_PROVIDER=groq u ollama en .env, o agrega saldo en Anthropic."
        )
    if "connection refused" in lower or "connect" in lower and settings.llm_provider == "ollama":
        return "Ollama no está corriendo. Instálalo desde ollama.com, ejecuta 'ollama pull llama3.2' y reinicia."
    if "pcm wav" in lower or "audio file could not be read" in lower:
        return "Error al procesar el audio. Intenta de nuevo o escribe tu mensaje."
    return msg


def get_llm_status() -> dict:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)

    provider = os.environ.get("LLM_PROVIDER", settings.llm_provider).lower()

    if provider == "anthropic":
        key = settings.anthropic_api_key
        ok = bool(key and key.startswith("sk-ant-") and len(key) > 30 and "your_anthropic" not in key)
        return {
            "ok": ok,
            "provider": provider,
            "model": settings.llm_model,
            "message": None if ok else "Configura ANTHROPIC_API_KEY en .env",
        }

    if provider == "groq":
        key = os.environ.get("GROQ_API_KEY", "")
        ok = bool(key and len(key) > 20 and "your_groq" not in key)
        return {
            "ok": ok,
            "provider": provider,
            "model": os.environ.get("LLM_MODEL", "llama-3.1-8b-instant"),
            "message": None if ok else "Obtén una API key gratis en console.groq.com y ponla en GROQ_API_KEY",
        }

    if provider == "ollama":
        try:
            resp = httpx.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags", timeout=3)
            ok = resp.status_code == 200
            models = [m["name"] for m in resp.json().get("models", [])] if ok else []
            return {
                "ok": ok,
                "provider": provider,
                "model": settings.llm_model or "llama3.2",
                "message": None if ok else "Instala Ollama desde ollama.com",
                "models_available": models[:5],
            }
        except Exception:
            return {
                "ok": False,
                "provider": provider,
                "model": settings.llm_model or "llama3.2",
                "message": "Ollama no está corriendo. Instálalo y ejecuta: ollama pull llama3.2",
            }

    return {"ok": False, "provider": provider, "model": settings.llm_model, "message": f"Proveedor desconocido: {provider}"}


def is_api_key_valid() -> bool:
    return get_llm_status()["ok"]


class ConversationService:
    def __init__(self) -> None:
        self.memory = MemoryStore()
        self.orchestrator = Orchestrator()
        self._sessions: dict[str, dict] = {}
        self._default_session = "default"

    def _get_session(self, session_id: str | None = None) -> dict:
        sid = session_id or self._default_session
        if sid not in self._sessions:
            db_id = self.memory.create_session()
            self._sessions[sid] = {"db_id": db_id, "messages": []}
        return self._sessions[sid]

    def get_messages(self, session_id: str | None = None) -> list[dict]:
        return self._get_session(session_id)["messages"]

    def clear(self, session_id: str | None = None) -> None:
        sid = session_id or self._default_session
        self._sessions[sid] = {"db_id": self.memory.create_session(), "messages": []}

    def chat(self, user_message: str, session_id: str | None = None) -> dict:
        status = get_llm_status()
        if not status["ok"]:
            raise ValueError(status["message"] or "LLM no configurado")

        session = self._get_session(session_id)
        messages = session["messages"]
        messages.append({"role": "user", "content": user_message})
        self.memory.save_message(session["db_id"], "user", user_message)

        memory_ctx = self.memory.get_context()
        from backend.services.settings import get_assistant_settings
        ast = get_assistant_settings()
        if not memory_ctx.user_name and ast["user_name"]:
            self.memory.set_user_name(ast["user_name"])
            memory_ctx = self.memory.get_context()

        result = self.orchestrator.process(
            messages, memory_ctx,
            assistant_name=ast["assistant_name"],
            wake_word=ast["wake_word"],
        )
        messages.append({"role": "assistant", "content": result.text})
        self.memory.save_message(session["db_id"], "assistant", result.text, result.agent)

        if len(messages) > settings.max_history:
            session["messages"] = messages[-settings.max_history :]

        return {
            "reply": result.text,
            "agent": result.agent,
            "tools_used": result.tools_used,
            "youtube_video_id": result.youtube_video_id,
            "youtube_title": result.youtube_title,
        }


conversation_service = ConversationService()
