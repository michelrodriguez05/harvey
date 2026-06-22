from typing import Any

import httpx

from backend.core.config import settings
from backend.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    supports_tools = False

    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.llm_model or "llama3.2"

    def chat(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        ollama_messages = [{"role": "system", "content": system}]
        for msg in messages:
            content = msg.get("content")
            if isinstance(content, str):
                ollama_messages.append({"role": msg["role"], "content": content})

        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={"model": self.model, "messages": ollama_messages, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()

    def extract_text(self, response: dict[str, Any]) -> str:
        return response.get("message", {}).get("content", "")

    def is_tool_use(self, response: Any) -> bool:
        return False

    def get_tool_calls(self, response: Any) -> list[dict[str, Any]]:
        return []

    def format_assistant_message(self, response: Any) -> dict[str, Any]:
        return {"role": "assistant", "content": self.extract_text(response)}

    def format_tool_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        return {"role": "user", "content": str(results)}
