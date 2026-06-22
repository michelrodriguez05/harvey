export default function AudioVisualizer({ active, status }) {
  const bars = Array.from({ length: 12 });

  return (
    <div className="relative flex items-center justify-center">
      <div
        className={`absolute w-32 h-32 rounded-full transition-all duration-700 ${
          active ? "orb-glow scale-100" : "scale-90 opacity-40"
        }`}
      />
      <div
        className={`relative w-28 h-28 rounded-full flex items-center justify-center border transition-all duration-500 ${
          status === "thinking"
            ? "border-amber-400/60 bg-amber-500/10"
            : status === "speaking"
            ? "border-emerald-400/60 bg-emerald-500/10"
            : active
            ? "border-harvey-400/80 bg-harvey-500/20"
            : "border-gray-700/60 bg-gray-800/40"
        }`}
      >
        <div className="flex items-end gap-1 h-10">
          {bars.map((_, i) => (
            <div
              key={i}
              className={`w-1 rounded-full bg-gradient-to-t from-harvey-600 to-harvey-300 transition-all ${
                active ? "visualizer-bar" : "h-2 opacity-30"
              }`}
              style={{ animationDelay: `${i * 0.08}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
