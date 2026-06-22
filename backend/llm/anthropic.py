from typing import Any

from anthropic import Anthropic

from backend.core.config import settings
from backend.llm.base import LLMProvider


class AnthropicProvider(LLMProvider):
    supports_tools = True

    def __init__(self) -> None:
        self._client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.llm_model

    def chat(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 1024,
    ) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
        return self._client.messages.create(**kwargs)

    def extract_text(self, response: Any) -> str:
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return ""

    def is_tool_use(self, response: Any) -> bool:
        return response.stop_reason == "tool_use"

    def get_tool_calls(self, response: Any) -> list[dict[str, Any]]:
        return [
            {"id": block.id, "name": block.name, "input": block.input}
            for block in response.content
            if block.type == "tool_use"
        ]

    def format_assistant_message(self, response: Any) -> dict[str, Any]:
        return {"role": "assistant", "content": response.content}

    def format_tool_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        return {"role": "user", "content": results}


