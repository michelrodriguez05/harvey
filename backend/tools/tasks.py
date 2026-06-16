from datetime import datetime
from backend.db.database import get_connection


def add_todo(task: str, priority: str = "normal") -> dict:
    """Agrega una tarea pendiente."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO todos (task, priority) VALUES (?, ?)", (task, priority)
    )
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()
    return {"id": todo_id, "task": task, "priority": priority, "completed": False}


def list_todos(only_pending: bool = True) -> list[dict]:
    """Lista las tareas pendientes o todas."""
    conn = get_connection()
    if only_pending:
        rows = conn.execute(
            "SELECT * FROM todos WHERE completed = 0 ORDER BY priority DESC, created_at ASC"
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM todos ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def complete_todo(todo_id: int) -> dict:
    """Marca una tarea como completada."""
    conn = get_connection()
    conn.execute(
        "UPDATE todos SET completed = 1, completed_at = ? WHERE id = ?",
        (datetime.now().isoformat(), todo_id),
    )
    conn.commit()
    conn.close()
    return {"id": todo_id, "completed": True}


def delete_todo(todo_id: int) -> dict:
    """Elimina una tarea."""
    conn = get_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    return {"deleted": True, "id": todo_id}


def add_note(content: str) -> dict:
    """Guarda una nota libre."""
    conn = get_connection()
    cursor = conn.execute("INSERT INTO notes (content) VALUES (?)", (content,))
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return {"id": note_id, "content": content}


def list_notes() -> list[dict]:
    """Lista todas las notas guardadas."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM notes ORDER BY created_at DESC LIMIT 20").fetchall()
    conn.close()
    return [dict(r) for r in rows]
