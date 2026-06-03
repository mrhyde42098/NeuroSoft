/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/ScreeningWizard.jsx — Wizard de motivo de consulta
 * ───────────────────────────────────────────────────────────────────────
 * F8.2 — Reusa:
 *   - sugerenciaProtocolo(edad, motivos, escolaridad)        (protocolLoader)
 *   - sugerenciaQuejaMemoria(motivos)                        (protocolLoader)
 *   - sugerirPorConstructos(constructos, edad, esCuidador)   (screening)
 *   - tiempoTotalEstimado(testIds)                           (protocolLoader)
 *
 * El wizard NO agrega tests al plan automáticamente; sugiere chips
 * accionables que el clínico confirma manualmente. Esto preserva el
 * principio ético P4 (lenguaje descriptivo, no definitivo) — el
 * sistema no prescribe, sugiere.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useMemo, useState } from "react";
import { Btn, Card, I, Label, Sel } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { useToast } from "../../contexts.jsx";
import {
  sugerenciaProtocolo,
  sugerenciaQuejaMemoria,
  tiempoTotalEstimado,
} from "../../data/protocolLoader.js";
import {
  CONSTRUCTOS,
  SCREENING_FORMS,
  SCREENING_INDEX,
  getFormsPorConstructo,
  sugerirPorConstructos,
  getScreeningMetadata,
} from "../../data/screening.js";

/* ── Catálogo de motivos de consulta normalizados → constructos ── */
const MOTIVOS = [
  { id: "queja_memoria",   label: "Queja de memoria",          icon: "memory",      constructos: ["depresion", "cognitivo_global"] },
  { id: "tdah_infantil",   label: "Sospecha TDAH (niño)",     icon: "bolt",        constructos: ["tdah_infantil"] },
  { id: "tdah_adulto",     label: "Sospecha TDAH (adulto)",   icon: "self_improvement", constructos: ["tdah_adulto"] },
  { id: "depresion",       label: "Síntomas depresivos",      icon: "sentiment_very_dissatisfied", constructos: ["depresion"] },
  { id: "ansiedad",        label: "Síntomas ansiosos",        icon: "mood_bad",    constructos: ["ansiedad"] },
  { id: "tea",             label: "Sospecha TEA (≤30m)",      icon: "visibility",  constructos: ["tea_early_screening"] },
  { id: "deterioro_cognitivo", label: "Deterioro cognitivo",  icon: "psychology",  constructos: ["cognitivo_global", "demencia_severidad", "funcionalidad_instrum"] },
  { id: "neuropsiquiatria",    label: "Síntomas neuropsiquiátricos", icon: "psychology_alt", constructos: ["neuropsiquiatria"] },
  { id: "sobrecarga_cuidador", label: "Sobrecarga del cuidador", icon: "volunteer_activism", constructos: ["sobrecarga_cuidador"] },
  { id: "trauma_ptsd",         label: "Trauma / PTSD",        icon: "crisis_alert", constructos: ["trauma_ptsd"] },
  { id: "funcionalidad",       label: "Pérdida funcionalidad", icon: "accessibility_new", constructos: ["funcionalidad_basica", "funcionalidad_instrum"] },
  { id: "tdah_escolar",        label: "Comportamiento escolar", icon: "school",     constructos: ["tdah_escolar"] },
];

const MOTIVOS_KEYWORDS = {
  tdah: ["tdah", "atencion", "atención", "hiperactividad", "impulsividad", "concentracion", "concentración", "tdah_infantil", "tdah_adulto", "tdah_escolar"],
  memoria: ["memoria", "olvido", "demencia", "alzheimer", "deterioro", "mci", "dcl", "queja_memoria"],
  depresion: ["depresion", "depresión", "tristeza", "animo bajo", "ánimo bajo", "anhedonia", "deprimido"],
  ansiedad: ["ansiedad", "preocupacion", "preocupación", "panico", "pánico", "fobia", "ansioso"],
  tea: ["tea", "autismo", "autista", "espectro", "asd"],
  trauma: ["trauma", "ptsd", "estres post", "estrés post", "violencia", "abuso"],
  cuidador: ["cuidador", "burnout", "carga", "sobrecarga"],
  funcionalidad: ["funcionalidad", "actividades diarias", "avd", "iadv"],
  neuropsiquiatria: ["agresividad", "agitacion", "agitación", "delirios", "alucinaciones", "apraxia"],
};

function motivosTocan(constructo) {
  /* Devuelve los motivos del catálogo que disparan ``constructo``. */
  return MOTIVOS.filter((m) => m.constructos.includes(constructo));
}

function keywordsPorMotivos(motivosSeleccionados) {
  /* Combina los keywords de los motivos seleccionados (sirve para
     alimentar sugerenciaProtocolo que también espera keywords). */
  const set = new Set();
  for (const m of motivosSeleccionados) {
    const found = Object.entries(MOTIVOS_KEYWORDS).find(([_, kws]) => kws.includes(m.id));
    if (found) set.add(found[0]);
    /* Si el id del motivo ya coincide con un keyword, también lo añade. */
    set.add(m.id);
  }
  return Array.from(set);
}

export default function ScreeningWizard({ onPickTest, edadInicial = null }) {
  const toast = useToast();
  const [edad, setEdad] = useState(edadInicial || 35);
  const [motivosIds, setMotivosIds] = useState([]);
  const [escolaridad, setEscolaridad] = useState("");
  const [esCuidador, setEsCuidador] = useState(false);
  const [lastRun, setLastRun] = useState(null);

  const toggleMotivo = (id) => {
    setMotivosIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const recomendaciones = useMemo(() => {
    if (motivosIds.length === 0 && !esCuidador) return null;
    const motivosObj = MOTIVOS.filter((m) => motivosIds.includes(m.id));
    const keywords = keywordsPorMotivos(motivosObj);

    /* 1) Protocolo cognitivo (WISC-IV / WAIS-III / extendido queja memoria) */
    const protocolo = sugerenciaProtocolo(edad, keywords, escolaridad || null);
    const extendido = sugerenciaQuejaMemoria(keywords);

    /* 2) Constructos psicológicos a partir de los motivos elegidos. */
    const constructos = Array.from(new Set(motivosObj.flatMap((m) => m.constructos)));
    const screenIds = construirListaScreenings(constructos, edad, esCuidador);

    return {
      protocolo,
      extendido,
      constructos,
      screenIds,
      duracionProtocoloMin: protocolo ? tiempoTotalEstimado(protocolo.testIds) : 0,
    };
  }, [edad, motivosIds, escolaridad, esCuidador]);

  const handleCalcular = () => {
    if (motivosIds.length === 0 && !esCuidador) {
      toast("Selecciona al menos un motivo de consulta", "warn");
      return;
    }
    setLastRun({
      edad,
      motivos: motivosIds.slice(),
      escolaridad,
      esCuidador,
      recomendaciones,
    });
  };

  const handlePick = (testId) => {
    if (onPickTest) onPickTest(testId);
    else toast(`Test sugerido: ${testId} (no hay handler conectado)`, "info");
  };

  return (
    <Card className="p-5" style={{ borderLeft: `4px solid ${TEAL}` }}>
      <div className="flex items-center gap-2 mb-4">
        <I name="auto_awesome" className="text-lg" style={{ color: TEAL }} />
        <h3 className="font-bold text-sm" style={{ color: "var(--ns-text)" }}>
          Asistente de selección
        </h3>
        <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full font-semibold"
          style={{ background: `${TEAL}15`, color: TEAL }}>
          F8.2 · Sugerencia (no prescribe)
        </span>
      </div>

      <p className="text-xs mb-4" style={{ color: "var(--ns-muted)" }}>
        Marca los motivos de consulta y la edad. El asistente sugerirá una batería inicial.
        Puedes ignorar la sugerencia y elegir manualmente.
      </p>

      {/* Edad + escolaridad + cuidador */}
      <div className="grid sm:grid-cols-3 gap-3 mb-4">
        <div>
          <Label>Edad del paciente</Label>
          <input type="number" min="0" max="120" value={edad}
            onChange={(e) => setEdad(parseInt(e.target.value || "0", 10))}
            className="w-full px-3 py-2 rounded-lg text-sm"
            style={{ background: "var(--ns-card)", color: "var(--ns-text)", border: "1px solid var(--ns-card-b)" }} />
        </div>
        <div>
          <Label>Escolaridad (opcional)</Label>
          <Sel value={escolaridad} onChange={(e) => setEscolaridad(e.target.value)}>
            <option value="">— Sin especificar —</option>
            <option value="Analfabeta">Analfabeta</option>
            <option value="Primaria incompleta">Primaria incompleta</option>
            <option value="Primaria completa">Primaria completa</option>
            <option value="Secundaria incompleta">Secundaria incompleta</option>
            <option value="Secundaria completa">Secundaria completa</option>
            <option value="Universitaria">Universitaria</option>
            <option value="Posgrado">Posgrado</option>
          </Sel>
        </div>
        <div className="flex items-end">
          <label className="flex items-center gap-2 text-xs cursor-pointer"
            style={{ color: "var(--ns-text)" }}>
            <input type="checkbox" checked={esCuidador} onChange={(e) => setEsCuidador(e.target.checked)} />
            Responde un cuidador (proxy)
          </label>
        </div>
      </div>

      {/* Motivos */}
      <Label>Motivo(s) de consulta</Label>
      <div className="flex flex-wrap gap-2 mb-4">
        {MOTIVOS.map((m) => {
          const activo = motivosIds.includes(m.id);
          return (
            <button key={m.id} type="button" onClick={() => toggleMotivo(m.id)}
              className="px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all"
              style={activo
                ? { background: TEAL, color: "#fff" }
                : { background: "var(--ns-subtle)", color: "var(--ns-muted)", border: "1px solid var(--ns-card-b)" }}>
              <I name={m.icon} className="text-sm" />
              {m.label}
            </button>
          );
        })}
      </div>

      <div className="flex justify-end mb-4">
        <Btn variant="primary" onClick={handleCalcular}>
          <I name="auto_awesome" className="text-base" /> Calcular sugerencia
        </Btn>
      </div>

      {/* Resultados */}
      {lastRun && lastRun.recomendaciones && (
        <div className="space-y-3">
          {/* Protocolo cognitivo */}
          {lastRun.recomendaciones.protocolo ? (
            <div className="p-3 rounded-lg" style={{ background: "var(--ns-subtle)" }}>
              <div className="flex items-center gap-2 mb-2">
                <I name="psychology" style={{ color: TEAL }} />
                <span className="text-sm font-bold" style={{ color: "var(--ns-text)" }}>
                  Protocolo sugerido: {lastRun.recomendaciones.protocolo.protocolo}
                </span>
                <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full font-semibold"
                  style={{ background: `${TEAL}20`, color: TEAL }}>
                  ≈{lastRun.recomendaciones.duracionProtocoloMin} min
                </span>
              </div>
              <p className="text-[11px] mb-2" style={{ color: "var(--ns-muted)" }}>
                {lastRun.recomendaciones.protocolo.justificacion}
              </p>
              <div className="flex flex-wrap gap-1.5">
                {lastRun.recomendaciones.protocolo.testIds.map((tid) => (
                  <TestChip key={tid} testId={tid} onPick={handlePick} />
                ))}
              </div>
            </div>
          ) : (
            <p className="text-xs italic" style={{ color: "var(--ns-muted)" }}>
              Sin sugerencia de protocolo cognitivo para esta combinación de edad y motivo.
              Aplicar el protocolo por edad (WISC-IV si &lt;17a, WAIS-III si ≥17a).
            </p>
          )}

          {/* Queja memoria extendida */}
          {lastRun.recomendaciones.extendido && (
            <div className="p-3 rounded-lg" style={{ background: "var(--ns-subtle)" }}>
              <div className="flex items-center gap-2 mb-2">
                <I name="elderly" style={{ color: TEAL }} />
                <span className="text-sm font-bold" style={{ color: "var(--ns-text)" }}>
                  Batería extendida sugerida (queja de memoria)
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {lastRun.recomendaciones.extendido.map((t) => (
                  <TestChip key={t.testId} testId={t.testId} onPick={handlePick} razon={t.razon} />
                ))}
              </div>
            </div>
          )}

          {/* Screenings por constructo */}
          {lastRun.recomendaciones.screenIds.length > 0 ? (
            <div className="p-3 rounded-lg" style={{ background: "var(--ns-subtle)" }}>
              <div className="flex items-center gap-2 mb-2">
                <I name="quiz" style={{ color: TEAL }} />
                <span className="text-sm font-bold" style={{ color: "var(--ns-text)" }}>
                  Screenings sugeridos ({lastRun.recomendaciones.screenIds.length})
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {lastRun.recomendaciones.screenIds.map((tid) => (
                  <TestChip key={tid} testId={tid} onPick={handlePick} />
                ))}
              </div>
              {lastRun.recomendaciones.constructos.length > 0 && (
                <p className="text-[11px] mt-2" style={{ color: "var(--ns-muted)" }}>
                  Basado en constructos: {lastRun.recomendaciones.constructos
                    .map((c) => CONSTRUCTOS[c]?.label || c).join(" · ")}
                </p>
              )}
            </div>
          ) : null}
        </div>
      )}
    </Card>
  );
}

/* ── Chip accionable de un test ────────────────────────────────── */
function TestChip({ testId, onPick, razon = null }) {
  const meta = getScreeningMetadata(testId);
  const fromForm = SCREENING_FORMS[testId];
  if (!fromForm) {
    return (
      <button onClick={() => onPick(testId)} title={razon || ""}
        className="px-2 py-1 rounded text-[11px] font-semibold"
        style={{ background: "var(--ns-card)", color: "var(--ns-text)", border: "1px solid var(--ns-card-b)" }}>
        {testId}
      </button>
    );
  }
  const color = meta?.constructo?.color || TEAL;
  return (
    <button onClick={() => onPick(testId)} title={razon || fromForm.name}
      className="px-2 py-1 rounded text-[11px] font-semibold flex items-center gap-1"
      style={{ background: `${color}15`, color, border: `1px solid ${color}40` }}>
      <I name="play_arrow" className="text-xs" />
      {fromForm.abbr || testId}
    </button>
  );
}

/* ── Helper: union de screenings por constructo filtrados por edad ── */
function construirListaScreenings(constructos, edad, esCuidador) {
  /* Une las sugerencias por constructo, deduplica y limita a 8
     (un panel con >8 chips es ruido). */
  const set = new Set();
  for (const c of constructos) {
    for (const id of getFormsPorConstructo(c)) set.add(id);
  }
  const porEdad = new Set(sugerirPorConstructos(constructos, edad, esCuidador));
  const interseccion = Array.from(set).filter((id) => porEdad.has(id));
  if (interseccion.length > 0) return interseccion.slice(0, 8);
  /* Si la intersección está vacía (motivos sin tests para esa edad),
     devolver los del constructo sin filtrar para que el clínico
     vea opciones. */
  return Array.from(set).slice(0, 8);
}

/* ── Re-exports para tests externos ────────────────────────────── */
export { MOTIVOS, MOTIVOS_KEYWORDS, motivosTocan, construirListaScreenings };
