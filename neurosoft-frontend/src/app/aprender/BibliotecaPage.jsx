/* ═══════════════════════════════════════════════════════════════════════
 * src/app/aprender/BibliotecaPage.jsx
 * ───────────────────────────────────────────────────────────────────────
 * Página principal del módulo "Aprender" (Pilar 3 de NeuroSoft App).
 *
 * MVP: catálogo curado de bibliografía clínica buscable y filtrable por
 * categoría / nivel / texto libre. NO aloja PDFs — solo referencias.
 *
 * Diseño editorial coherente con Dashboard y SesionSOAP:
 *   - Header con eyebrow + título serif
 *   - Filtros como chips (no como dropdowns)
 *   - Cards de referencia tipo "ficha bibliográfica" (rounded-md + acento)
 *   - Destacados arriba con badge
 *
 * Próximas iteraciones (no MVP):
 *   - Curso interactivo "Mejorando tu evaluación"
 *   - Casos clínicos resueltos para entrenamiento
 *   - Quizes de auto-evaluación
 *   - Marcar leídos / favoritos en localStorage
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useMemo, useState } from "react";
import { I, TopBar } from "../../ui/primitives.jsx";
import { TEAL, NAVY } from "../../ui/tokens.js";
import {
  BIBLIOTECA_RECURSOS,
  BIBLIOTECA_CATEGORIAS,
  filtrarRecursos,
} from "../../data/bibliotecaRecursos.js";

const TIPO_LABEL = {
  articulo:   { lb: "Artículo",    ic: "article" },
  manual:     { lb: "Manual",      ic: "menu_book" },
  escala:     { lb: "Escala",      ic: "rule" },
  guia:       { lb: "Guía",        ic: "map" },
  video:      { lb: "Video",       ic: "play_circle" },
  protocolo:  { lb: "Protocolo",   ic: "fact_check" },
};

const NIVEL_LABEL = {
  basico:     { lb: "Básico",      c: "#10b981" },
  intermedio: { lb: "Intermedio",  c: "#B45309" },
  avanzado:   { lb: "Avanzado",    c: "#7c1212" },
};

export default function BibliotecaPage() {
  const [texto, setTexto] = useState("");
  const [categoria, setCategoria] = useState("todos");
  const [nivel, setNivel] = useState("");

  const filtrados = useMemo(
    () => filtrarRecursos(BIBLIOTECA_RECURSOS, { texto, categoria, nivel }),
    [texto, categoria, nivel]
  );

  const destacados = useMemo(
    () => filtrados.filter(r => r.destacado).slice(0, 4),
    [filtrados]
  );

  const restantes = useMemo(
    () => filtrados.filter(r => !r.destacado),
    [filtrados]
  );

  return (
    <>
      <TopBar title="Aprender · Biblioteca Clínica" />
      <main className="p-6 lg:p-8 max-w-7xl mx-auto space-y-7"
        style={{ background: "var(--ns-bg)", minHeight: "100vh" }}>

        {/* §editorial: header */}
        <div className="ns-section-rule">
          <p className="ns-eyebrow" style={{ color: TEAL }}>Pilar 3 · Aprender</p>
          <h2 className="ns-serif text-3xl font-bold mt-1 mb-2" style={{ color: "var(--ns-text)" }}>
            Biblioteca <span className="ns-serif-italic" style={{ color: TEAL }}>clínica curada</span>
          </h2>
          <p className="text-sm max-w-2xl" style={{ color: "var(--ns-muted)" }}>
            Una selección viva de manuales, artículos y escalas relevantes para tu práctica.
            Cada recurso está clasificado por categoría, nivel y fuente —
            no alojamos los textos, te guiamos a las fuentes oficiales.
          </p>
        </div>

        {/* Buscador */}
        <div className="rounded-md border p-4"
          style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
          <div className="flex items-center gap-3 mb-4">
            <I name="search" className="text-lg" style={{ color: TEAL }} />
            <input
              type="text"
              value={texto}
              onChange={e => setTexto(e.target.value)}
              placeholder="Busca por título, autor, tag o palabra clave…"
              className="flex-1 px-3 py-2 rounded-md text-sm"
              style={{
                background: "var(--ns-input)",
                border: "1px solid var(--ns-card-b)",
                color: "var(--ns-text)",
              }}
            />
            {texto && (
              <button onClick={() => setTexto("")}
                className="text-xs flex items-center gap-1 px-2 py-1 rounded"
                style={{ color: "var(--ns-muted)" }}>
                <I name="close" className="text-sm" /> Limpiar
              </button>
            )}
          </div>

          {/* Categorías como chips */}
          <div>
            <p className="ns-eyebrow mb-2">Categoría</p>
            <div className="flex flex-wrap gap-2">
              {BIBLIOTECA_CATEGORIAS.map(c => {
                const activo = categoria === c.id;
                return (
                  <button key={c.id} onClick={() => setCategoria(c.id)}
                    className="text-xs font-semibold px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all"
                    style={{
                      background: activo ? c.color : "transparent",
                      color: activo ? "#fff" : c.color,
                      border: `1px solid ${c.color}50`,
                    }}>
                    <I name={c.ic} className="text-sm" />
                    {c.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Nivel */}
          <div className="mt-3">
            <p className="ns-eyebrow mb-2">Nivel</p>
            <div className="flex flex-wrap gap-2">
              <button onClick={() => setNivel("")}
                className="text-xs font-semibold px-3 py-1.5 rounded-md transition-all"
                style={{
                  background: nivel === "" ? "var(--ns-text)" : "transparent",
                  color: nivel === "" ? "var(--ns-card)" : "var(--ns-muted)",
                  border: "1px solid var(--ns-card-b)",
                }}>
                Todos
              </button>
              {Object.entries(NIVEL_LABEL).map(([k, v]) => {
                const activo = nivel === k;
                return (
                  <button key={k} onClick={() => setNivel(k)}
                    className="text-xs font-semibold px-3 py-1.5 rounded-md transition-all"
                    style={{
                      background: activo ? v.c : "transparent",
                      color: activo ? "#fff" : v.c,
                      border: `1px solid ${v.c}50`,
                    }}>
                    {v.lb}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Resumen de resultados */}
        <div className="flex items-center justify-between">
          <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
            <span className="ns-serif text-base font-bold tabular-nums" style={{ color: "var(--ns-text)" }}>
              {filtrados.length}
            </span>{" "}
            recurso{filtrados.length !== 1 ? "s" : ""} {texto ? `para “${texto}”` : ""}
          </p>
        </div>

        {/* Destacados */}
        {destacados.length > 0 && (
          <div>
            <p className="ns-eyebrow mb-3" style={{ color: TEAL }}>Destacados</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {destacados.map(r => <ResourceCard key={r.id} recurso={r} destacado />)}
            </div>
          </div>
        )}

        {/* Resto */}
        {restantes.length > 0 && (
          <div>
            <p className="ns-eyebrow mb-3">Catálogo completo</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {restantes.map(r => <ResourceCard key={r.id} recurso={r} />)}
            </div>
          </div>
        )}

        {/* Sin resultados */}
        {filtrados.length === 0 && (
          <div className="rounded-md border p-12 text-center"
            style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
            <I name="search_off" className="text-4xl mb-3" style={{ color: "var(--ns-muted)" }} />
            <p className="ns-serif text-lg italic" style={{ color: "var(--ns-muted)" }}>
              Sin resultados para esa búsqueda.
            </p>
            <p className="text-xs mt-2" style={{ color: "var(--ns-muted)" }}>
              Prueba con otra categoría, otro nivel, o palabras más generales.
            </p>
          </div>
        )}

        {/* Disclaimer final */}
        <div className="rounded-md p-4 mt-8"
          style={{ background: "var(--ns-subtle)", borderLeft: `3px solid ${TEAL}` }}>
          <p className="ns-eyebrow mb-1" style={{ color: TEAL }}>Sobre esta biblioteca</p>
          <p className="text-xs leading-relaxed" style={{ color: "var(--ns-muted)" }}>
            Los recursos aquí listados son referencias bibliográficas curadas — NeuroSoft no aloja
            ni distribuye los textos completos. Para acceder al material, sigue las indicaciones de
            cada ficha (PDF abierto, suscripción institucional, librería). Si encuentras una referencia
            que debería estar acá, escríbenos a{" "}
            <span className="ns-mono" style={{ color: NAVY }}>jssalgadosa@unal.edu.co</span>.
          </p>
        </div>
      </main>
    </>
  );
}

function ResourceCard({ recurso, destacado }) {
  const tipo = TIPO_LABEL[recurso.tipo] || { lb: recurso.tipo, ic: "auto_stories" };
  const nivelMeta = NIVEL_LABEL[recurso.nivel] || { lb: recurso.nivel, c: "#475569" };
  const cat = BIBLIOTECA_CATEGORIAS.find(c => c.id === recurso.categoria);
  const acento = cat?.color || TEAL;

  const abrir = () => {
    if (recurso.url) window.open(recurso.url, "_blank", "noopener,noreferrer");
    else if (recurso.doi) window.open(`https://doi.org/${recurso.doi}`, "_blank", "noopener,noreferrer");
  };

  return (
    <article
      role={recurso.url || recurso.doi ? "button" : undefined}
      tabIndex={recurso.url || recurso.doi ? 0 : undefined}
      onClick={recurso.url || recurso.doi ? abrir : undefined}
      onKeyDown={recurso.url || recurso.doi ? (e) => { if (e.key === "Enter") abrir(); } : undefined}
      className={`p-5 rounded-md border transition-all hover:shadow-sm ${recurso.url || recurso.doi ? "cursor-pointer" : ""}`}
      style={{
        background: "var(--ns-card)",
        borderColor: "var(--ns-card-b)",
        borderLeftWidth: destacado ? 4 : 3,
        borderLeftColor: acento,
      }}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <I name={tipo.ic} className="text-sm" style={{ color: acento }} />
          <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: acento }}>
            {tipo.lb} · {recurso.año}
          </span>
        </div>
        <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded-sm"
          style={{ background: `${nivelMeta.c}15`, color: nivelMeta.c }}>
          {nivelMeta.lb}
        </span>
      </div>

      <h3 className="ns-serif text-base font-bold leading-snug mb-1" style={{ color: "var(--ns-text)" }}>
        {recurso.titulo}
      </h3>

      <p className="ns-serif-italic text-xs mb-2" style={{ color: "var(--ns-muted)" }}>
        {recurso.autores} · <span className="ns-mono">{recurso.fuente}</span>
      </p>

      <p className="text-xs leading-relaxed mb-3" style={{ color: "var(--ns-text)" }}>
        {recurso.resumen}
      </p>

      <div className="flex flex-wrap gap-1.5 mb-3">
        {(recurso.tags || []).slice(0, 5).map(t => (
          <span key={t} className="text-[10px] px-1.5 py-0.5 rounded-sm"
            style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
            #{t}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between pt-2 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
        <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--ns-muted)" }}>
          <I name={recurso.url || recurso.doi ? "open_in_new" : "local_library"} className="text-xs" />
          {recurso.url || recurso.doi ? "Abrir referencia" : recurso.formato}
        </span>
      </div>
    </article>
  );
}
