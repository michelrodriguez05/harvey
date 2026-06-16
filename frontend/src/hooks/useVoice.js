import { useState, useRef, useCallback } from "react";
import axios from "axios";

export function useVoice({ onTranscript, onReply }) {
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mr = new MediaRecorder(stream, { mimeType: "audio/webm" });
    chunksRef.current = [];

    mr.ondataavailable = (e) => chunksRef.current.push(e.data);
    mr.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      await sendAudio(blob);
    };

    mr.start();
    mediaRecorderRef.current = mr;
    setRecording(true);
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  }, [recording]);

  const sendAudio = async (blob) => {
    setProcessing(true);
    try {
      const formData = new FormData();
      formData.append("audio", blob, "recording.webm");

      const res = await axios.post("/api/voice/chat", formData, {
        responseType: "arraybuffer",
      });

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
      console.error("Error en voice chat:", err);
    } finally {
      setProcessing(false);
    }
  };

  return { recording, processing, startRecording, stopRecording };
}
