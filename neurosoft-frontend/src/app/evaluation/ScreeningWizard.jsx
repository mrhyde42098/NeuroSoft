/* Wizard de motivo de consulta — sugerencias clínicas (no prescriptivas) */
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
  getFormsPorConstructo,
  sugerirPorConstructos,
  getScreeningMetadata,
} from "../../data/screening.js";

const MOTIVOS = [
  { id: "queja_memoria", label: "Queja de memoria", icon: "memory", constructos: ["depresion", "cognitivo_global"] },
  { id: "tdah_infantil", label: "TDAH (niño/a)", icon: "bolt", constructos: ["tdah_infantil"] },
  { id: "tdah_adulto", label: "TDAH (adulto)", icon: "self_improvement", constructos: ["tdah_adulto"] },
  { id: "depresion", label: "Síntomas depresivos", icon: "sentiment_very_dissatisfied", constructos: ["depresion"] },
  { id: "ansiedad", label: "Síntomas ansiosos", icon: "mood_bad", constructos: ["ansiedad"] },
  { id: "tea", label: "Sospecha TEA (≤30 m)", icon: "visibility", constructos: ["tea_early_screening"] },
  { id: "deterioro_cognitivo", label: "Deterioro cognitivo", icon: "psychology", constructos: ["cognitivo_global", "demencia_severidad", "funcionalidad_instrum"] },
  { id: "neuropsiquiatria", label: "Síntomas neuropsiquiátricos", icon: "psychology_alt", constructos: ["neuropsiquiatria"] },
  { id: "sobrecarga_cuidador", label: "Sobrecarga del cuidador", icon: "volunteer_activism", constructos: ["sobrecarga_cuidador"] },
  { id: "trauma_ptsd", label: "Trauma / TEPT", icon: "crisis_alert", constructos: ["trauma_ptsd"] },
  { id: "funcionalidad", label: "Pérdida funcional", icon: "accessibility_new", constructos: ["funcionalidad_basica", "funcionalidad_instrum"] },
  { id: "tdah_escolar", label: "Conducta escolar", icon: "school", constructos: ["tdah_escolar"] },
];

const MOTIVOS_KEYWORDS = {
  tdah: ["tdah", "atencion", "atención", "hiperactividad", "impulsividad", "concentracion", "concentración", "tdah_infantil", "tdah_adulto", "tdah_escolar"],
  memoria: ["memoria", "olvido", "demencia", "alzheimer", "deterioro", "mci", "dcl", "queja_memoria"],
  depresion: ["depresion", "depresión", "tristeza", "animo bajo", "ánimo bajo", "anhedonia", "deprimido"],
  ansiedad: ["ansiedad", "preocupacion", "preocupación", "panico", "pánico", "fobia", "ansioso"],
  tea: ["tea", "autismo", "autista", "espectro", "asd"],
  trauma: ["trauma", "ptsd", "tept", "estres post", "estrés post", "violencia", "abuso"],
  cuidador: ["cuidador", "burnout", "carga", "sobrecarga"],
  funcionalidad: ["funcionalidad", "actividades diarias", "avd", "iadv"],
  neuropsiquiatria: ["agresividad", "agitacion", "agitación", "delirios", "alucinaciones", "apraxia"],
};

function keywordsPorMotivos(motivosSeleccionados) {
  const set = new Set();
  for (const m of motivosSeleccionados) {
    const found = Object.entries(MOTIVOS_KEYWORDS).find(([, kws]) => kws.includes(m.id));
    if (found) set.add(found[0]);
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
    const protocolo = sugerenciaProtocolo(edad, keywords, escolaridad || null);
    const extendido = sugerenciaQuejaMemoria(keywords);
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
      toast.warn("Seleccione al menos un motivo de consulta");
      return;
    }
    setLastRun({ edad, motivos: motivosIds.slice(), escolaridad, esCuidador, recomendaciones });
  };

  const handlePick = (testId) => {
    if (onPickTest) onPickTest(testId);
    else toast.info(`Instrumento sugerido: ${testId}`);
  };

  return (
    <Card className="p-5 border-l-4" style={{ borderLeftColor: TEAL, background: "var(--ns-card)" }}>
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <I name="route" className="text-lg" style={{ color: TEAL }} />
        <h3 className="font-bold text-sm" style={{ color: "var(--ns-text)" }}>Orientador por motivo de consulta</h3>
        <span className="text-[10px] px-2 py-0.5 rounded-full font-semibold ml-auto"
          style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
          Sugerencia clínica · usted decide
        </span>
      </div>

      <p className="text-xs mb-4 leading-relaxed" style={{ color: "var(--ns-muted)" }}>
        Indique edad y motivos. NeuroSoft propone protocolo cognitivo y escalas coherentes con la queja;
        puede aceptar, modificar o ignorar cada sugerencia.
      </p>

      <div className="grid sm:grid-cols-3 gap-3 mb-4">
        <div>
          <Label>Edad del paciente</Label>
          <input type="number" min="0" max="120" value={edad}
            onChange={(e) => setEdad(parseInt(e.target.value || "0", 10))}
            className="w-full px-3 py-2.5 rounded-xl text-sm border"
            style={{ background: "var(--ns-input)", color: "var(--ns-text)", borderColor: "var(--ns-card-b)" }} />
        </div>
        <div>
          <Label>Escolaridad (opcional)</Label>
          <Sel value={escolaridad} onChange={(e) => setEscolaridad(e.target.value)}>
            <option value="">— Sin especificar —</option>
            {["Analfabeta", "Primaria incompleta", "Primaria completa", "Secundaria incompleta", "Secundaria completa", "Universitaria", "Posgrado"].map((o) => (
              <option key={o} value={o}>{o}</option>
            ))}
          </Sel>
        </div>
        <div className="flex items-end">
          <label className="flex items-start gap-2 text-xs cursor-pointer p-2 rounded-xl border w-full"
            style={{ borderColor: esCuidador ? TEAL : "var(--ns-card-b)", background: esCuidador ? `${TEAL}08` : "transparent" }}>
            <input type="checkbox" className="mt-0.5" checked={esCuidador} onChange={(e) => setEsCuidador(e.target.checked)} />
            <span>
              <strong>Informante cuidador</strong>
              <span className="block text-[10px] mt-0.5 opacity-80">Quien responde es familiar o cuidador (ej. Zarit, NPI-Q)</span>
            </span>
          </label>
        </div>
      </div>

      <Label>Motivo(s) de consulta</Label>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 mb-4">
        {MOTIVOS.map((m) => {
          const activo = motivosIds.includes(m.id);
          return (
            <button key={m.id} type="button" onClick={() => toggleMotivo(m.id)}
              className="px-3 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition-all text-left border"
              style={activo
                ? { background: TEAL, color: "#fff", borderColor: TEAL }
                : { background: "var(--ns-subtle)", color: "var(--ns-text)", borderColor: "var(--ns-card-b)" }}>
              <I name={m.icon} className="text-base shrink-0" />
              <span className="leading-snug">{m.label}</span>
            </button>
          );
        })}
      </div>

      <div className="flex justify-end mb-4">
        <Btn onClick={handleCalcular} className="!min-h-[44px]">
          <I name="search" className="text-base" /> Ver sugerencias
        </Btn>
      </div>

      {lastRun?.recomendaciones && (
        <div className="space-y-3 border-t pt-4" style={{ borderColor: "var(--ns-card-b)" }}>
          {lastRun.recomendaciones.protocolo ? (
            <ResultBlock icon="psychology" title={`Protocolo: ${lastRun.recomendaciones.protocolo.protocolo}`}
              badge={`≈${lastRun.recomendaciones.duracionProtocoloMin} min`}
              desc={lastRun.recomendaciones.protocolo.justificacion}>
              {lastRun.recomendaciones.protocolo.testIds.map((tid) => (
                <TestChip key={tid} testId={tid} onPick={handlePick} />
              ))}
            </ResultBlock>
          ) : (
            <p className="text-xs italic" style={{ color: "var(--ns-muted)" }}>
              Sin batería cognitiva sugerida para esta edad/motivo. Revise WISC-IV (&lt;17 años) o WAIS-III (≥17 años) en Evaluación.
            </p>
          )}
          {lastRun.recomendaciones.extendido?.length > 0 && (
            <ResultBlock icon="elderly" title="Ampliación por queja de memoria">
              {lastRun.recomendaciones.extendido.map((t) => (
                <TestChip key={t.testId} testId={t.testId} onPick={handlePick} razon={t.razon} />
              ))}
            </ResultBlock>
          )}
          {lastRun.recomendaciones.screenIds.length > 0 && (
            <ResultBlock icon="quiz" title={`Escalas sugeridas (${lastRun.recomendaciones.screenIds.length})`}
              desc={lastRun.recomendaciones.constructos.map((c) => CONSTRUCTOS[c]?.label || c).join(" · ")}>
              {lastRun.recomendaciones.screenIds.map((tid) => (
                <TestChip key={tid} testId={tid} onPick={handlePick} />
              ))}
            </ResultBlock>
          )}
        </div>
      )}
    </Card>
  );
}

function ResultBlock({ icon, title, badge, desc, children }) {
  return (
    <div className="p-3 rounded-xl border" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
      <div className="flex items-center gap-2 mb-2 flex-wrap">
        <I name={icon} style={{ color: TEAL }} />
        <span className="text-sm font-bold">{title}</span>
        {badge && (
          <span className="text-[10px] px-2 py-0.5 rounded-full font-semibold ml-auto" style={{ background: `${TEAL}20`, color: TEAL }}>
            {badge}
          </span>
        )}
      </div>
      {desc && <p className="text-[11px] mb-2" style={{ color: "var(--ns-muted)" }}>{desc}</p>}
      <div className="flex flex-wrap gap-1.5">{children}</div>
    </div>
  );
}

function TestChip({ testId, onPick, razon = null }) {
  const meta = getScreeningMetadata(testId);
  const fromForm = SCREENING_FORMS[testId];
  if (!fromForm) {
    return (
      <button type="button" onClick={() => onPick(testId)} title={razon || ""}
        className="px-2.5 py-1.5 rounded-lg text-[11px] font-bold border"
        style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
        {testId}
      </button>
    );
  }
  const color = meta?.constructo?.color || TEAL;
  return (
    <button type="button" onClick={() => onPick(testId)} title={razon || fromForm.name}
      className="px-2.5 py-1.5 rounded-lg text-[11px] font-bold flex items-center gap-1 border"
      style={{ background: `${color}12`, color, borderColor: `${color}35` }}>
      <I name="north_east" className="text-xs" />
      {fromForm.abbr || testId}
    </button>
  );
}

function construirListaScreenings(constructos, edad, esCuidador) {
  const set = new Set();
  for (const c of constructos) {
    for (const id of getFormsPorConstructo(c)) set.add(id);
  }
  if (esCuidador) {
    for (const id of sugerirPorConstructos(["sobrecarga_cuidador"], edad, true)) set.add(id);
  }
  return Array.from(set).slice(0, 8);
}
