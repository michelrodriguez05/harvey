import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.database import init_db
from backend.tools.bootstrap import init_tools
from backend.plugins.loader import load_plugins
from backend.routers import auth, chat, agenda, memory, websocket, settings as settings_router

app = FastAPI(
    title="Yarbis Assistant",
    version="2.0.0",
    description="Asistente de voz inteligente con arquitectura de agentes",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", "http://localhost:5173"), "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Transcript", "X-Reply"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(agenda.router)
app.include_router(memory.router)
app.include_router(websocket.router)
app.include_router(settings_router.router)


@app.on_event("startup")
def startup():
    init_db()
    init_tools()
    loaded = load_plugins()
    if loaded:
        print(f"Plugins cargados: {', '.join(loaded)}")


@app.get("/")
def root():
    return {
        "message": "Yarbis Assistant API",
        "status": "running",
        "version": "2.0.0",
        "features": ["agents", "memory", "websocket", "plugins"],
    }


@app.get("/api/config")
def get_config():
    from backend.services.settings import get_assistant_settings
    from backend.services.conversation import get_llm_status
    s = get_assistant_settings()
    llm = get_llm_status()
    return {
        "assistant_name": s["assistant_name"],
        "wake_word": s["wake_word"],
        "user_name": s["user_name"],
        "always_listen": s["always_listen"],
        "voice_first": s["voice_first"],
        "llm_provider": llm["provider"],
        "llm_model": llm["model"],
        "llm_ready": llm["ok"],
    }
