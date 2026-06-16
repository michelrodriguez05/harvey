import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from backend.db.database import get_connection

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _get_credentials() -> Credentials | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM google_tokens WHERE id = 1").fetchone()
    conn.close()
    if not row:
        return None
    return Credentials(
        token=row["token"],
        refresh_token=row["refresh_token"],
        token_uri=row["token_uri"],
        client_id=row["client_id"],
        client_secret=row["client_secret"],
        scopes=json.loads(row["scopes"]),
    )


def _get_service():
    creds = _get_credentials()
    if not creds:
        raise ValueError("Google Calendar no está conectado. Ve a /auth/google para autorizar.")
    return build("calendar", "v3", credentials=creds)


def create_event(title: str, date: str, time: str, description: str = "", duration_minutes: int = 60) -> dict:
    """Crea un evento en Google Calendar."""
    service = _get_service()
    start_dt = datetime.fromisoformat(f"{date}T{time}:00")
    end_dt = start_dt + timedelta(minutes=duration_minutes)

    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "America/Bogota"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "America/Bogota"},
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 15},
            ],
        },
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    return {
        "id": created["id"],
        "title": title,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "link": created.get("htmlLink"),
    }


def list_events(days_ahead: int = 7) -> list[dict]:
    """Lista eventos de los próximos N días."""
    service = _get_service()
    now = datetime.utcnow().isoformat() + "Z"
    until = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            timeMax=until,
            maxResults=20,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = []
    for e in result.get("items", []):
        start = e["start"].get("dateTime", e["start"].get("date"))
        events.append({"id": e["id"], "title": e["summary"], "start": start, "description": e.get("description", "")})
    return events


def delete_event(event_id: str) -> dict:
    """Elimina un evento de Google Calendar."""
    service = _get_service()
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return {"deleted": True, "event_id": event_id}
