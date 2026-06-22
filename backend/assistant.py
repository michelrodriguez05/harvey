"""Backward-compatible entry point."""

from backend.services.conversation import conversation_service


def chat(messages: list[dict]) -> str:
    if not messages or messages[-1]["role"] != "user":
        return ""
    session = conversation_service._get_session()
    session["messages"] = list(messages[:-1])
    return conversation_service.chat(messages[-1]["content"])["reply"]
