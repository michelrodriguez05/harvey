from backend.tools import calendar as cal_tools
from backend.tools import tasks as task_tools
from backend.tools import media as media_tools
from backend.tools.registry import registry
from backend.memory.store import MemoryStore

_memory = MemoryStore()


def register_productivity_tools() -> None:
    registry.register(
        "create_calendar_event",
        "Crea un evento en Google Calendar del usuario.",
        {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "time": {"type": "string", "description": "HH:MM 24h"},
                "description": {"type": "string"},
                "duration_minutes": {"type": "integer"},
            },
            "required": ["title", "date", "time"],
        },
        lambda i: cal_tools.create_event(**i),
    )
    registry.register(
        "list_calendar_events",
        "Lista los próximos eventos del calendario.",
        {"type": "object", "properties": {"days_ahead": {"type": "integer"}}},
        lambda i: cal_tools.list_events(**i),
    )
    registry.register(
        "delete_calendar_event",
        "Elimina un evento del calendario por ID.",
        {"type": "object", "properties": {"event_id": {"type": "string"}}, "required": ["event_id"]},
        lambda i: cal_tools.delete_event(**i),
    )
    registry.register(
        "add_todo",
        "Agrega una tarea pendiente.",
        {
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "priority": {"type": "string", "enum": ["alta", "normal", "baja"]},
            },
            "required": ["task"],
        },
        lambda i: task_tools.add_todo(**i),
    )
    registry.register(
        "list_todos",
        "Lista tareas pendientes.",
        {"type": "object", "properties": {"only_pending": {"type": "boolean"}}},
        lambda i: task_tools.list_todos(**i),
    )
    registry.register(
        "complete_todo",
        "Marca una tarea como completada.",
        {"type": "object", "properties": {"todo_id": {"type": "integer"}}, "required": ["todo_id"]},
        lambda i: task_tools.complete_todo(**i),
    )
    registry.register(
        "add_note",
        "Guarda una nota o recordatorio.",
        {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]},
        lambda i: task_tools.add_note(**i),
    )
    registry.register(
        "list_notes",
        "Muestra notas guardadas.",
        {"type": "object", "properties": {}},
        lambda _: task_tools.list_notes(),
    )


def register_memory_tools() -> None:
    registry.register(
        "remember_fact",
        "Guarda un hecho importante en la memoria a largo plazo del asistente.",
        {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "value": {"type": "string"},
                "category": {"type": "string", "description": "general, preferencia, proyecto, objetivo"},
                "importance": {"type": "integer", "description": "1-10"},
            },
            "required": ["key", "value"],
        },
        lambda i: _memory.remember(
            i["key"], i["value"], i.get("category", "general"), i.get("importance", 5)
        ),
    )
    registry.register(
        "recall_facts",
        "Recupera hechos guardados en memoria.",
        {"type": "object", "properties": {"category": {"type": "string"}}},
        lambda i: {"facts": _memory.list_facts(i.get("category"))},
    )
    registry.register(
        "save_project",
        "Guarda o actualiza un proyecto activo del usuario.",
        {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string", "enum": ["active", "paused", "archived"]},
            },
            "required": ["name"],
        },
        lambda i: _memory.upsert_project(i["name"], i.get("description", ""), status=i.get("status", "active")),
    )
    registry.register(
        "list_projects",
        "Lista proyectos del usuario.",
        {"type": "object", "properties": {}},
        lambda _: {"projects": _memory.list_projects()},
    )
    registry.register(
        "set_user_name",
        "Actualiza el nombre del usuario en memoria.",
        {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
        lambda i: (_memory.set_user_name(i["name"]), {"name": i["name"]})[1],
    )


def register_media_tools() -> None:
    registry.register(
        "play_youtube",
        "Busca y reproduce un video o canción en YouTube. Abre el navegador del usuario.",
        {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Canción, artista o video a buscar"},
            },
            "required": ["query"],
        },
        lambda i: media_tools.play_youtube(i["query"]),
    )
    registry.register(
        "control_media",
        "Controla multimedia. Acciones: play, search (YouTube).",
        {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "play, search, pause"},
                "query": {"type": "string", "description": "Canción o video"},
            },
            "required": ["action"],
        },
        lambda i: media_tools.control_media(i["action"], i.get("query", "")),
    )


def register_stub_tools() -> None:
    """Placeholder tools for future agents — return informative stubs."""

    def _stub(feature: str):
        return lambda _: {
            "status": "not_implemented",
            "message": f"La capacidad '{feature}' está preparada en la arquitectura y se activará en una próxima fase.",
        }

    stubs = [
        ("search_web", "Busca información en Internet.", {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}, "búsqueda web"),
        ("run_code", "Ejecuta o genera código en un proyecto.", {"type": "object", "properties": {"instruction": {"type": "string"}}, "required": ["instruction"]}, "programador"),
        ("open_application", "Abre una aplicación en el sistema.", {"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"]}, "automatización"),
        ("send_message", "Envía un mensaje por Gmail, Telegram o WhatsApp.", {"type": "object", "properties": {"channel": {"type": "string"}, "to": {"type": "string"}, "body": {"type": "string"}}, "required": ["channel", "body"]}, "comunicación"),
        ("analyze_image", "Analiza una imagen o captura de pantalla.", {"type": "object", "properties": {"description": {"type": "string"}}, "required": ["description"]}, "visión artificial"),
    ]
    for name, desc, schema, feature in stubs:
        registry.register(name, desc, schema, _stub(feature))


def init_tools() -> None:
    register_productivity_tools()
    register_memory_tools()
    register_media_tools()
    register_stub_tools()
