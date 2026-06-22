import json
from typing import Any

from backend.core.config import settings
from backend.core.types import MemoryContext
from backend.db.database import get_connection


class MemoryStore:
    """Persistent memory: profile, facts, projects, conversations."""

    def get_context(self) -> MemoryContext:
        conn = get_connection()
        profile = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
        facts = conn.execute(
            "SELECT key, value, category FROM memory_facts ORDER BY importance DESC, updated_at DESC LIMIT 20"
        ).fetchall()
        projects = conn.execute(
            "SELECT name, description, status, context FROM projects WHERE status != 'archived' ORDER BY updated_at DESC LIMIT 10"
        ).fetchall()
        conn.close()

        if profile:
            prefs = json.loads(profile["preferences"] or "{}")
            user_name = profile["name"] or settings.user_name
        else:
            prefs = {}
            user_name = settings.user_name

        return MemoryContext(
            user_name=user_name,
            preferences=prefs,
            facts=[dict(f) for f in facts],
            projects=[{**dict(p), "context": json.loads(p["context"] or "{}")} for p in projects],
        )

    def set_user_name(self, name: str) -> None:
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO user_profile (id, name, preferences)
            VALUES (1, ?, COALESCE((SELECT preferences FROM user_profile WHERE id = 1), '{}'))
            ON CONFLICT(id) DO UPDATE SET name = excluded.name, updated_at = CURRENT_TIMESTAMP
            """,
            (name,),
        )
        conn.commit()
        conn.close()

    def set_preference(self, key: str, value: Any) -> None:
        ctx = self.get_context()
        ctx.preferences[key] = value
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO user_profile (id, name, preferences)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET preferences = excluded.preferences, updated_at = CURRENT_TIMESTAMP
            """,
            (ctx.user_name, json.dumps(ctx.preferences, ensure_ascii=False)),
        )
        conn.commit()
        conn.close()

    def remember(self, key: str, value: str, category: str = "general", importance: int = 5) -> dict:
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO memory_facts (key, value, category, importance)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                category = excluded.category,
                importance = excluded.importance,
                updated_at = CURRENT_TIMESTAMP
            """,
            (key, value, category, importance),
        )
        conn.commit()
        conn.close()
        return {"key": key, "value": value, "category": category}

    def list_facts(self, category: str | None = None) -> list[dict]:
        conn = get_connection()
        if category:
            rows = conn.execute(
                "SELECT key, value, category, importance, updated_at FROM memory_facts WHERE category = ? ORDER BY importance DESC",
                (category,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT key, value, category, importance, updated_at FROM memory_facts ORDER BY importance DESC, updated_at DESC"
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def forget(self, key: str) -> bool:
        conn = get_connection()
        cur = conn.execute("DELETE FROM memory_facts WHERE key = ?", (key,))
        conn.commit()
        conn.close()
        return cur.rowcount > 0

    def upsert_project(self, name: str, description: str = "", context: dict | None = None, status: str = "active") -> dict:
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO projects (name, description, context, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                description = excluded.description,
                context = excluded.context,
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
            """,
            (name, description, json.dumps(context or {}, ensure_ascii=False), status),
        )
        conn.commit()
        conn.close()
        return {"name": name, "description": description, "status": status}

    def list_projects(self) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT name, description, status, context, updated_at FROM projects ORDER BY updated_at DESC"
        ).fetchall()
        conn.close()
        return [{**dict(r), "context": json.loads(r["context"] or "{}")} for r in rows]

    def create_session(self) -> int:
        conn = get_connection()
        cur = conn.execute("INSERT INTO conversation_sessions DEFAULT VALUES")
        session_id = cur.lastrowid
        conn.commit()
        conn.close()
        return session_id

    def save_message(self, session_id: int, role: str, content: str, agent: str = "orchestrator") -> None:
        conn = get_connection()
        conn.execute(
            "INSERT INTO conversation_messages (session_id, role, content, agent) VALUES (?, ?, ?, ?)",
            (session_id, role, content, agent),
        )
        conn.commit()
        conn.close()

    def get_session_messages(self, session_id: int, limit: int = 40) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT role, content, agent, created_at FROM conversation_messages
            WHERE session_id = ? ORDER BY id DESC LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in reversed(rows)]

    def get_recent_sessions(self, limit: int = 10) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT s.id, s.created_at,
                   (SELECT content FROM conversation_messages WHERE session_id = s.id AND role = 'user' ORDER BY id LIMIT 1) as preview
            FROM conversation_sessions s ORDER BY s.created_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
