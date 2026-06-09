import React, { useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { Btn, I, Input } from "../primitives.jsx";
import { TEAL } from "../tokens.js";

const FRECUENTES = [
  { codigo: "F90", descripcion: "TDAH" },
  { codigo: "F84", descripcion: "Trastorno del espectro autista" },
  { codigo: "F81", descripcion: "Trastorno del aprendizaje" },
  { codigo: "F32", descripcion: "Episodio depresivo" },
  { codigo: "F41", descripcion: "Trastorno de ansiedad" },
  { codigo: "F809", descripcion: "Trastorno del desarrollo del habla/lenguaje" },
  { codigo: "G3184", descripcion: "Deterioro cognitivo leve" },
  { codigo: "Z04", descripcion: "Examen/observación (peritaje)" },
];

export default function CieSearchModal({ open, onClose, onSelect, title = "Buscar CIE-10" }) {
  const [q, setQ] = useState("");
  const [results, setResults] = useState(FRECUENTES);
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  const search = async (term) => {
    setQ(term);
    if (term.length < 2) {
      setResults(FRECUENTES);
      return;
    }
    const local = FRECUENTES.filter(
      (c) => c.codigo.toLowerCase().includes(term.toLowerCase())
        || c.descripcion.toLowerCase().includes(term.toLowerCase()),
    );
    setResults(local);
    setLoading(true);
    try {
      const d = await api.get(`/api/v1/cie10/?buscar=${encodeURIComponent(term)}`);
      if (Array.isArray(d) && d.length) {
        setResults(d.map((c) => ({ codigo: c.codigo, descripcion: c.descripcion || c.nombre })));
      } else if (!local.length) setResults([]);
    } catch {
      if (!local.length) setResults([]);
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center p-4" style={{ background: "rgba(0,0,0,0.55)" }}>
      <div className="w-full max-w-lg rounded-2xl shadow-xl flex flex-col max-h-[85vh]" style={{ background: "var(--ns-card)" }}>
        <div className="p-4 border-b flex items-center justify-between" style={{ borderColor: "var(--ns-card-b)" }}>
          <h3 className="font-bold flex items-center gap-2"><I name="search" style={{ color: TEAL }} />{title}</h3>
          <button type="button" onClick={onClose} className="p-2 rounded-lg hover:opacity-80" aria-label="Cerrar"><I name="close" /></button>
        </div>
        <div className="p-4 border-b" style={{ borderColor: "var(--ns-card-b)" }}>
          <Input value={q} onChange={(e) => search(e.target.value)} placeholder="Código o descriptor (mín. 2 caracteres)…" autoFocus />
        </div>
        <div className="flex-1 overflow-auto p-2">
          {loading && <p className="text-xs text-center py-4" style={{ color: "var(--ns-muted)" }}>Buscando…</p>}
          {!loading && results.length === 0 && (
            <p className="text-xs text-center py-6" style={{ color: "var(--ns-muted)" }}>Sin resultados</p>
          )}
          {results.map((c) => (
            <button
              key={c.codigo}
              type="button"
              onClick={() => { onSelect(c.codigo, c.descripcion); onClose(); }}
              className="w-full text-left px-3 py-2.5 rounded-lg hover:opacity-90 mb-1 flex gap-2"
              style={{ background: "var(--ns-subtle)" }}
            >
              <span className="font-mono text-xs font-bold shrink-0" style={{ color: TEAL }}>{c.codigo}</span>
              <span className="text-xs truncate">{c.descripcion}</span>
            </button>
          ))}
        </div>
        <div className="p-3 border-t flex justify-end" style={{ borderColor: "var(--ns-card-b)" }}>
          <Btn v="outline" onClick={onClose}>Cerrar</Btn>
        </div>
      </div>
    </div>
  );
}
