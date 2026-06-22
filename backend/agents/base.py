from abc import ABC, abstractmethod

from backend.core.types import AgentRole, MemoryContext


class BaseAgent(ABC):
    role: AgentRole
    name: str
    description: str

    @abstractmethod
    def system_section(self, memory: MemoryContext) -> str:
        """Agent-specific instructions appended to the orchestrator prompt."""

    def keywords(self) -> list[str]:
        return []
