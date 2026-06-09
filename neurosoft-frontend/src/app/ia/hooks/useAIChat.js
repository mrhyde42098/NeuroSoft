import { useCallback, useEffect, useRef, useState } from "react";

const API = import.meta.env.PROD ? "" : "http://localhost:8000";
const tok = () => localStorage.getItem("ns_token") || "";

async function aiPost(path, body) {
  const r = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${tok()}`, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `HTTP ${r.status}`);
  return r.json();
}

const INITIAL_MSG = {
  role: "assistant",
  content:
    "Hola 👋 Soy el asistente clínico de NeuroSoft. Puedo ayudarte con interpretación de puntajes, redacción de informes o dudas técnicas.\n\n¿En qué te ayudo hoy?",
};

export function useAIChat() {
  const [msgs, setMsgs] = useState([INITIAL_MSG]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [showChips, setShowChips] = useState(true);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [msgs]);

  const send = useCallback(
    async (text) => {
      const t = (text || input).trim();
      if (!t || busy) return;
      const userMsg = { role: "user", content: t };
      setMsgs((m) => [...m, userMsg]);
      setInput("");
      setBusy(true);
      setShowChips(false);
      try {
        const r = await aiPost("/api/v1/ai/chat", {
          messages: [...msgs, userMsg].map((m) => ({ role: m.role, content: m.content })),
        });
        setMsgs((m) => [
          ...m,
          {
            role: "assistant",
            content: r.content || r.reply || "(respuesta vacía)",
            provider: `${r.provider || "?"}${r.model ? " · " + r.model : ""}`,
          },
        ]);
      } catch (e) {
        setMsgs((m) => [...m, { role: "assistant", content: `⚠ Error: ${e.message}`, error: true }]);
      }
      setBusy(false);
    },
    [input, busy, msgs],
  );

  const clearChat = useCallback(() => {
    setMsgs([{ role: "assistant", content: "Hola 👋 Soy el asistente clínico de NeuroSoft. ¿En qué te ayudo?" }]);
    setShowChips(true);
    setInput("");
  }, []);

  return { msgs, input, setInput, busy, showChips, scrollRef, send, clearChat };
}
