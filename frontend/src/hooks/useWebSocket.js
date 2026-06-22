import { useState, useRef, useCallback, useEffect } from "react";

const WS_URL = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws`;

export function useWebSocket({ onTranscript, onReply, onStatus, onAgent, onError, onConnected, onPlayYoutube }) {
  const wsRef = useRef(null);
  const callbacksRef = useRef({ onTranscript, onReply, onStatus, onAgent, onError, onConnected, onPlayYoutube });
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState("idle");
  const reconnectRef = useRef(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    callbacksRef.current = { onTranscript, onReply, onStatus, onAgent, onError, onConnected, onPlayYoutube };
  });

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      if (!mountedRef.current) return;
      setConnected(true);
      callbacksRef.current.onConnected?.();
    };

    ws.onclose = () => {
      if (!mountedRef.current) return;
      setConnected(false);
      wsRef.current = null;
      reconnectRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const cb = callbacksRef.current;

      switch (data.type) {
        case "connected":
          setConnected(true);
          break;
        case "status":
          setStatus(data.state);
          cb.onStatus?.(data.state);
          break;
        case "transcript":
          cb.onTranscript?.(data.text, data.role);
          break;
        case "reply":
          cb.onReply?.(data.text, data.agent, data.tools_used, data.youtube_video_id, data.youtube_title);
          cb.onAgent?.(data.agent);
          if (data.youtube_video_id) {
            cb.onPlayYoutube?.(data.youtube_video_id, data.youtube_title);
          }
          break;
        case "play_youtube":
          cb.onPlayYoutube?.(data.video_id, data.title);
          break;
        case "audio":
          playAudio(data.data, data.mime);
          break;
        case "error":
          cb.onError?.(data.message);
          setStatus("idle");
          cb.onStatus?.("idle");
          break;
        default:
          break;
      }
    };
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      clearTimeout(reconnectRef.current);
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [connect]);

  const send = useCallback((payload) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
      return true;
    }
    return false;
  }, []);

  const sendMessage = useCallback(
    (content, withAudio = false) => send({ type: "message", content, with_audio: withAudio }),
    [send]
  );

  const sendAudio = useCallback(
    (blob) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result.split(",")[1];
        send({ type: "audio", data: base64, mime: blob.type });
      };
      reader.readAsDataURL(blob);
    },
    [send]
  );

  const clearHistory = useCallback(() => send({ type: "clear" }), [send]);

  return { connected, status, sendMessage, sendAudio, clearHistory, send };
}

async function playAudio(base64, mime = "audio/mpeg") {
  try {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    const blob = new Blob([bytes], { type: mime });
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    await audio.play();
    audio.onended = () => URL.revokeObjectURL(url);
  } catch (err) {
    console.error("Error reproduciendo audio:", err);
  }
}
