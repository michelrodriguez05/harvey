import { useEffect, useState } from "react";
import axios from "axios";
import { Settings, Save, Mic, MicOff } from "lucide-react";

export default function SettingsPanel({ onSettingsSaved }) {
  const [form, setForm] = useState({
    assistant_name: "Yarbis",
    wake_word: "Yarbis",
    user_name: "Michel",
    always_listen: true,
    voice_first: true,
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    axios.get("/api/settings").then((r) => setForm((f) => ({ ...f, ...r.data }))).catch(() => {});
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      const res = await axios.patch("/api/settings", form);
      setForm((f) => ({ ...f, ...res.data }));
      setSaved(true);
      onSettingsSaved?.(res.data);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 text-sm">
      <div className="flex items-center gap-2 text-slate-400 mb-2">
        <Settings className="w-3.5 h-3.5" />
        <span className="text-xs font-medium uppercase tracking-wider">Personalizar Yarbis</span>
      </div>

      <div className="glass-card p-4 space-y-4">
        <div>
          <label className="text-xs text-slate-500 block mb-1">Nombre del asistente</label>
          <input
            value={form.assistant_name}
            onChange={(e) => setForm({ ...form, assistant_name: e.target.value })}
            className="w-full bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-cyan-500"
            placeholder="Ej: Yarbis, Jarvis, Nova..."
          />
          <p className="text-[10px] text-slate-600 mt-1">Di "Hola [nombre]" para activarlo</p>
        </div>

        <div>
          <label className="text-xs text-slate-500 block mb-1">Palabra de activación</label>
          <input
            value={form.wake_word}
            onChange={(e) => setForm({ ...form, wake_word: e.target.value })}
            className="w-full bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div>
          <label className="text-xs text-slate-500 block mb-1">Tu nombre</label>
          <input
            value={form.user_name}
            onChange={(e) => setForm({ ...form, user_name: e.target.value })}
            className="w-full bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>

        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={form.always_listen}
            onChange={(e) => setForm({ ...form, always_listen: e.target.checked })}
            className="rounded border-slate-600"
          />
          <span className="text-xs text-slate-400 flex items-center gap-1">
            {form.always_listen ? <Mic className="w-3 h-3 text-cyan-400" /> : <MicOff className="w-3 h-3" />}
            Escucha continua (menciona su nombre)
          </span>
        </label>

        <button
          onClick={save}
          disabled={saving}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white text-sm font-medium transition-all disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {saved ? "Guardado" : saving ? "Guardando…" : "Guardar cambios"}
        </button>
      </div>
    </div>
  );
}
