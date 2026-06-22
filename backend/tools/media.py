import re
import urllib.parse

import httpx

PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://pipedapi.adminforge.de",
    "https://api.piped.yt",
]

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
}


def _extract_video_id(url: str) -> str | None:
    if not url:
        return None
    match = re.search(r"(?:v=|/embed/|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None


def _search_via_piped(query: str) -> dict | None:
    for base in PIPED_INSTANCES:
        try:
            resp = httpx.get(
                f"{base}/search",
                params={"q": query, "filter": "videos"},
                timeout=8,
                headers=_HEADERS,
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])
            if not items:
                continue
            item = items[0]
            video_id = _extract_video_id(item.get("url", ""))
            if not video_id and item.get("url", "").startswith("/watch"):
                video_id = item["url"].split("v=")[-1][:11]
            if video_id:
                return {
                    "video_id": video_id,
                    "title": item.get("title", query),
                }
        except Exception:
            continue
    return None


def _search_via_youtube_html(query: str) -> dict | None:
    try:
        resp = httpx.get(
            "https://www.youtube.com/results",
            params={"search_query": query},
            headers=_HEADERS,
            timeout=10,
            follow_redirects=True,
        )
        resp.raise_for_status()
        ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', resp.text)
        titles = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"', resp.text)
        seen = set()
        for vid in ids:
            if vid in seen or vid in ("undefined",):
                continue
            seen.add(vid)
            title = titles[len(seen) - 1] if len(titles) >= len(seen) else query
            return {"video_id": vid, "title": title}
    except Exception:
        pass
    return None


def search_youtube(query: str) -> dict:
    query = (query or "").strip()
    if not query:
        return {"status": "error", "message": "No se indicó qué reproducir."}

    found = _search_via_piped(query) or _search_via_youtube_html(query)
    if found:
        vid = found["video_id"]
        return {
            "status": "ok",
            "action": "play_youtube",
            "query": query,
            "video_id": vid,
            "title": found.get("title", query),
            "url": f"https://www.youtube.com/watch?v={vid}",
            "embed_url": f"https://www.youtube.com/embed/{vid}?autoplay=1&rel=0",
        }

    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    return {
        "status": "partial",
        "action": "search_youtube",
        "query": query,
        "url": search_url,
        "message": "No encontré un video exacto, abre la búsqueda.",
    }


def play_youtube(query: str) -> dict:
    """Busca un video y devuelve datos para reproducción automática en el frontend."""
    return search_youtube(query)


def control_media(action: str, query: str = "") -> dict:
    action = (action or "play").lower()
    if action in ("play", "search", "reproducir", "buscar"):
        return play_youtube(query)
    return {
        "status": "not_implemented",
        "message": f"La acción '{action}' aún no está disponible. Usa play o search.",
    }
