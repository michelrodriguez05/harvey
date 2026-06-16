import { useState, useCallback } from "react";
import axios from "axios";
import { Send, Trash2, LayoutGrid } from "lucide-react";
import Chat from "./components/Chat";
import VoiceButton from "./components/VoiceButton";
import Agenda from "./components/Agenda";
import { useVoice } from "./hooks/useVoice";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showAgenda, setShowAgenda] = useState(false);

  const addMessage = useCallback((role, content) => {
    setMessages((prev) => [...prev, { role, content }]);
  }, []);

  const { recording, processing, startRecording, stopRecording } = useVoice({
    onTranscript: (text) => addMessage("user", text),
    onReply: (reply) => addMessage("assistant", reply),
  });

  const sendText = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    addMessage("user", text);
    setLoading(true);
    try {
      const res = await axios.post("/api/chat", { message: text });
      addMessage("assistant", res.data.reply);
    } catch {
      addMessage("assistant", "Error al procesar tu mensaje. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    await axios.delete("/api/history");
    setMessages([]);
  };

  return (
    <div className="flex h-screen max-w-5xl mx-auto">
      {/* Panel principal */}
      <div className="flex flex-col flex-1 border-r border-gray-800">
        {/* Header */}
        <header className="flex items-center justify-between px-5 py-4 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-harvey-500 flex items-center justify-center font-bold text-white text-lg">H</div>
            <div>
              <h1 className="font-semibold text-gray-100 leading-none">Harvey</h1>
              <p className="text-xs text-gray-500">Asistente personal</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowAgenda((v) => !v)}
              className={`p-2 rounded-lg transition-colors ${showAgenda ? "bg-harvey-600 text-white" : "text-gray-500 hover:text-gray-300 hover:bg-gray-800"}`}
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button onClick={clearHistory} className="p-2 rounded-lg text-gray-500 hover:text-red-400 hover:bg-gray-800 transition-colors">
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Chat */}
        <Chat messages={messages} />

        {/* Input area */}
        <div className="border-t border-gray-800 px-4 py-4">
          <div className="flex items-center gap-3">
            <VoiceButton
              recording={recording}
              processing={processing}
              onStart={startRecording}
              onStop={stopRecording}
            />
            <div className="flex-1 flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendText()}
                placeholder="Escribe o usa el micrófono…"
                disabled={loading || recording || processing}
                className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-harvey-500 disabled:opacity-50"
              />
              <button
                onClick={sendText}
                disabled={loading || !input.trim() || recording}
                className="p-3 rounded-xl bg-harvey-500 hover:bg-harvey-600 text-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
          {(recording || processing) && (
            <p className="text-xs text-center mt-2 text-harvey-400">
              {recording ? "Escuchando… suelta para enviar" : "Procesando…"}
            </p>
          )}
        </div>
      </div>

      {/* Panel agenda (lateral) */}
      {showAgenda && (
        <div className="w-80 flex flex-col border-l border-gray-800">
          <div className="px-4 py-4 border-b border-gray-800">
            <h2 className="font-semibold text-gray-200 text-sm">Mi Agenda</h2>
          </div>
          <Agenda />
        </div>
      )}
    </div>
  );
}
