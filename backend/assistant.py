import json
import os
from anthropic import Anthropic
from backend.tools import calendar as cal_tools
from backend.tools import tasks as task_tools

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """Eres Harvey, un asistente personal inteligente que habla en español.
Puedes escuchar, responder y ayudar con:
- Agendar y consultar eventos en Google Calendar
- Gestionar tareas pendientes (to-dos)
- Guardar notas y recordatorios
- Responder preguntas generales

Usa las herramientas disponibles cuando el usuario quiera agendar algo, agregar una tarea,
consultar su agenda, etc. Siempre responde de forma amigable y concisa en español.
Cuando uses una herramienta, confirma al usuario lo que hiciste de forma natural.
"""

TOOLS = [
    {
        "name": "create_calendar_event",
        "description": "Crea un evento en Google Calendar del usuario.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Título del evento"},
                "date": {"type": "string", "description": "Fecha en formato YYYY-MM-DD"},
                "time": {"type": "string", "description": "Hora en formato HH:MM (24h)"},
                "description": {"type": "string", "description": "Descripción opcional del evento"},
                "duration_minutes": {"type": "integer", "description": "Duración en minutos, por defecto 60"},
            },
            "required": ["title", "date", "time"],
        },
    },
    {
        "name": "list_calendar_events",
        "description": "Lista los próximos eventos del calendario del usuario.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days_ahead": {"type": "integer", "description": "Cuántos días hacia adelante buscar (por defecto 7)"},
            },
        },
    },
    {
        "name": "delete_calendar_event",
        "description": "Elimina un evento del Google Calendar por su ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "ID del evento a eliminar"},
            },
            "required": ["event_id"],
        },
    },
    {
        "name": "add_todo",
        "description": "Agrega una tarea pendiente a la lista de to-dos.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Descripción de la tarea"},
                "priority": {"type": "string", "enum": ["alta", "normal", "baja"], "description": "Prioridad de la tarea"},
            },
            "required": ["task"],
        },
    },
    {
        "name": "list_todos",
        "description": "Lista las tareas pendientes del usuario.",
        "input_schema": {
            "type": "object",
            "properties": {
                "only_pending": {"type": "boolean", "description": "Si es true, solo muestra las pendientes"},
            },
        },
    },
    {
        "name": "complete_todo",
        "description": "Marca una tarea como completada.",
        "input_schema": {
            "type": "object",
            "properties": {
                "todo_id": {"type": "integer", "description": "ID de la tarea a completar"},
            },
            "required": ["todo_id"],
        },
    },
    {
        "name": "add_note",
        "description": "Guarda una nota o recordatorio libre del usuario.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Contenido de la nota"},
            },
            "required": ["content"],
        },
    },
    {
        "name": "list_notes",
        "description": "Muestra las notas guardadas del usuario.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


def _run_tool(name: str, inputs: dict) -> str:
    try:
        if name == "create_calendar_event":
            result = cal_tools.create_event(**inputs)
        elif name == "list_calendar_events":
            result = cal_tools.list_events(**inputs)
        elif name == "delete_calendar_event":
            result = cal_tools.delete_event(**inputs)
        elif name == "add_todo":
            result = task_tools.add_todo(**inputs)
        elif name == "list_todos":
            result = task_tools.list_todos(**inputs)
        elif name == "complete_todo":
            result = task_tools.complete_todo(**inputs)
        elif name == "add_note":
            result = task_tools.add_note(**inputs)
        elif name == "list_notes":
            result = task_tools.list_notes()
        else:
            result = {"error": f"Herramienta desconocida: {name}"}
        return json.dumps(result, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def chat(messages: list[dict]) -> str:
    """Envía mensajes al asistente y retorna la respuesta de texto."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
    )

    while response.stop_reason == "tool_use":
        tool_results = []
        assistant_msg = {"role": "assistant", "content": response.content}

        for block in response.content:
            if block.type == "tool_use":
                result = _run_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages = messages + [assistant_msg, {"role": "user", "content": tool_results}]
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

    for block in response.content:
        if hasattr(block, "text"):
            return block.text
    return ""
