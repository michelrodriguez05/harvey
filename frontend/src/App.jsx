import { useState, useCallback, useEffect, useRef } from "react";
import axios from "axios";
import {
  Send,
  Trash2,
  LayoutGrid,
  Brain,
  Settings,
  Wifi,
  WifiOff,
  AlertTriangle,
  MessageSquare,
  Mic,
  ChevronUp,
  ChevronDown,
} from "lucide-react";
import Chat from "./components/Chat";
import VoiceButton from "./components/VoiceButton";
import Agenda from "./components/Agenda";
import VoiceOrb from "./components/VoiceOrb";
import MemoryPanel from "./components/MemoryPanel";
import SettingsPanel from "./components/SettingsPanel";
import YouTubePlayer from "./components/YouTubePlayer";
import { useWebSocket } from "./hooks/useWebSocket";
import { useVoice } from "./hooks/useVoice";
import { useAlwaysListening } from "./hooks/useAlwaysListening";

const TABS = [
  { id: "agenda", icon: LayoutGrid, label: "Agenda" },
  { id: "memory", icon: Brain, label: "Memoria" },
  { id: "settings", icon: Settings, label: "Config" },
];

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sideTab, setSideTab] = useState(null);
  const [activeAgent, setActiveAgent] = useState(null);
  const [config, setConfig] = useState({
    assistant_name: "Yarbis",
    wake_word: "Yarbis",
    user_name: "Michel",
    always_listen: true,
    voice_first: true,
  });
  const [wsStatus, setWsStatus] = useState("idle");
  const [systemError, setSystemError] = useState(null);
  const [youtube, setYoutube] = useState({ videoId: null, title: null });
  const [showTextInput, setShowTextInput] = useState(false);
  const [showChat, setShowChat] = useState(true);
  const alwaysListenRef = useRef(null);

  const loadConfig = useCallback(() => {
    axios.get("/api/config").then((r) => setConfig((c) => ({ ...c, ...r.data }))).catch(() => {});
  }, []);

  useEffect(() => {
    loadConfig();
    axios.get("/api/health").then((r) => {
      if (!r.data.api_key_ok) setSystemError(r.data.api_key_message);
    }).catch(() => {});
    axios.get("/api/history").then((r) => {
      if (r.data.messages?.length) setMessages(r.data.messages);
    }).catch(() => {});
  }, [loadConfig]);

  const addMessage = useCallback((role, content, agent) => {
    setMessages((prev) => [...prev, { role, content, agent }]);
  }, []);

  const playYoutube = useCallback((videoId, title) => {
    if (videoId) setYoutube({ videoId, title: title || null });
  }, []);

  const handleError = useCallback(
    (message) => {
      const lower = (message || "").toLowerCase();
      let friendly = message || "Error desconocido";
      if (lower.includes("credit balance") || lower.includes("billing")) {
        friendly = "Sin créditos en Anthropic. Usa Groq en .env o agrega saldo.";
      }
      setSystemError(friendly);
      addMessage("assistant", friendly, "sistema");
      setLoading(false);
      alwaysListenRef.current?.markProcessingDone?.();
    },
    [addMessage]
  );

  const sendUserMessage = useCallback(
    (text, withAudio = true) => {
      const trimmed = text.trim();
      if (!trimmed || loading) return false;
      addMessage("user", trimmed);
      setLoading(true);
      setWsStatus("thinking");
      const sent = wsSendRef.current?.({ type: "message", content: trimmed, with_audio: withAudio });
      if (!sent) {
        axios
          .post("/api/chat", { message: trimmed })
          .then((res) => {
            addMessage("assistant", res.data.reply, res.data.agent);
            setActiveAgent(res.data.agent);
            if (res.data.youtube_video_id) playYoutube(res.data.youtube_video_id, res.data.youtube_title);
            if (withAudio && !res.data.youtube_video_id) {
              axios.post("/api/voice/speak", { message: res.data.reply }, { responseType: "arraybuffer" }).then((speak) => {
                const ctx = new AudioContext();
                ctx.decodeAudioData(speak.data).then((buf) => {
                  const src = ctx.createBufferSource();
                  src.buffer = buf;
                  src.connect(ctx.destination);
                  src.start();
                });
              });
            }
          })
          .catch((err) => handleError(err.response?.data?.detail || err.message))
          .finally(() => {
            setLoading(false);
            setWsStatus("idle");
            alwaysListenRef.current?.markProcessingDone?.();
          });
      }
      return true;
    },
    [loading, addMessage, playYoutube, handleError]
  );

  const wsSendRef = useRef(null);

  const { connected, send: wsSend } = useWebSocket({
    onTranscript: (text, role) => {
      if (role === "user") addMessage("user", text);
    },
    onReply: (text, agent, _tools, videoId, title) => {
      addMessage("assistant", text, agent);
      setActiveAgent(agent);
      setLoading(false);
      setWsStatus("idle");
      setSystemError(null);
      if (videoId) playYoutube(videoId, title);
      alwaysListenRef.current?.markProcessingDone?.();
    },
    onStatus: (state) => {
      setWsStatus(state);
      if (state === "speaking") setLoading(true);
      if (state === "idle") setLoading(false);
    },
    onError: handleError,
    onPlayYoutube: playYoutube,
  });

  wsSendRef.current = wsSend;

  const { listening, awaitingCommand, markProcessingDone } = useAlwaysListening({
    assistantName: config.assistant_name,
    wakeWord: config.wake_word,
    enabled: config.always_listen && connected && !loading,
    onCommand: (command) => sendUserMessage(command, true),
    onWake: () => setWsStatus("listening"),
    onError: handleError,
  });

  alwaysListenRef.current = { markProcessingDone };

  const { recording, processing, startRecording, stopRecording } = useVoice({
    useWebSocket: true,
    onAudioBlob: (blob, text) => {
      setLoading(true);
      setWsStatus("thinking");
      if (text) {
        addMessage("user", text);
        wsSend({ type: "message", content: text, with_audio: true });
      } else if (blob) {
        const reader = new FileReader();
        reader.onload = () => {
          wsSend({ type: "audio", data: reader.result.split(",")[1], mime: blob.type || "audio/wav" });
        };
        reader.readAsDataURL(blob);
      }
    },
    connected,
    onError: handleError,
  });

  const sendText = () => {
    if (sendUserMessage(input, false)) setInput("");
  };

  const clearHistory = () => {
    wsSend({ type: "clear" });
    axios.delete("/api/history").catch(() => {});
    setMessages([]);
    setActiveAgent(null);
    setSystemError(null);
    setYoutube({ videoId: null, title: null });
  };

  const orbStatus = recording
    ? "recording"
    : loading || wsStatus === "thinking"
    ? "thinking"
    : wsStatus === "speaking"
    ? "speaking"
    : listening
    ? "listening"
    : "idle";

  return (
    <div className="app-bg flex h-screen w-full">
      <div className="flex flex-col flex-1 min-w-0">
        <header className="flex items-center justify-between px-6 py-4 border-b border-slate-800/60">
          <div className="flex items-center gap-4">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-cyan-400 to-indigo-600 flex items-center justify-center font-bold text-white text-lg shadow-lg shadow-cyan-500/20">
              {config.assistant_name?.[0]?.toUpperCase() || "Y"}
            </div>
            <div>
              <h1 className="font-semibold text-lg text-slate-100 tracking-tight">{config.assistant_name} AI</h1>
              <p className="text-xs text-slate-500 flex items-center gap-1.5">
                {connected ? <Wifi className="w-3 h-3 text-emerald-400" /> : <WifiOff className="w-3 h-3 text-amber-400" />}
                {activeAgent ? `Agente: ${activeAgent}` : listening ? "Escuchando…" : connected ? "En línea" : "Modo HTTP"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setShowChat((v) => !v)}
              className={`p-2.5 rounded-xl transition-colors ${showChat ? "bg-slate-800 text-cyan-400" : "text-slate-500 hover:bg-slate-800"}`}
              title="Chat"
            >
              <MessageSquare className="w-4 h-4" />
            </button>
            {TABS.map(({ id, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setSideTab((prev) => (prev === id ? null : id))}
                className={`p-2.5 rounded-xl transition-colors ${
                  sideTab === id ? "bg-indigo-600 text-white" : "text-slate-500 hover:bg-slate-800 hover:text-slate-300"
                }`}
              >
                <Icon className="w-4 h-4" />
              </button>
            ))}
            <button onClick={clearHistory} className="p-2.5 rounded-xl text-slate-500 hover:text-red-400 hover:bg-slate-800">
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </header>

        {systemError && (
          <div className="mx-6 mt-3 flex items-start gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-xs text-amber-200">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{systemError}</span>
          </div>
        )}

        <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
          <VoiceOrb
            status={orbStatus}
            assistantName={config.assistant_name}
            wakeWord={config.wake_word}
            listening={listening || recording}
            awaitingCommand={awaitingCommand}
          />

          <YouTubePlayer
            videoId={youtube.videoId}
            title={youtube.title}
            onClose={() => setYoutube({ videoId: null, title: null })}
          />

          {showChat && (
            <div className="flex-1 min-h-0 mx-6 mb-2 glass-panel overflow-hidden animate-fade-in">
              <Chat messages={messages} assistantName={config.assistant_name} />
            </div>
          )}
        </div>

        <div className="border-t border-slate-800/60 px-6 py-4 space-y-3">
          <div className="flex items-center justify-center gap-4">
            <VoiceButton recording={recording} processing={processing || loading} onStart={startRecording} onStop={stopRecording} />
            <button
              onClick={() => setShowTextInput((v) => !v)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs transition-colors ${
                showTextInput ? "bg-slate-800 text-cyan-400" : "text-slate-500 hover:bg-slate-800"
              }`}
            >
              {showTextInput ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
              {showTextInput ? "Ocultar texto" : "Escribir mensaje"}
            </button>
            <div className="flex items-center gap-1.5 text-xs text-slate-600">
              <Mic className={`w-3 h-3 ${config.always_listen ? "text-cyan-400" : "text-slate-600"}`} />
              {config.always_listen ? "Voz activa" : "Voz pausada"}
            </div>
          </div>

          {showTextInput && (
            <div className="flex gap-2 max-w-2xl mx-auto animate-fade-in">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendText()}
                placeholder="Escribe cuando quieras…"
                disabled={loading || recording}
                className="flex-1 bg-slate-900/80 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500/60"
              />
              <button
                onClick={sendText}
                disabled={loading || !input.trim()}
                className="p-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 text-white disabled:opacity-40 transition-opacity"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>

      {sideTab && (
        <div className="w-80 flex flex-col border-l border-slate-800/60 bg-slate-950/80 backdrop-blur-xl">
          <div className="px-4 py-4 border-b border-slate-800/60">
            <h2 className="font-semibold text-slate-200 text-sm capitalize">{sideTab}</h2>
          </div>
          {sideTab === "agenda" && <Agenda />}
          {sideTab === "memory" && <MemoryPanel />}
          {sideTab === "settings" && (
            <SettingsPanel
              onSettingsSaved={(data) => {
                setConfig((c) => ({ ...c, ...data }));
                loadConfig();
              }}
            />
          )}
        </div>
      )}
    </div>
  );
}
