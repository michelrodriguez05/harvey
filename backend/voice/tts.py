import io
import tempfile
import subprocess
from pathlib import Path


def text_to_speech_bytes(text: str, lang: str = "es") -> bytes:
    """Convierte texto a audio MP3 usando gTTS (Google Text-to-Speech, gratis)."""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except ImportError:
        raise RuntimeError("Instala gTTS: pip install gtts")


def speak_text(text: str, lang: str = "es"):
    """Reproduce texto en voz alta en el servidor (para uso local/CLI)."""
    import pyttsx3
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    for v in voices:
        if "spanish" in v.name.lower() or "es" in v.id.lower():
            engine.setProperty("voice", v.id)
            break
    engine.setProperty("rate", 165)
    engine.say(text)
    engine.runAndWait()
