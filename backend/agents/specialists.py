from backend.agents.base import BaseAgent
from backend.core.types import AgentRole, MemoryContext


class ProductivityAgent(BaseAgent):
    role = AgentRole.PRODUCTIVITY
    name = "productividad"
    description = "Gestiona calendario, tareas, notas, recordatorios y agenda."

    def system_section(self, memory: MemoryContext) -> str:
        return (
            "AGENTE PRODUCTIVIDAD: Usa herramientas de calendario, todos y notas. "
            "Confirma acciones de forma natural y proactiva."
        )

    def keywords(self) -> list[str]:
        return ["agenda", "calendario", "tarea", "recordatorio", "reunión", "evento", "nota", "alarma"]


class ProgrammerAgent(BaseAgent):
    role = AgentRole.PROGRAMMER
    name = "programador"
    description = "Genera código, explica errores, analiza proyectos y trabaja con repositorios."

    def system_section(self, memory: MemoryContext) -> str:
        return (
            "AGENTE PROGRAMADOR: Experto en Python, JavaScript, React y APIs. "
            "Genera código limpio, explica errores y sugiere arquitectura."
        )

    def keywords(self) -> list[str]:
        return ["código", "programar", "react", "python", "bug", "error", "github", "api", "componente"]


class ResearcherAgent(BaseAgent):
    role = AgentRole.RESEARCHER
    name = "investigador"
    description = "Busca información, resume artículos y compara alternativas."

    def system_section(self, memory: MemoryContext) -> str:
        return "AGENTE INVESTIGADOR: Busca información actualizada y resume hallazgos con fuentes."

    def keywords(self) -> list[str]:
        return ["busca", "investiga", "información", "artículo", "comparar", "resumen"]


class TeacherAgent(BaseAgent):
    role = AgentRole.TEACHER
    name = "profesor"
    description = "Explica conceptos paso a paso de forma didáctica."

    def system_section(self, memory: MemoryContext) -> str:
        return "AGENTE PROFESOR: Explica con claridad, ejemplos y pasos progresivos."

    def keywords(self) -> list[str]:
        return ["explica", "enseña", "cómo funciona", "aprender", "tutorial"]


class DesignerAgent(BaseAgent):
    role = AgentRole.DESIGNER
    name = "diseñador"
    description = "Experto en HTML, CSS, UX/UI y diseño de interfaces."

    def system_section(self, memory: MemoryContext) -> str:
        return "AGENTE DISEÑADOR: Propone interfaces modernas, accesibles y coherentes."

    def keywords(self) -> list[str]:
        return ["diseño", "ui", "ux", "interfaz", "css", "layout", "estilo"]


class AutomationAgent(BaseAgent):
    role = AgentRole.AUTOMATION
    name = "automatización"
    description = "Ejecuta acciones en el sistema: abrir apps, scripts, archivos."

    def system_section(self, memory: MemoryContext) -> str:
        return "AGENTE AUTOMATIZACIÓN: Ejecuta acciones del sistema de forma segura y confirmada."

    def keywords(self) -> list[str]:
        return ["abre", "ejecuta", "script", "archivo", "carpeta", "captura", "automatiza", "reproduce", "pon", "música", "canción", "youtube", "spotify"]


ALL_AGENTS: list[BaseAgent] = [
    ProductivityAgent(),
    ProgrammerAgent(),
    ResearcherAgent(),
    TeacherAgent(),
    DesignerAgent(),
    AutomationAgent(),
]
