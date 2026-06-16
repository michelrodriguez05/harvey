import { Mic, MicOff, Loader } from "lucide-react";

export default function VoiceButton({ recording, processing, onStart, onStop }) {
  if (processing) {
    return (
      <button className="w-20 h-20 rounded-full bg-harvey-700 flex items-center justify-center cursor-not-allowed">
        <Loader className="w-8 h-8 animate-spin text-white" />
      </button>
    );
  }

  if (recording) {
    return (
      <button
        onClick={onStop}
        className="w-20 h-20 rounded-full bg-red-600 hover:bg-red-500 flex items-center justify-center recording-pulse transition-colors"
      >
        <MicOff className="w-8 h-8 text-white" />
      </button>
    );
  }

  return (
    <button
      onClick={onStart}
      className="w-20 h-20 rounded-full bg-harvey-500 hover:bg-harvey-600 flex items-center justify-center transition-colors shadow-lg shadow-harvey-500/30"
    >
      <Mic className="w-8 h-8 text-white" />
    </button>
  );
}
