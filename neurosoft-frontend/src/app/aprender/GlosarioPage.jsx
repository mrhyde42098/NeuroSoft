/* ═══════════════════════════════════════════════════════════════════════
 * src/app/aprender/GlosarioPage.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §M-2 — Glosario buscable de términos técnicos.
 *
 * Cada término tiene: definición extendida, ejemplo, referencias cruzadas,
 * fuente bibliográfica. Búsqueda full-text + filtros por categoría.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useMemo, useState } from "react";
import { Card, I, Input, TopBar } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { GLOSARIO, CATEGORIAS_GLOSARIO } from "../../data/aprenderContent.js";

const CAT_LABELS = {
  // Neuropsicología
  psicometria_basica: "Psicometría básica",
  psicometria_wisc: "WISC-IV",
  psicometria_wais: "WAIS-III",
  dominios_cognitivos: "Dominios cognitivos",
  neuroanatomia_funcional: "Neuroanatomía funcional",
  funciones_ejecutivas: "Funciones ejecutivas",
  lenguaje: "Lenguaje",
  memoria: "Memoria",
  escalas_psiquiatricas: "Escalas psiquiátricas",
  instrumentos_neuro: "Instrumentos neuropsicológicos",
  psicopatologia_dsm5: "Psicopatología DSM-5",
  desarrollo: "Desarrollo",
  etica_colombia: "Ética Colombia",
  // Psicología Clínica
  psicoterapia_general: "Psicoterapia general",
  psicoterapia_cognitiva: "Psicoterapia cognitiva",
  psicoterapia_conductual: "Psicoterapia conductual",
  psicoterapia_psicodinamica: "P. psicodinámica",
  psicoterapia_humanista: "P. humanista",
  psicoterapia_sistemica: "P. sistémica",
  psicopatologia: "Psicopatología",
  evaluacion_clinica: "Evaluación clínica",
  intervencion_crisis: "Intervención en crisis",
  psicofarmacologia: "Psicofarmacología",
  trauma_y_estres: "Trauma y estrés",
  terapia_pareja_familia: "Terapia pareja y familia",
  salud_mental_colombia: "Salud mental Colombia",
};

const DISCIPLINA_COLORS = {
  neuropsicologia: "#0D9488", // TEAL
  psicologia_clinica: "#7c3aed", // PURPLE
};

const TERMINO_DISCIPLINA = {};
(() => {
  const neuro = new Set([
    "psicometria_basica","psicometria_wisc","psicometria_wais",
    "dominios_cognitivos","neuroanatomia_funcional","funciones_ejecutivas",
    "lenguaje","memoria","escalas_psiquiatricas","instrumentos_neuro",
    "psicopatologia_dsm5","desarrollo","etica_colombia"
  ]);
  for (const g of GLOSARIO) {
    TERMINO_DISCIPLINA[g.termino] = neuro.has(g.categoria) ? "neuropsicologia" : "psicologia_clinica";
  }
})();

export default function GlosarioPage() {
  const [texto, setTexto] = useState("");
  const [categoria, setCategoria] = useState("");
  const [disciplina, setDisciplina] = useState("");
  const [seleccionado, setSeleccionado] = useState(null);

  const filtrados = useMemo(() => {
    const q = texto.toLowerCase().trim();
    return GLOSARIO.filter(g => {
      if (categoria && g.categoria !== categoria) return false;
      if (disciplina && TERMINO_DISCIPLINA[g.termino] !== disciplina) return false;
      if (!q) return true;
      return (
        g.termino.toLowerCase().includes(q) ||
        g.nombre_completo?.toLowerCase().includes(q) ||
        g.definicion?.toLowerCase().includes(q)
      );
    });
  }, [texto, categoria, disciplina]);

  return (
    <>
      <TopBar title="Glosario clínico" />
      <main className="p-8 max-w-6xl mx-auto space-y-5">
        <div className="flex items-center gap-3 mb-4">
          <I name="library_books" style={{ color: TEAL, fontSize: 26 }} />
          <div>
            <h2 className="ns-serif text-xl font-bold">Glosario neuropsicológico y de psicología clínica</h2>
            <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
              {GLOSARIO.length} términos · {CATEGORIAS_GLOSARIO.length} categorías ·
              Fuentes verificadas (Wechsler, Beck, Rogers, Freud, OMS, Ley 1090, etc.)
            </p>
          </div>
        </div>

        {/* Búsqueda */}
        <Card className="p-4 space-y-3">
          <div className="relative">
            <I name="search" className="absolute left-3 top-1/2 -translate-y-1/2 text-lg"
              style={{ color: "var(--ns-muted)" }} />
            <Input value={texto} onChange={e => setTexto(e.target.value)}
              placeholder="Buscar término (ej. ICV, MMSE, RCI, dislexia...)"
              style={{ paddingLeft: 38 }} />
          </div>
          <div className="flex flex-wrap gap-1.5">
            <button onClick={() => setCategoria("")}
              className="text-xs px-2.5 py-1 rounded"
              style={{
                background: !categoria ? TEAL : "var(--ns-subtle)",
                color: !categoria ? "white" : "var(--ns-muted)",
              }}>Todos</button>
            {CATEGORIAS_GLOSARIO.map(c => (
              <button key={c} onClick={() => setCategoria(c)}
                className="text-xs px-2.5 py-1 rounded"
                style={{
                  background: categoria === c ? TEAL : "var(--ns-subtle)",
                  color: categoria === c ? "white" : "var(--ns-muted)",
                }}>{CAT_LABELS[c] || c}</button>
            ))}
          </div>
          {/* Filtro por disciplina */}
          <div className="flex gap-2 pt-1 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
            <button onClick={() => setDisciplina("")}
              className="text-[10px] px-2.5 py-1 rounded-full font-bold transition-all"
              style={{
                background: !disciplina ? "var(--ns-skeleton-bg)" : "var(--ns-card)",
                color: !disciplina ? "var(--ns-text)" : "var(--ns-muted)",
                border: `1px solid ${!disciplina ? "var(--ns-card-b)" : "var(--ns-card-b-hover)"}`,
              }}>Todas las disciplinas</button>
            <button onClick={() => setDisciplina("neuropsicologia")}
              className="text-[10px] px-2.5 py-1 rounded-full font-bold transition-all"
              style={{
                background: disciplina === "neuropsicologia" ? "#0D948820" : "var(--ns-card)",
                color: disciplina === "neuropsicologia" ? "#0D9488" : "var(--ns-muted)",
                border: `1px solid ${disciplina === "neuropsicologia" ? "#0D9488" : "var(--ns-card-b-hover)"}`,
              }}>Neuropsicología</button>
            <button onClick={() => setDisciplina("psicologia_clinica")}
              className="text-[10px] px-2.5 py-1 rounded-full font-bold transition-all"
              style={{
                background: disciplina === "psicologia_clinica" ? "#7c3aed20" : "var(--ns-card)",
                color: disciplina === "psicologia_clinica" ? "#7c3aed" : "var(--ns-muted)",
                border: `1px solid ${disciplina === "psicologia_clinica" ? "#7c3aed" : "var(--ns-card-b-hover)"}`,
              }}>Psicología Clínica</button>
          </div>
        </Card>

        <div className="grid lg:grid-cols-3 gap-4">
          {/* Lista de términos */}
          <div className="lg:col-span-1 space-y-2 max-h-[70vh] overflow-auto pr-1">
            {filtrados.length === 0 && (
              <p className="text-sm italic text-center py-8" style={{ color: "var(--ns-muted)" }}>
                Sin resultados para "{texto}".
              </p>
            )}
            {filtrados.map(g => (
              <button key={g.termino} onClick={() => setSeleccionado(g)}
                className="w-full text-left p-3 rounded border transition-all"
                style={{
                  background: seleccionado?.termino === g.termino ? `${DISCIPLINA_COLORS[TERMINO_DISCIPLINA[g.termino]] || TEAL}10` : "var(--ns-card)",
                  borderColor: seleccionado?.termino === g.termino ? (DISCIPLINA_COLORS[TERMINO_DISCIPLINA[g.termino]] || TEAL) : "var(--ns-card-b)",
                }}>
                <div className="flex items-center justify-between gap-2">
                  <p className="font-bold ns-mono text-sm"
                    style={{ color: DISCIPLINA_COLORS[TERMINO_DISCIPLINA[g.termino]] || TEAL }}>
                    {g.termino}
                  </p>
                  <span className="text-[9px] uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
                    {CAT_LABELS[g.categoria] || g.categoria}
                  </span>
                </div>
                {g.nombre_completo && (
                  <p className="text-xs mt-0.5" style={{ color: "var(--ns-text)" }}>
                    {g.nombre_completo}
                  </p>
                )}
              </button>
            ))}
          </div>

          {/* Detalle */}
          <div className="lg:col-span-2">
            {seleccionado ? (
              <Card className="p-5 sticky top-24">
                <p className="ns-eyebrow mb-1" style={{ color: TEAL }}>
                  {CAT_LABELS[seleccionado.categoria] || seleccionado.categoria}
                  <span className="ml-2 text-[9px] px-1.5 py-0.5 rounded-full font-bold"
                    style={{
                      background: (DISCIPLINA_COLORS[TERMINO_DISCIPLINA[seleccionado.termino]] || TEAL) + "15",
                      color: DISCIPLINA_COLORS[TERMINO_DISCIPLINA[seleccionado.termino]] || TEAL,
                    }}>
                    {TERMINO_DISCIPLINA[seleccionado.termino] === "psicologia_clinica" ? "Psicología Clínica" : "Neuropsicología"}
                  </span>
                </p>
                <h3 className="ns-serif text-2xl font-bold mb-1">
                  <span className="ns-mono" style={{ color: TEAL }}>{seleccionado.termino}</span>
                </h3>
                {seleccionado.nombre_completo && (
                  <p className="text-base mb-4" style={{ color: "var(--ns-muted)" }}>
                    {seleccionado.nombre_completo}
                  </p>
                )}

                <p className="ns-eyebrow mb-1">Definición</p>
                <p className="text-sm leading-relaxed mb-4" style={{ color: "var(--ns-text)" }}>
                  {seleccionado.definicion}
                </p>

                {seleccionado.ejemplo && (
                  <div className="rounded p-3 mb-4" style={{ background: "var(--ns-subtle)" }}>
                    <p className="ns-eyebrow mb-1">Ejemplo clínico</p>
                    <p className="text-sm ns-serif-italic" style={{ color: "var(--ns-text)" }}>
                      {seleccionado.ejemplo}
                    </p>
                  </div>
                )}

                {seleccionado.ver_tambien?.length > 0 && (
                  <div className="mb-4">
                    <p className="ns-eyebrow mb-1.5">Ver también</p>
                    <div className="flex flex-wrap gap-1.5">
                      {seleccionado.ver_tambien.map(rel => {
                        const found = GLOSARIO.find(x => x.termino === rel);
                        return (
                          <button key={rel}
                            onClick={() => found && setSeleccionado(found)}
                            disabled={!found}
                            className="text-xs ns-mono px-2 py-1 rounded border"
                            style={{
                              borderColor: TEAL, color: TEAL,
                              opacity: found ? 1 : 0.5,
                              cursor: found ? "pointer" : "not-allowed",
                            }}>
                            {rel}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {seleccionado.fuente && (
                  <div className="border-t pt-3 mt-3" style={{ borderColor: "var(--ns-card-b)" }}>
                    <p className="ns-eyebrow mb-0.5">Fuente</p>
                    <p className="text-[11px] ns-serif-italic" style={{ color: "var(--ns-muted)" }}>
                      {seleccionado.fuente}
                    </p>
                  </div>
                )}
              </Card>
            ) : (
              <Card className="p-12 text-center" style={{ background: "var(--ns-subtle)" }}>
                <I name="touch_app" className="text-5xl opacity-30 mb-3" />
                <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
                  Selecciona un término de la lista para ver su definición completa.
                </p>
              </Card>
            )}
          </div>
        </div>
      </main>
    </>
  );
}
