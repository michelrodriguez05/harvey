import { useEffect, useRef } from "react";
import { Bot, User } from "lucide-react";

export default function Chat({ messages, assistantName = "Yarbis" }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-3 p-6">
        <Bot className="w-10 h-10 opacity-30 text-cyan-400" />
        <p className="text-sm text-center">
          Di <span className="text-cyan-400">"Hola {assistantName}"</span> o usa el micrófono
        </p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto chat-scroll px-4 py-4 space-y-4">
      {messages.map((msg, i) => (
        <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
          {msg.role === "assistant" && (
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 text-white" />
            </div>
          )}
          <div
            className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
              msg.role === "user"
                ? "bg-gradient-to-br from-cyan-600 to-indigo-600 text-white rounded-br-md"
                : "bg-slate-800/80 text-slate-100 border border-slate-700/50 rounded-bl-md"
            }`}
          >
            {msg.agent && msg.agent !== "sistema" && (
              <span className="text-[10px] uppercase tracking-wider text-cyan-400/80 block mb-1">{msg.agent}</span>
            )}
            {msg.content}
          </div>
          {msg.role === "user" && (
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center shrink-0">
              <User className="w-4 h-4 text-slate-300" />
            </div>
          )}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
