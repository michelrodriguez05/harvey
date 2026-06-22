import { useState, useRef, useCallback } from "react";
import axios from "axios";
import { audioBlobToWav, createSpeechRecognition } from "./audioUtils";

export function useVoice({ onTranscript, onReply, onAudioBlob, useWebSocket = false, connected = false, onError }) {
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const recognitionRef = useRef(null);
  const useBrowserSttRef = useRef(!!createSpeechRecognition());

  const sendViaHttp = async (textOrBlob, isText = false) => {
    setProcessing(true);
    try {
      if (isText) {
        const res = await axios.post("/api/chat", { message: textOrBlob });
        onTranscript?.(textOrBlob);
        onReply?.(res.data.reply, res.data.agent);
        const speakRes = await axios.post("/api/voice/speak", { message: res.data.reply }, { responseType: "arraybuffer" });
        const audioCtx = new AudioContext();
        const decoded = await audioCtx.decodeAudioData(speakRes.data);
        const source = audioCtx.createBufferSource();
        source.buffer = decoded;
        source.connect(audioCtx.destination);
        source.start();
        return;
      }

      const wavBlob = await audioBlobToWav(textOrBlob);
      const formData = new FormData();
      formData.append("audio", wavBlob, "recording.wav");

      const res = await axios.post("/api/voice/chat", formData, { responseType: "arraybuffer" });
      const transcript = res.headers["x-transcript"];
      const reply = res.headers["x-reply"];

      if (transcript) onTranscript?.(transcript);
      if (reply) onReply?.(reply);

      const audioCtx = new AudioContext();
      const decoded = await audioCtx.decodeAudioData(res.data);
      const source = audioCtx.createBufferSource();
      source.buffer = decoded;
      source.connect(audioCtx.destination);
      source.start();
    } catch (err) {
      const detail = err.response?.data?.detail || err.message;
      onError?.(typeof detail === "string" ? detail : "Error en voz");
    } finally {
      setProcessing(false);
    }
  };

  const startBrowserRecognition = useCallback(() => {
    const recognition = createSpeechRecognition();
    if (!recognition) return false;

    recognitionRef.current = recognition;
    recognition.onresult = async (event) => {
      const text = event.results[0][0].transcript.trim();
      if (!text) return;
      setProcessing(true);
      if (useWebSocket && connected && onAudioBlob) {
        onTranscript?.(text);
        onAudioBlob(null, text);
      } else {
        await sendViaHttp(text, true);
      }
    };
    recognition.onerror = (event) => {
      if (event.error !== "aborted") {
        onError?.("No se pudo reconocer la voz. Intenta de nuevo.");
      }
      setRecording(false);
      setProcessing(false);
    };
    recognition.onend = () => setRecording(false);
    recognition.start();
    setRecording(true);
    return true;
  }, [useWebSocket, connected, onAudioBlob, onTranscript, onError]);

  const startRecording = useCallback(async () => {
    if (useBrowserSttRef.current && startBrowserRecognition()) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";
      const mr = new MediaRecorder(stream, { mimeType });
      chunksRef.current = [];

      mr.ondataavailable = (e) => chunksRef.current.push(e.data);
      mr.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: mimeType });
        setProcessing(true);
        try {
          if (useWebSocket && connected && onAudioBlob) {
            const wavBlob = await audioBlobToWav(blob);
            onAudioBlob(wavBlob);
          } else {
            await sendViaHttp(blob, false);
          }
        } catch {
          onError?.("Error al procesar el audio.");
          setProcessing(false);
        }
      };

      mr.start();
      mediaRecorderRef.current = mr;
      setRecording(true);
    } catch {
      onError?.("No se pudo acceder al micrófono. Verifica permisos del navegador.");
    }
  }, [useWebSocket, connected, onAudioBlob, onError, startBrowserRecognition]);

  const stopRecording = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
      return;
    }
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  }, []);

  return { recording, processing, startRecording, stopRecording };
}
