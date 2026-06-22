import { useEffect, useState } from "react";
import axios from "axios";
import { Brain, FolderKanban, User } from "lucide-react";

export default function MemoryPanel() {
  const [context, setContext] = useState({ facts: [], projects: [], user_name: "", preferences: {} });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios
      .get("/api/memory/context")
      .then((r) => setContext(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-xs text-gray-500 p-4">Cargando memoria…</p>;
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-5 text-sm">
      <section>
        <div className="flex items-center gap-2 text-gray-400 mb-2">
          <User className="w-3.5 h-3.5" />
          <span className="text-xs font-medium uppercase tracking-wider">Perfil</span>
        </div>
        <p className="text-gray-200">{context.user_name || "Sin nombre"}</p>
        {Object.keys(context.preferences || {}).length > 0 && (
          <div className="mt-2 space-y-1">
            {Object.entries(context.preferences).map(([k, v]) => (
              <p key={k} className="text-xs text-gray-500">
                {k}: <span className="text-gray-400">{String(v)}</span>
              </p>
            ))}
          </div>
        )}
      </section>

      <section>
        <div className="flex items-center gap-2 text-gray-400 mb-2">
          <Brain className="w-3.5 h-3.5" />
          <span className="text-xs font-medium uppercase tracking-wider">Hechos</span>
        </div>
        {context.facts?.length ? (
          <ul className="space-y-2">
            {context.facts.map((f) => (
              <li key={f.key} className="glass-card p-2.5">
                <p className="text-xs text-harvey-400">{f.category}</p>
                <p className="text-gray-200 font-medium">{f.key}</p>
                <p className="text-gray-500 text-xs mt-0.5">{f.value}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-xs text-gray-600">Aún no hay hechos guardados.</p>
        )}
      </section>

      <section>
        <div className="flex items-center gap-2 text-gray-400 mb-2">
          <FolderKanban className="w-3.5 h-3.5" />
          <span className="text-xs font-medium uppercase tracking-wider">Proyectos</span>
        </div>
        {context.projects?.length ? (
          <ul className="space-y-2">
            {context.projects.map((p) => (
              <li key={p.name} className="glass-card p-2.5">
                <p className="text-gray-200 font-medium">{p.name}</p>
                <p className="text-xs text-gray-500">{p.description}</p>
                <span className="text-[10px] text-harvey-400 uppercase">{p.status}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-xs text-gray-600">Sin proyectos activos.</p>
        )}
      </section>
    </div>
  );
}
