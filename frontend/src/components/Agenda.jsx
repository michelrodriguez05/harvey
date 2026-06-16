import { useEffect, useState } from "react";
import axios from "axios";
import { Calendar, CheckSquare, FileText, Trash2, Check } from "lucide-react";
import { format, parseISO } from "date-fns";
import { es } from "date-fns/locale";

export default function Agenda() {
  const [events, setEvents] = useState([]);
  const [todos, setTodos] = useState([]);
  const [notes, setNotes] = useState([]);
  const [tab, setTab] = useState("events");
  const [googleConnected, setGoogleConnected] = useState(false);

  useEffect(() => {
    axios.get("/auth/google/status").then((r) => setGoogleConnected(r.data.connected));
    loadAll();
  }, []);

  const loadAll = () => {
    axios.get("/api/events").then((r) => setEvents(r.data)).catch(() => {});
    axios.get("/api/todos").then((r) => setTodos(r.data)).catch(() => {});
    axios.get("/api/notes").then((r) => setNotes(r.data)).catch(() => {});
  };

  const completeTodo = async (id) => {
    await axios.patch(`/api/todos/${id}/complete`);
    loadAll();
  };

  const deleteEvent = async (id) => {
    await axios.delete(`/api/events/${id}`);
    loadAll();
  };

  const tabs = [
    { id: "events", label: "Agenda", icon: Calendar },
    { id: "todos", label: "Tareas", icon: CheckSquare },
    { id: "notes", label: "Notas", icon: FileText },
  ];

  return (
    <div className="flex flex-col h-full">
      {!googleConnected && (
        <div className="bg-yellow-900/40 border border-yellow-700 rounded-lg p-3 mx-3 mt-3 text-xs text-yellow-300 flex items-center justify-between">
          <span>Google Calendar no conectado</span>
          <a href="/auth/google" className="underline font-medium">Conectar</a>
        </div>
      )}

      <div className="flex border-b border-gray-800 mt-3">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium transition-colors ${
              tab === id ? "text-harvey-400 border-b-2 border-harvey-400" : "text-gray-500 hover:text-gray-300"
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            {label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {tab === "events" &&
          (events.length === 0 ? (
            <p className="text-gray-500 text-xs text-center mt-8">Sin eventos próximos</p>
          ) : (
            events.map((ev) => (
              <div key={ev.id} className="bg-gray-800 rounded-lg p-3 flex justify-between items-start">
                <div>
                  <p className="text-sm font-medium text-gray-100">{ev.title}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {format(parseISO(ev.start), "dd MMM, HH:mm", { locale: es })}
                  </p>
                  {ev.description && <p className="text-xs text-gray-500 mt-1">{ev.description}</p>}
                </div>
                <button onClick={() => deleteEvent(ev.id)} className="text-gray-600 hover:text-red-400 ml-2 shrink-0">
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          ))}

        {tab === "todos" &&
          (todos.length === 0 ? (
            <p className="text-gray-500 text-xs text-center mt-8">Sin tareas pendientes</p>
          ) : (
            todos.map((todo) => (
              <div key={todo.id} className="bg-gray-800 rounded-lg p-3 flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-100">{todo.task}</p>
                  <span className={`text-xs mt-0.5 inline-block px-1.5 py-0.5 rounded-full ${
                    todo.priority === "alta" ? "bg-red-900 text-red-300" :
                    todo.priority === "baja" ? "bg-gray-700 text-gray-400" :
                    "bg-blue-900 text-blue-300"
                  }`}>{todo.priority}</span>
                </div>
                <button onClick={() => completeTodo(todo.id)} className="text-gray-600 hover:text-green-400 ml-2">
                  <Check className="w-4 h-4" />
                </button>
              </div>
            ))
          ))}

        {tab === "notes" &&
          (notes.length === 0 ? (
            <p className="text-gray-500 text-xs text-center mt-8">Sin notas guardadas</p>
          ) : (
            notes.map((note) => (
              <div key={note.id} className="bg-gray-800 rounded-lg p-3">
                <p className="text-sm text-gray-200 whitespace-pre-wrap">{note.content}</p>
                <p className="text-xs text-gray-600 mt-1">{note.created_at}</p>
              </div>
            ))
          ))}
      </div>
    </div>
  );
}
