from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    supports_tools: bool = True

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 1024,
    ) -> Any:
        pass

    @abstractmethod
    def extract_text(self, response: Any) -> str:
        pass

    @abstractmethod
    def is_tool_use(self, response: Any) -> bool:
        pass

    @abstractmethod
    def get_tool_calls(self, response: Any) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def format_assistant_message(self, response: Any) -> dict[str, Any]:
        pass

    @abstractmethod
    def format_tool_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        pass
