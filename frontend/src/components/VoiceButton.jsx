import { Mic, MicOff, Loader } from "lucide-react";

export default function VoiceButton({ recording, processing, onStart, onStop }) {
  if (processing) {
    return (
      <button className="w-16 h-16 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center cursor-not-allowed">
        <Loader className="w-7 h-7 animate-spin text-cyan-400" />
      </button>
    );
  }

  if (recording) {
    return (
      <button
        onClick={onStop}
        className="w-16 h-16 rounded-full bg-red-500/90 hover:bg-red-400 flex items-center justify-center recording-pulse transition-all shadow-lg shadow-red-500/30"
      >
        <MicOff className="w-7 h-7 text-white" />
      </button>
    );
  }

  return (
    <button
      onClick={onStart}
      className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 flex items-center justify-center transition-all shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:scale-105"
    >
      <Mic className="w-7 h-7 text-white" />
    </button>
  );
}
