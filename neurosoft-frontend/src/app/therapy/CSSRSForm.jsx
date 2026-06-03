/* ═══════════════════════════════════════════════════════════════════════
 * src/app/therapy/CSSRSForm.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §M-3 — Evaluación de riesgo suicida con C-SSRS adaptada.
 *
 * Columbia Suicide Severity Rating Scale (Posner et al., 2011) — versión
 * abreviada de tamizaje. 6 preguntas SÍ/NO que escalan en severidad.
 * El sistema calcula el nivel de riesgo automáticamente y permite añadir
 * factores protectores/de riesgo + plan de seguridad.
 *
 * Crítico: por implicaciones legales (Ley 1090 art. 36) toda evaluación
 * de riesgo se guarda inmutable en BD y aparece en el banner persistente
 * del paciente hasta que se registre una evaluación posterior.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState, useMemo } from "react";
import { api, _parseError } from "../../api/client.js";
import { Btn, I, Label, Txta } from "../../ui/primitives.jsx";
import { useToast } from "../../contexts.jsx";

/* C-SSRS abreviada — 6 preguntas + un cuestionario de intento previo.
 * Cada pregunta marca SÍ/NO. El nivel se deriva de la combinación. */
const PREGUNTAS = [
  { id: "p1", txt: "¿Ha deseado estar muerto/a o no despertar?", peso: "leve" },
  { id: "p2", txt: "¿Ha tenido pensamientos de hacerse daño a sí mismo/a?", peso: "leve" },
  { id: "p3", txt: "¿Ha pensado en cómo se haría daño (método sin plan)?", peso: "moderado" },
  { id: "p4", txt: "¿Ha tenido intención de actuar sobre esos pensamientos?", peso: "moderado" },
  { id: "p5", txt: "¿Ha comenzado a planificar cómo, cuándo o dónde?", peso: "alto" },
  { id: "p6", txt: "¿Ha hecho algo, preparado algo, o ensayado un intento (incluso si no llegó a hacerlo)?", peso: "inminente" },
];

const NIVEL_LABELS = {
  ninguno: { label: "Sin riesgo identificado", color: "var(--ns-muted)", bg: "var(--ns-subtle)" },
  leve:    { label: "Riesgo leve", color: "#92400E", bg: "rgba(180,83,9,0.10)" },
  moderado:{ label: "Riesgo moderado", color: "#9F1239", bg: "rgba(159,18,57,0.10)" },
  alto:    { label: "Riesgo alto",     color: "#7F1D1D", bg: "rgba(127,29,29,0.12)" },
  inminente:{ label: "RIESGO INMINENTE — derivar emergencia", color: "#FFFFFF", bg: "#7F1D1D" },
};

const CONTACTOS_CRISIS_DEFAULT = [
  { nombre: "Línea Nacional Salud Mental Colombia", telefono: "192 opción 4" },
  { nombre: "Línea 106 (Bogotá)", telefono: "106" },
  { nombre: "Emergencias", telefono: "123" },
];

export default function CSSRSForm({ patientId, sessionId, onSaved, onCancel }) {
  const toast = useToast();
  const [resp, setResp] = useState({}); // p1: true/false
  const [intentoPrevio, setIntentoPrevio] = useState(false);
  const [intento30d, setIntento30d] = useState(false);
  const [factoresProt, setFactoresProt] = useState("");
  const [factoresRiesgo, setFactoresRiesgo] = useState("");
  const [planSeguridad, setPlanSeguridad] = useState("");
  const [derivacion, setDerivacion] = useState(false);
  const [nota, setNota] = useState("");
  const [saving, setSaving] = useState(false);

  /* Cálculo automático del nivel.
   * Reglas:
   *   p6 SÍ              → inminente (siempre)
   *   p5 SÍ              → alto
   *   p3 o p4 SÍ         → moderado
   *   p1 o p2 SÍ         → leve
   *   ninguna SÍ         → ninguno
   *   intento_reciente_30d eleva 1 escalón mínimo a "alto"
   */
  const nivel = useMemo(() => {
    let n = "ninguno";
    if (resp.p1 || resp.p2) n = "leve";
    if (resp.p3 || resp.p4) n = "moderado";
    if (resp.p5) n = "alto";
    if (resp.p6) n = "inminente";
    if (intento30d && n !== "inminente") n = "alto";
    return n;
  }, [resp, intento30d]);

  const ideacion = !!(resp.p1 || resp.p2 || resp.p3 || resp.p4);
  const ideacionPlan = !!resp.p5;

  /* Auto-activar derivación si nivel alto o inminente */
  React.useEffect(() => {
    if (nivel === "alto" || nivel === "inminente") setDerivacion(true);
  }, [nivel]);

  const nlbl = NIVEL_LABELS[nivel];

  const guardar = async () => {
    if (Object.keys(resp).length === 0) {
      toast.error("Responde al menos las primeras preguntas antes de guardar.");
      return;
    }
    setSaving(true);
    try {
      const body = {
        patient_id: patientId,
        session_id: sessionId || null,
        instrumento: "c_ssrs",
        nivel,
        ideacion_suicida: ideacion,
        ideacion_con_plan: ideacionPlan,
        intento_previo: intentoPrevio,
        intento_reciente_30d: intento30d,
        factores_protectores: factoresProt || null,
        factores_riesgo: factoresRiesgo || null,
        plan_seguridad: planSeguridad || null,
        derivacion_emergencia: derivacion,
        nota_clinica: nota || null,
      };
      const saved = await api.post("/api/v1/therapy/risk-assessments", body);
      toast.success("Evaluación de riesgo registrada");
      onSaved && onSaved(saved);
    } catch (e) {
      toast.error(_parseError(e));
    }
    setSaving(false);
  };

  return (
    <div
      onClick={(e) => { if (e.target === e.currentTarget && !saving) onCancel(); }}
      className="fixed inset-0 z-[70] flex items-center justify-center p-4"
      style={{ background: "rgba(15,23,42,0.65)" }}
    >
      <div className="w-full max-w-3xl max-h-[92vh] rounded-lg shadow-2xl flex flex-col overflow-hidden"
        style={{ background: "var(--ns-card)" }}>
        {/* Header */}
        <div className="p-5 border-b flex items-start gap-3" style={{ borderColor: "var(--ns-card-b)" }}>
          <I name="emergency" fill style={{ color: "#9F1239", fontSize: 28 }} />
          <div className="flex-1">
            <p className="ns-eyebrow mb-1" style={{ color: "#9F1239" }}>Evaluación crítica</p>
            <h2 className="ns-serif text-xl font-bold">Escala C-SSRS (Riesgo Suicida)</h2>
            <p className="text-xs mt-1" style={{ color: "var(--ns-muted)" }}>
              Columbia Suicide Severity Rating Scale · Posner et al. (2011), versión abreviada de tamizaje.
            </p>
          </div>
          <button onClick={onCancel} disabled={saving}
            className="p-2 rounded hover:bg-gray-100" style={{ color: "var(--ns-muted)" }}>
            <I name="close" />
          </button>
        </div>

        {/* Cuerpo */}
        <div className="flex-1 overflow-auto p-5 space-y-5">
          {/* Preguntas */}
          <div>
            <Label>En las últimas 4 semanas o desde su última visita…</Label>
            <div className="space-y-2 mt-2">
              {PREGUNTAS.map((q, i) => (
                <div key={q.id} className="flex items-start gap-3 p-3 rounded border"
                  style={{
                    borderColor: resp[q.id] ? "#9F1239" : "var(--ns-card-b)",
                    background: resp[q.id] ? "rgba(159,18,57,0.04)" : "var(--ns-card)",
                  }}>
                  <span className="ns-mono text-xs font-bold mt-0.5"
                    style={{ color: resp[q.id] ? "#9F1239" : "var(--ns-muted)" }}>
                    {i + 1}
                  </span>
                  <p className="text-sm flex-1" style={{ color: "var(--ns-text)" }}>{q.txt}</p>
                  <div className="flex gap-1 shrink-0">
                    <button onClick={() => setResp(r => ({ ...r, [q.id]: false }))}
                      className="px-3 py-1 rounded text-xs font-bold border transition-colors"
                      style={{
                        background: resp[q.id] === false ? "var(--ns-subtle)" : "transparent",
                        borderColor: resp[q.id] === false ? "var(--ns-muted)" : "var(--ns-card-b)",
                        color: resp[q.id] === false ? "var(--ns-text)" : "var(--ns-muted)",
                      }}>NO</button>
                    <button onClick={() => setResp(r => ({ ...r, [q.id]: true }))}
                      className="px-3 py-1 rounded text-xs font-bold border transition-colors"
                      style={{
                        background: resp[q.id] === true ? "#9F1239" : "transparent",
                        borderColor: resp[q.id] === true ? "#9F1239" : "var(--ns-card-b)",
                        color: resp[q.id] === true ? "white" : "var(--ns-muted)",
                      }}>SÍ</button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Conducta suicida */}
          <div className="grid sm:grid-cols-2 gap-3">
            <label className="flex items-center gap-2 p-3 rounded border cursor-pointer"
              style={{ borderColor: "var(--ns-card-b)" }}>
              <input type="checkbox" checked={intentoPrevio}
                onChange={(e) => setIntentoPrevio(e.target.checked)} />
              <span className="text-sm">¿Intento suicida previo (alguna vez en su vida)?</span>
            </label>
            <label className="flex items-center gap-2 p-3 rounded border cursor-pointer"
              style={{
                borderColor: intento30d ? "#7F1D1D" : "var(--ns-card-b)",
                background: intento30d ? "rgba(127,29,29,0.08)" : "transparent",
              }}>
              <input type="checkbox" checked={intento30d}
                onChange={(e) => setIntento30d(e.target.checked)} />
              <span className="text-sm font-medium" style={{ color: intento30d ? "#7F1D1D" : "var(--ns-text)" }}>
                ¿Intento reciente (últimos 30 días)?
              </span>
            </label>
          </div>

          {/* Indicador de nivel calculado */}
          <div className="rounded-lg p-4 flex items-center gap-3"
            style={{ background: nlbl.bg, color: nlbl.color }}>
            <I name={nivel === "inminente" ? "emergency" : nivel === "alto" ? "warning" : "shield"}
              fill style={{ fontSize: 26 }} />
            <div className="flex-1">
              <p className="ns-eyebrow opacity-80">Nivel de riesgo calculado</p>
              <p className="font-bold text-base">{nlbl.label}</p>
            </div>
            {(nivel === "alto" || nivel === "inminente") && (
              <details className="text-xs">
                <summary className="cursor-pointer underline">Contactos de crisis</summary>
                <ul className="mt-2 space-y-1">
                  {CONTACTOS_CRISIS_DEFAULT.map(c => (
                    <li key={c.nombre}>{c.nombre}: <strong>{c.telefono}</strong></li>
                  ))}
                </ul>
              </details>
            )}
          </div>

          {/* Plan de seguridad */}
          <div>
            <Label>Plan de seguridad (Stanley & Brown, 2012)</Label>
            <Txta rows={4} value={planSeguridad}
              onChange={(e) => setPlanSeguridad(e.target.value)}
              placeholder={
                "Pasos co-construidos con el paciente:\n" +
                "1. Señales de alarma personales\n" +
                "2. Estrategias de afrontamiento internas\n" +
                "3. Personas y entornos que distraen\n" +
                "4. Personas a quien pedir ayuda\n" +
                "5. Profesionales / línea de crisis"
              } />
          </div>

          <div className="grid sm:grid-cols-2 gap-3">
            <div>
              <Label>Factores protectores</Label>
              <Txta rows={3} value={factoresProt} onChange={(e) => setFactoresProt(e.target.value)}
                placeholder="Razones para vivir, vínculos significativos, religión/espiritualidad, etc." />
            </div>
            <div>
              <Label>Factores de riesgo</Label>
              <Txta rows={3} value={factoresRiesgo} onChange={(e) => setFactoresRiesgo(e.target.value)}
                placeholder="Pérdida reciente, acceso a medios, aislamiento, abuso de sustancias, etc." />
            </div>
          </div>

          <div>
            <Label>Nota clínica adicional</Label>
            <Txta rows={3} value={nota} onChange={(e) => setNota(e.target.value)} />
          </div>

          <label className="flex items-center gap-2 cursor-pointer p-3 rounded border-2"
            style={{
              borderColor: derivacion ? "#9F1239" : "var(--ns-card-b)",
              background: derivacion ? "rgba(159,18,57,0.05)" : "transparent",
            }}>
            <input type="checkbox" checked={derivacion}
              onChange={(e) => setDerivacion(e.target.checked)} />
            <span className="text-sm font-bold" style={{ color: derivacion ? "#9F1239" : "var(--ns-text)" }}>
              <I name="local_hospital" className="mr-1" />
              Derivación a servicio de emergencia activada
            </span>
          </label>
        </div>

        {/* Footer */}
        <div className="p-4 border-t flex justify-end gap-2"
          style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
          <Btn variant="ghost" onClick={onCancel} disabled={saving}>Cancelar</Btn>
          <Btn onClick={guardar} disabled={saving}
            style={{
              background: nivel === "inminente" ? "#7F1D1D" : nivel === "alto" ? "#9F1239" : "#0D9488",
              color: "#fff",
              borderColor: nivel === "inminente" ? "#7F1D1D" : nivel === "alto" ? "#9F1239" : "#0D9488",
            }}>
            {saving ? "Guardando…" : <><I name="save" className="mr-1.5" />Registrar evaluación</>}
          </Btn>
        </div>
      </div>
    </div>
  );
}
