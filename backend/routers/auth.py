import json
import os
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from backend.db.database import get_connection

router = APIRouter(prefix="/auth", tags=["auth"])

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _get_flow() -> Flow:
    return Flow.from_client_config(
        {
            "web": {
                "client_id": os.environ["GOOGLE_CLIENT_ID"],
                "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.environ["GOOGLE_REDIRECT_URI"]],
            }
        },
        scopes=SCOPES,
        redirect_uri=os.environ["GOOGLE_REDIRECT_URI"],
    )


@router.get("/google")
def google_login():
    """Inicia el flujo OAuth2 con Google."""
    flow = _get_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return RedirectResponse(auth_url)


@router.get("/google/callback")
def google_callback(code: str):
    """Recibe el callback de Google y guarda el token."""
    flow = _get_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    conn = get_connection()
    conn.execute(
        """
        INSERT INTO google_tokens (id, token, refresh_token, token_uri, client_id, client_secret, scopes)
        VALUES (1, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            token=excluded.token,
            refresh_token=excluded.refresh_token,
            updated_at=CURRENT_TIMESTAMP
        """,
        (
            creds.token,
            creds.refresh_token,
            creds.token_uri,
            creds.client_id,
            creds.client_secret,
            json.dumps(list(creds.scopes)),
        ),
    )
    conn.commit()
    conn.close()

    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    return RedirectResponse(f"{frontend_url}?google_connected=true")


@router.get("/google/status")
def google_status():
    """Verifica si Google Calendar está conectado."""
    conn = get_connection()
    row = conn.execute("SELECT id FROM google_tokens WHERE id = 1").fetchone()
    conn.close()
    return {"connected": row is not None}
