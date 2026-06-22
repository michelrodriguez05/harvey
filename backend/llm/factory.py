from backend.core.config import settings
from backend.llm.base import LLMProvider


def get_provider() -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "anthropic":
        from backend.llm.anthropic import AnthropicProvider
        return AnthropicProvider()
    if provider == "groq":
        from backend.llm.groq import GroqProvider
        return GroqProvider()
    if provider == "ollama":
        from backend.llm.ollama import OllamaProvider
        return OllamaProvider()
    raise ValueError(f"Proveedor LLM no soportado: {provider}. Usa: anthropic, groq, ollama")
