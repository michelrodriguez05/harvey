import json
import os
from typing import Any

import httpx

from backend.core.config import settings
from backend.llm.base import LLMProvider
from backend.llm.tool_utils import to_openai_tools


class GroqProvider(LLMProvider):
    supports_tools = True

    def __init__(self) -> None:
        self.model = settings.llm_model or "llama-3.1-8b-instant"

    def _api_key(self) -> str:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        return os.environ.get("GROQ_API_KEY", settings.groq_api_key)

    def chat(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        api_messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
        for msg in messages:
            api_messages.append(msg)

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": api_messages,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = to_openai_tools(tools)
            payload["tool_choice"] = "auto"

        response = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {self._api_key()}", "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def extract_text(self, response: dict[str, Any]) -> str:
        message = response["choices"][0]["message"]
        return message.get("content") or ""

    def is_tool_use(self, response: Any) -> bool:
        message = response["choices"][0]["message"]
        return bool(message.get("tool_calls"))

    def get_tool_calls(self, response: Any) -> list[dict[str, Any]]:
        message = response["choices"][0]["message"]
        calls = []
        for tc in message.get("tool_calls", []):
            args = tc["function"].get("arguments", "{}")
            if isinstance(args, str):
                args = json.loads(args)
            calls.append({
                "id": tc["id"],
                "name": tc["function"]["name"],
                "input": args,
            })
        return calls

    def format_assistant_message(self, response: Any) -> dict[str, Any]:
        return response["choices"][0]["message"]

    def format_tool_results(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "role": "tool",
                "tool_call_id": r["tool_use_id"],
                "content": r["content"] if isinstance(r["content"], str) else json.dumps(r["content"]),
            }
            for r in results
        ]
