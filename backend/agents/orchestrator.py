import json

from backend.agents.base import BaseAgent
from backend.agents.specialists import ALL_AGENTS
from backend.core.config import settings
from backend.core.types import AgentResponse, MemoryContext
from backend.llm.factory import get_provider
from backend.tools.registry import registry


class Orchestrator:
    """Central coordinator: routes context to specialized agents via unified LLM loop."""

    def __init__(self, agents: list[BaseAgent] | None = None) -> None:
        self.agents = agents or ALL_AGENTS
        self.llm = get_provider()

    def _build_system_prompt(
        self, memory: MemoryContext, active_agent: BaseAgent | None = None, assistant_name: str | None = None, wake_word: str | None = None
    ) -> str:
        name = assistant_name or settings.assistant_name
        wake = wake_word or settings.wake_word
        agent_lines = "\n".join(f"- {a.name}: {a.description}" for a in self.agents)
        sections = "\n".join(a.system_section(memory) for a in self.agents)

        focus = ""
        if active_agent:
            focus = f"\nEl mensaje parece dirigido al agente **{active_agent.name}**. Prioriza sus capacidades.\n"

        return f"""Eres {name}, un asistente virtual de nueva generación inspirado en Jarvis.
Hablas en español de forma natural, profesional y cercana.
La palabra de activación es "{wake}".

## Memoria del usuario
{memory.to_prompt()}

## Agentes especializados disponibles
{agent_lines}
{focus}
## Instrucciones por agente
{sections}

## Reglas generales
- Saluda al usuario por su nombre cuando sea apropiado.
- Usa herramientas cuando el usuario pida acciones concretas.
- Guarda en memoria hechos importantes (preferencias, proyectos, objetivos).
- Si una capacidad aún no está implementada, explica con claridad qué puedes hacer hoy.
- Responde de forma concisa en voz; evita listas largas salvo que se pidan.
- Mantén contexto de la conversación y proyectos activos.
- Para reproducir música, USA la herramienta play_youtube. No digas que reprodujiste algo si no llamaste la herramienta.
- Si una herramienta falla, dilo con honestidad.
"""

    def _detect_agent(self, message: str) -> BaseAgent | None:
        lower = message.lower()
        best: BaseAgent | None = None
        best_score = 0
        for agent in self.agents:
            score = sum(1 for kw in agent.keywords() if kw in lower)
            if score > best_score:
                best_score = score
                best = agent
        return best if best_score > 0 else None

    def process(self, messages: list[dict], memory: MemoryContext, assistant_name: str | None = None, wake_word: str | None = None) -> AgentResponse:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        active = self._detect_agent(last_user) if isinstance(last_user, str) else None
        system = self._build_system_prompt(memory, active, assistant_name, wake_word)
        tools = registry.get_tools() if self.llm.supports_tools else None
        tools_used: list[str] = []
        youtube_video_id: str | None = None
        youtube_title: str | None = None

        response = self.llm.chat(messages, system, tools=tools)

        while tools and self.llm.is_tool_use(response):
            tool_results = []
            for call in self.llm.get_tool_calls(response):
                tools_used.append(call["name"])
                raw = registry.run(call["name"], call["input"])
                if call["name"] in ("play_youtube", "control_media"):
                    try:
                        data = json.loads(raw)
                        if data.get("video_id"):
                            youtube_video_id = data["video_id"]
                            youtube_title = data.get("title")
                    except json.JSONDecodeError:
                        pass
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": call["id"],
                    "content": raw,
                })

            tool_msgs = self.llm.format_tool_results(tool_results)
            if isinstance(tool_msgs, list):
                messages = messages + [self.llm.format_assistant_message(response)] + tool_msgs
            else:
                messages = messages + [
                    self.llm.format_assistant_message(response),
                    tool_msgs,
                ]
            response = self.llm.chat(messages, system, tools=tools)

        text = self.llm.extract_text(response)
        agent_name = active.name if active else "orchestrator"
        return AgentResponse(
            text=text,
            agent=agent_name,
            tools_used=tools_used,
            youtube_video_id=youtube_video_id,
            youtube_title=youtube_title,
        )
