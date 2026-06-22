import { X } from "lucide-react";

export default function YouTubePlayer({ videoId, title, onClose }) {
  if (!videoId) return null;

  return (
    <div className="mx-4 mb-3 rounded-2xl overflow-hidden border border-gray-700/80 bg-black shadow-2xl shadow-harvey-500/10">
      <div className="flex items-center justify-between px-3 py-2 bg-gray-900/90 border-b border-gray-800">
        <p className="text-xs text-gray-300 truncate pr-2">
          Reproduciendo{title ? `: ${title}` : ""}
        </p>
        <button
          onClick={onClose}
          className="p-1 rounded-lg text-gray-500 hover:text-gray-200 hover:bg-gray-800 transition-colors"
          aria-label="Cerrar reproductor"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="relative w-full aspect-video">
        <iframe
          key={videoId}
          className="absolute inset-0 w-full h-full"
          src={`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&modestbranding=1`}
          title={title || "YouTube"}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    </div>
  );
}
