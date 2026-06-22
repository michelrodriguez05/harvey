from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    PRODUCTIVITY = "productivity"
    PROGRAMMER = "programmer"
    RESEARCHER = "researcher"
    TEACHER = "teacher"
    DESIGNER = "designer"
    AUTOMATION = "automation"


@dataclass
class Message:
    role: str
    content: str | list[dict[str, Any]]


@dataclass
class MemoryContext:
    user_name: str = ""
    preferences: dict[str, Any] = field(default_factory=dict)
    facts: list[dict[str, Any]] = field(default_factory=list)
    projects: list[dict[str, Any]] = field(default_factory=list)

    def to_prompt(self) -> str:
        lines = []
        if self.user_name:
            lines.append(f"Nombre del usuario: {self.user_name}")
        if self.preferences:
            lines.append(f"Preferencias: {self.preferences}")
        for fact in self.facts[:15]:
            lines.append(f"- [{fact.get('category', 'general')}] {fact['key']}: {fact['value']}")
        for project in self.projects[:5]:
            status = project.get("status", "activo")
            lines.append(f"- Proyecto ({status}): {project['name']} — {project.get('description', '')}")
        return "\n".join(lines) if lines else "Sin contexto de memoria previo."


@dataclass
class AgentResponse:
    text: str
    agent: str = "orchestrator"
    tools_used: list[str] = field(default_factory=list)
    youtube_video_id: str | None = None
    youtube_title: str | None = None
