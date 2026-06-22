import json
from collections.abc import Callable
from typing import Any


class ToolRegistry:
    """Central registry for assistant tools. Supports plugin-style registration."""

    def __init__(self) -> None:
        self._tools: list[dict[str, Any]] = []
        self._handlers: dict[str, Callable[[dict], Any]] = {}

    def register(self, name: str, description: str, schema: dict, handler: Callable[[dict], Any]) -> None:
        self._handlers[name] = handler
        self._tools.append({
            "name": name,
            "description": description,
            "input_schema": schema,
        })

    def get_tools(self) -> list[dict[str, Any]]:
        return list(self._tools)

    def run(self, name: str, inputs: dict) -> str:
        handler = self._handlers.get(name)
        if not handler:
            return json.dumps({"error": f"Herramienta desconocida: {name}"}, ensure_ascii=False)
        try:
            result = handler(inputs)
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)


registry = ToolRegistry()
