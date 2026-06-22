import io
import tempfile
from pathlib import Path

import speech_recognition as sr


def _webm_to_wav(audio_bytes: bytes, content_type: str) -> bytes:
    """Intenta convertir webm/ogg a wav usando pydub si está disponible."""
    try:
        from pydub import AudioSegment

        fmt = "webm" if "webm" in content_type else "ogg"
        segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format=fmt)
        segment = segment.set_frame_rate(16000).set_channels(1)
        out = io.BytesIO()
        segment.export(out, format="wav")
        return out.getvalue()
    except Exception:
        raise RuntimeError(
            "No se pudo convertir el audio. El navegador debe enviar WAV o instala ffmpeg para soporte webm."
        )


def transcribe_audio_file(audio_bytes: bytes, content_type: str = "audio/webm") -> str:
    """Transcribe audio bytes usando Google Speech Recognition (gratis, sin API key)."""
    recognizer = sr.Recognizer()

    if "wav" in content_type:
        wav_bytes = audio_bytes
    elif "webm" in content_type or "ogg" in content_type:
        wav_bytes = _webm_to_wav(audio_bytes, content_type)
    else:
        wav_bytes = audio_bytes

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(wav_bytes)
        tmp_path = tmp.name

    try:
        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)

        try:
            return recognizer.recognize_google(audio, language="es-CO")
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            raise RuntimeError(f"Error en el servicio de reconocimiento de voz: {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


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
