import io
import tempfile
import speech_recognition as sr


def transcribe_audio_file(audio_bytes: bytes, content_type: str = "audio/webm") -> str:
    """Transcribe audio bytes usando Google Speech Recognition (gratis, sin API key)."""
    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    with sr.AudioFile(tmp_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language="es-CO")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        raise RuntimeError(f"Error en el servicio de reconocimiento de voz: {e}")


def transcribe_microphone() -> str:
    """Escucha el micrófono del servidor y transcribe (para uso en CLI local)."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)

    try:
        return recognizer.recognize_google(audio, language="es-CO")
    except sr.UnknownValueError:
        return ""
