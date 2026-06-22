import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


@dataclass(frozen=True)
class Settings:
    assistant_name: str = os.environ.get("ASSISTANT_NAME", "Yarbis")
    wake_word: str = os.environ.get("WAKE_WORD", "Yarbis")
    user_name: str = os.environ.get("USER_NAME", "Michel")
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    groq_api_key: str = os.environ.get("GROQ_API_KEY", "")
    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    llm_model: str = os.environ.get("LLM_MODEL", "claude-sonnet-4-6")
    llm_provider: str = os.environ.get("LLM_PROVIDER", "anthropic")
    frontend_url: str = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    timezone: str = os.environ.get("TIMEZONE", "America/Bogota")
    max_history: int = int(os.environ.get("MAX_HISTORY", "40"))
    plugins_dir: str = os.environ.get("PLUGINS_DIR", "backend/plugins")


settings = Settings()
