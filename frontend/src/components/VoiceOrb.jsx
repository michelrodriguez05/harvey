export default function VoiceOrb({ status, assistantName, wakeWord, listening, awaitingCommand }) {
  const label = {
    idle: `Di "Hola ${wakeWord || assistantName}"`,
    listening: awaitingCommand ? "Te escucho…" : "Escuchando…",
    thinking: "Pensando…",
    speaking: "Respondiendo…",
    recording: "Grabando…",
  }[status] || "Listo";

  const active = ["listening", "thinking", "speaking", "recording"].includes(status);

  return (
    <div className="relative flex flex-col items-center justify-center py-8">
      <div className={`orb-ring ${active ? "orb-ring-active" : ""}`} />
      <div className={`orb-ring orb-ring-2 ${active ? "orb-ring-active" : ""}`} />

      <div
        className={`relative w-44 h-44 rounded-full flex items-center justify-center transition-all duration-700 ${
          status === "thinking"
            ? "orb-core-thinking"
            : status === "speaking"
            ? "orb-core-speaking"
            : status === "listening" || status === "recording"
            ? "orb-core-listening"
            : "orb-core-idle"
        }`}
      >
        <div className="absolute inset-3 rounded-full border border-white/10" />
        <div className="flex items-end gap-1 h-12 z-10">
          {Array.from({ length: 16 }).map((_, i) => (
            <div
              key={i}
              className={`w-1 rounded-full bg-gradient-to-t from-cyan-400 to-indigo-300 transition-all ${
                active ? "orb-bar" : "h-2 opacity-20"
              }`}
              style={{ animationDelay: `${i * 0.06}s` }}
            />
          ))}
        </div>
      </div>

      <p className="mt-8 text-sm font-medium tracking-wide text-slate-300">{label}</p>
      {listening && (
        <p className="mt-1 text-xs text-cyan-400/80 animate-pulse">
          {awaitingCommand ? "¿En qué te ayudo?" : `Menciona "${wakeWord || assistantName}" para hablar`}
        </p>
      )}
    </div>
  );
}
