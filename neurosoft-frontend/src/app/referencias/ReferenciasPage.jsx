/* ═══════════════════════════════════════════════════════════════════════
 * src/app/referencias/ReferenciasPage.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §F2 — Catálogo de referencias bibliográficas verificadas.
 *
 * Muestra referencias curadas con filtros por disciplina, tipo y categoría.
 * Búsqueda full-text. Cada ficha incluye cita APA, DOI/ISBN, resumen.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api } from "../../api/client.js";
import { Card, I, Input, Sel, TopBar, Spinner } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import SectionCard from "../../ui/SectionCard.jsx";

const TIPO_LABELS = {
  libro: "Libro", articulo: "Artículo", manual: "Manual",
  guia: "Guía", ley: "Ley", escala: "Escala", protocolo: "Protocolo",
};

const DISCIPLINA_COLORS = {
  neuropsicologia: "#0D9488",
  psicologia_clinica: "#7c3aed",
  ambas: "#0D9488",
};

export default function ReferenciasPage() {
  const [refs, setRefs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [disciplina, setDisciplina] = useState("");
  const [tipo, setTipo] = useState("");
  const [total, setTotal] = useState(0);

  const load = async (searchQuery) => {
    setLoading(true);
    try {
      const endpoint = searchQuery
        ? `/api/v1/referencias/search?q=${encodeURIComponent(searchQuery)}&limit=50`
        : `/api/v1/referencias/?limit=50${disciplina ? `&disciplina=${disciplina}` : ""}${tipo ? `&tipo=${tipo}` : ""}`;
      const data = await api.get(endpoint);
      setRefs(data.referencias || []);
      setTotal(data.total || 0);
    } catch { setRefs([]); }
    setLoading(false);
  };

  useEffect(() => { load(); /* eslint-disable-line react-hooks/exhaustive-deps */ }, [disciplina, tipo]);
  useEffect(() => {
    const t = setTimeout(() => load(q), 300);
    return () => clearTimeout(t);
  /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [q]);

  return <>
    <TopBar title="Referencias bibliográficas" />
    <main className="p-8 max-w-7xl mx-auto space-y-5">
      <div className="flex items-center gap-3 mb-4">
        <I name="menu_book" style={{ color: TEAL, fontSize: 26 }} />
        <div>
          <h2 className="ns-serif text-xl font-bold">Catálogo bibliográfico seleccionado</h2>
          <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
            {total} referencias · Fuentes verificadas con DOI/ISBN · APA 7ª edición
          </p>
        </div>
      </div>

      {/* Filtros */}
      <Card className="p-4 space-y-3">
        <div className="relative">
          <I name="search" className="absolute left-3 top-1/2 -translate-y-1/2 text-lg"
            style={{ color: "var(--ns-muted)" }} />
          <Input value={q} onChange={e => setQ(e.target.value)}
            placeholder="Buscar por título, autor o palabra clave..."
            style={{ paddingLeft: 38 }} />
        </div>
        <div className="flex gap-3 flex-wrap">
          <Sel value={disciplina} onChange={e => setDisciplina(e.target.value)} className="text-xs">
            <option value="">Todas las disciplinas</option>
            <option value="neuropsicologia">Neuropsicología</option>
            <option value="psicologia_clinica">Psicología Clínica</option>
            <option value="ambas">Ambas</option>
          </Sel>
          <Sel value={tipo} onChange={e => setTipo(e.target.value)} className="text-xs">
            <option value="">Todos los tipos</option>
            <option value="libro">Libro</option>
            <option value="articulo">Artículo</option>
            <option value="manual">Manual</option>
            <option value="guia">Guía</option>
            <option value="ley">Ley</option>
            <option value="escala">Escala</option>
            <option value="protocolo">Protocolo</option>
          </Sel>
        </div>
      </Card>

      {/* Listado */}
      {loading ? (
        <div className="py-12 text-center"><Spinner /></div>
      ) : refs.length === 0 ? (
        <Card className="p-12 text-center" style={{ background: "var(--ns-subtle)" }}>
          <I name="search_off" className="text-5xl opacity-30 mb-3" />
          <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
            {q ? `Sin resultados para "${q}".` : "No hay referencias disponibles."}
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {refs.map(r => {
            const discColor = DISCIPLINA_COLORS[r.disciplina] || TEAL;
            return (
              <SectionCard
                key={r.id}
                title={r.titulo}
                eyebrow={r.categoria?.replace(/_/g, " ") || "General"}
                subtitle={`${r.autores} (${r.anio})`}
                headerRight={
                  <div className="flex gap-2 shrink-0">
                    <span className="text-[10px] px-2 py-0.5 rounded-full font-bold"
                      style={{ background: discColor + "15", color: discColor }}>
                      {TIPO_LABELS[r.tipo] || r.tipo}
                    </span>
                    {r.nivel_evidencia && (
                      <span className="text-[10px] px-2 py-0.5 rounded-full font-bold"
                        style={{ background: "#10b98115", color: "#047857" }}>
                        Evidencia {r.nivel_evidencia}
                      </span>
                    )}
                  </div>
                }
              >
                {r.resumen && (
                  <p className="text-xs leading-relaxed mb-2" style={{ color: "var(--ns-text)" }}>
                    {r.resumen}
                  </p>
                )}

                {r.journal && (
                  <p className="text-[10px] ns-serif-italic mb-2" style={{ color: "var(--ns-muted)" }}>
                    {r.journal}
                  </p>
                )}

                <div className="flex flex-wrap gap-2 items-center text-[10px]"
                  style={{ color: "var(--ns-muted)" }}>
                  {r.doi && (
                    <a href={`https://doi.org/${r.doi}`} target="_blank" rel="noreferrer"
                      className="ns-mono hover:underline" style={{ color: discColor }}>
                      DOI: {r.doi}
                    </a>
                  )}
                  {r.isbn && (
                    <span className="ns-mono">ISBN: {r.isbn}</span>
                  )}
                  {r.url && (
                    <a href={r.url} target="_blank" rel="noreferrer"
                      className="hover:underline flex items-center gap-1" style={{ color: discColor }}>
                      <I name="open_in_new" className="text-xs" /> Enlace
                    </a>
                  )}
                </div>

                {r.tags && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {(() => {
                      try { return JSON.parse(r.tags).map(t => (
                        <span key={t} className="text-[9px] px-1.5 py-0.5 rounded"
                          style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>{t}</span>
                      )); } catch { return null; }
                    })()}
                  </div>
                )}
              </SectionCard>
            );
          })}
        </div>
      )}
    </main>
  </>;
}
