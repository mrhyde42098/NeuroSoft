/* ═══════════════════════════════════════════════════════════════════════
 * src/app/therapy/SesionSOAPForm.jsx — Modal de creación/edición de sesión
 * ───────────────────────────────────────────────────────────────────────
 * Formulario tipo "split-view editorial" con las 4 secciones SOAP:
 *   S — Subjetivo (lo que el paciente reporta)
 *   O — Objetivo  (lo que el clínico observa)
 *   A — Análisis  (interpretación clínica)
 *   P — Plan      (próximos pasos)
 *
 * Plus: modalidad, riesgo suicida, alianza terapéutica, estado emocional
 * inicio/fin. Botón "Firmar y cerrar sesión" → lock irreversible.
 *
 * NO usa cards saturadas. Estilo editorial: columnas, etiquetas SOAP grandes
 * con sigla en serif, separadores horizontales sutiles.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { Btn, I, Sel, Txta } from "../../ui/primitives.jsx";
import { TEAL, NAVY, ACCENTS } from "../../ui/tokens.js";
import { useToast, useConfirm } from "../../contexts.jsx";
import TareasTerapeuticasPanel from "./TareasTerapeuticasPanel.jsx";

const PLUM = ACCENTS.plum;

const MODALIDADES = [
  { id: "presencial",    label: "Presencial" },
  { id: "telepsicologia", label: "Telepsicología" },
  { id: "telefonica",    label: "Telefónica" },
];

const RIESGO_OPCIONES = [
  { id: "ninguno",          label: "Sin riesgo",      color: "var(--ns-muted)" },
  { id: "ideacion_pasiva",  label: "Ideación pasiva", color: "#92400E" },
  { id: "ideacion_activa",  label: "Ideación activa", color: "#9F1239" },
  { id: "plan",             label: "Plan suicida",    color: "#7F1D1D" },
  { id: "intento_reciente", label: "Intento reciente",color: "#7F1D1D" },
];

const SOAP_SECCIONES = [
  { key: "soap_subjetivo", letter: "S", label: "Subjetivo",
    hint: "Lo que el paciente reporta sobre cómo se ha sentido desde la última sesión." },
  { key: "soap_objetivo", letter: "O", label: "Objetivo",
    hint: "Lo que tú observas: presentación, afecto, conducta no verbal, indicadores objetivos." },
  { key: "soap_analisis", letter: "A", label: "Análisis",
    hint: "Tu interpretación clínica: hipótesis, conexión con el plan, progreso, obstáculos." },
  { key: "soap_plan",     letter: "P", label: "Plan",
    hint: "Próximos pasos: tareas asignadas, foco de la siguiente sesión, ajustes de tratamiento." },
];

export default function SesionSOAPForm({ sessionId, patientId, planId, onSaved, onCancel }) {
  const toast = useToast();
  const confirm = useConfirm();
  const [loading, setLoading] = useState(!!sessionId);
  const [saving, setSaving] = useState(false);
  const [locking, setLocking] = useState(false);
  const [form, setForm] = useState({
    patient_id: patientId,
    plan_id: planId || null,
    modalidad: "presencial",
    duracion_min: 50,
    soap_subjetivo: "",
    soap_objetivo: "",
    soap_analisis: "",
    soap_plan: "",
    tareas_asignadas: "",
    medicacion_actual: "",
    riesgo_suicida: "ninguno",
    riesgo_observaciones: "",
    alianza_terapeutica: null,
    estado_emocional_ini: null,
    estado_emocional_fin: null,
  });
  const [lockedAt, setLockedAt] = useState(null);

  /* Carga si es edición */
  useEffect(() => {
    if (!sessionId) return;
    api.get(`/api/v1/therapy/sessions/${sessionId}`)
      .then(d => {
        setForm(prev => ({ ...prev, ...d }));
        setLockedAt(d.locked_at || null);
        setLoading(false);
      })
      .catch(e => { toast.error(_parseError(e)); setLoading(false); });
  }, [sessionId, toast]);

  const isLocked = !!lockedAt;
  const set = (k, v) => !isLocked && setForm(f => ({ ...f, [k]: v }));

  const guardar = async () => {
    setSaving(true);
    try {
      if (sessionId) {
        const d = await api.patch(`/api/v1/therapy/sessions/${sessionId}`, {
          soap_subjetivo: form.soap_subjetivo, soap_objetivo: form.soap_objetivo,
          soap_analisis: form.soap_analisis, soap_plan: form.soap_plan,
          tareas_asignadas: form.tareas_asignadas, medicacion_actual: form.medicacion_actual,
          riesgo_suicida: form.riesgo_suicida, riesgo_observaciones: form.riesgo_observaciones,
          alianza_terapeutica: form.alianza_terapeutica,
          estado_emocional_ini: form.estado_emocional_ini, estado_emocional_fin: form.estado_emocional_fin,
        });
        onSaved?.(d);
      } else {
        const d = await api.post("/api/v1/therapy/sessions", form);
        onSaved?.(d);
      }
    } catch (e) { toast.error(_parseError(e)); }
    setSaving(false);
  };

  const firmar = async () => {
    if (!sessionId) {
      toast.warn("Guarda la sesión primero antes de firmarla.");
      return;
    }
    if (!(await confirm({
      title: "Firmar sesión",
      message: "Una vez firmada, la sesión queda inmutable (Resolución 1995 / 2014).\nNo podrás editar S-O-A-P, riesgo ni tareas asignadas después.",
      confirmText: "Firmar",
      dangerous: true,
    }))) return;
    setLocking(true);
    try {
      const d = await api.post(`/api/v1/therapy/sessions/${sessionId}/lock`);
      setLockedAt(d.locked_at);
      onSaved?.(d);
      toast.success("Sesión firmada correctamente.");
    } catch (e) { toast.error(_parseError(e)); }
    setLocking(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(15,23,42,0.55)", backdropFilter: "blur(2px)" }}
      onClick={onCancel}>
      <div onClick={e => e.stopPropagation()}
        className="w-full max-w-4xl max-h-[92vh] rounded-lg shadow-2xl flex flex-col overflow-hidden"
        style={{ background: "var(--ns-card)" }}>
        {/* Header */}
        <div className="px-6 py-4 border-b flex items-center justify-between"
          style={{ borderColor: "var(--ns-card-b)" }}>
          <div>
            <p className="ns-eyebrow" style={{ color: PLUM }}>Sesión terapéutica</p>
            <h3 className="ns-serif text-xl font-bold mt-0.5">
              {sessionId ? (isLocked ? "Sesión firmada" : "Editar sesión") : "Nueva sesión"}
            </h3>
            {isLocked && (
              <p className="text-[11px] mt-1" style={{ color: "var(--ns-muted)" }}>
                <I name="lock" className="text-xs mr-1" style={{ color: TEAL }} />
                Firmada el {new Date(lockedAt).toLocaleString("es-CO")} · solo lectura
              </p>
            )}
          </div>
          <button onClick={onCancel} aria-label="Cerrar formulario"
            className="p-2 rounded-md hover:bg-gray-100" style={{ color: "var(--ns-muted)" }}>
            <I name="close" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-auto p-6 space-y-6">
          {loading ? (
            <div className="text-center py-12" style={{ color: "var(--ns-muted)" }}>
              <div className="inline-block animate-spin w-6 h-6 border-2 border-current border-t-transparent rounded-full" />
            </div>
          ) : (
            <>
              {/* Modalidad + duración + estado emocional */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="ns-eyebrow mb-1.5">Modalidad</p>
                  <Sel value={form.modalidad} onChange={e => set("modalidad", e.target.value)} disabled={isLocked}>
                    {MODALIDADES.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
                  </Sel>
                  {/* §M-4 Telepsicología: link a sala Jitsi y consentimiento */}
                  {form.modalidad === "telepsicologia" && (
                    <TelepsicologiaTools sessionId={sessionId} isLocked={isLocked} />
                  )}
                </div>
                <div>
                  <p className="ns-eyebrow mb-1.5">Duración (min)</p>
                  <input type="number" min="5" max="240" value={form.duracion_min}
                    onChange={e => set("duracion_min", parseInt(e.target.value, 10) || 50)}
                    disabled={isLocked}
                    className="w-full px-3 py-2 rounded-md text-sm"
                    style={{ background: "var(--ns-input)", border: "1px solid var(--ns-card-b)", color: "var(--ns-text)" }} />
                </div>
                <div>
                  <p className="ns-eyebrow mb-1.5">Alianza (1-5, auto-evaluación clínica)</p>
                  <Sel value={form.alianza_terapeutica || ""}
                    onChange={e => set("alianza_terapeutica", e.target.value ? parseInt(e.target.value, 10) : null)}
                    disabled={isLocked}>
                    <option value="">— Sin evaluar —</option>
                    {[1,2,3,4,5].map(n => <option key={n} value={n}>{n} {n===5?"(excelente)":n===1?"(muy baja)":""}</option>)}
                  </Sel>
                </div>
              </div>

              {/* SOAP — sección editorial */}
              <div className="space-y-5">
                {SOAP_SECCIONES.map(s => (
                  <div key={s.key} className="ns-section-rule pl-5">
                    <div className="flex items-baseline gap-3 mb-2">
                      <span className="ns-serif text-3xl font-bold leading-none" style={{ color: PLUM }}>
                        {s.letter}
                      </span>
                      <div>
                        <h4 className="font-bold text-sm uppercase tracking-wide" style={{ color: "var(--ns-text)" }}>
                          {s.label}
                        </h4>
                        <p className="text-[11px] mt-0.5" style={{ color: "var(--ns-muted)" }}>{s.hint}</p>
                      </div>
                    </div>
                    <Txta value={form[s.key] || ""} onChange={e => set(s.key, e.target.value)}
                      disabled={isLocked} rows={3}
                      placeholder={`Notas del bloque ${s.label.toLowerCase()}…`}
                      className="text-sm" />
                  </div>
                ))}
              </div>

              {/* Estado emocional */}
              <div className="grid grid-cols-2 gap-4 pt-2 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
                <div className="pt-4">
                  <p className="ns-eyebrow mb-1.5">Estado emocional al INICIO (0–10)</p>
                  <input type="range" min="0" max="10" value={form.estado_emocional_ini ?? 5}
                    onChange={e => set("estado_emocional_ini", parseInt(e.target.value, 10))}
                    disabled={isLocked}
                    className="w-full" style={{ accentColor: PLUM }} />
                  <p className="text-xs mt-1" style={{ color: "var(--ns-muted)" }}>
                    {form.estado_emocional_ini ?? "—"} / 10
                  </p>
                </div>
                <div className="pt-4">
                  <p className="ns-eyebrow mb-1.5">Estado emocional al CIERRE (0–10)</p>
                  <input type="range" min="0" max="10" value={form.estado_emocional_fin ?? 5}
                    onChange={e => set("estado_emocional_fin", parseInt(e.target.value, 10))}
                    disabled={isLocked}
                    className="w-full" style={{ accentColor: PLUM }} />
                  <p className="text-xs mt-1" style={{ color: "var(--ns-muted)" }}>
                    {form.estado_emocional_fin ?? "—"} / 10
                  </p>
                </div>
              </div>

              {/* Tareas + medicación */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="ns-eyebrow mb-1.5">Tareas asignadas</p>
                  <Txta value={form.tareas_asignadas || ""} onChange={e => set("tareas_asignadas", e.target.value)}
                    disabled={isLocked} rows={2}
                    placeholder="Ej. registro de pensamientos diario, lectura de capítulo…"
                    className="text-sm" />
                </div>
                <div>
                  <p className="ns-eyebrow mb-1.5">Medicación reportada</p>
                  <Txta value={form.medicacion_actual || ""} onChange={e => set("medicacion_actual", e.target.value)}
                    disabled={isLocked} rows={2}
                    placeholder="Cambios, adherencia, efectos secundarios…"
                    className="text-sm" />
                </div>
              </div>

              {/* §tareas: panel embebido cuando la sesión ya está guardada
                * (necesita session_id para vincular las tareas a esta sesión). */}
              {sessionId && !isLocked && (
                <div className="pt-2 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
                  <div className="pt-4">
                    <TareasTerapeuticasPanel
                      patientId={patientId}
                      planId={planId}
                      sessionId={sessionId}
                      embedded
                    />
                  </div>
                </div>
              )}

              {/* Riesgo suicida — sección crítica */}
              <div className="rounded-md p-4" style={{ background: "rgba(159,18,57,0.04)", border: "1px solid rgba(159,18,57,0.20)" }}>
                <div className="flex items-center gap-2 mb-3">
                  <I name="emergency" className="text-base" style={{ color: "#9F1239" }} />
                  <p className="ns-eyebrow" style={{ color: "#9F1239" }}>Evaluación de riesgo suicida</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  {RIESGO_OPCIONES.map(r => (
                    <label key={r.id} className="flex items-center gap-2 cursor-pointer text-sm">
                      <input type="radio" name="riesgo" checked={form.riesgo_suicida === r.id}
                        onChange={() => set("riesgo_suicida", r.id)} disabled={isLocked}
                        style={{ accentColor: r.color }} />
                      <span style={{ color: form.riesgo_suicida === r.id ? r.color : "var(--ns-text)" }}>
                        {r.label}
                      </span>
                    </label>
                  ))}
                </div>
                {form.riesgo_suicida && form.riesgo_suicida !== "ninguno" && (
                  <Txta value={form.riesgo_observaciones || ""} onChange={e => set("riesgo_observaciones", e.target.value)}
                    disabled={isLocked} rows={2}
                    placeholder="Detalla: factores de riesgo, protección, plan de seguridad pactado…"
                    className="text-sm" />
                )}
              </div>
            </>
          )}
        </div>

        {/* Footer acciones */}
        {!loading && (
          <div className="px-6 py-3 border-t flex items-center justify-end gap-2"
            style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
            <Btn v="outline" onClick={onCancel} className="text-xs">Cerrar</Btn>
            {!isLocked && (
              <>
                <Btn onClick={guardar} disabled={saving} className="text-xs" style={{ background: NAVY }}>
                  <I name="save" className="text-sm" />{saving ? "Guardando…" : (sessionId ? "Guardar cambios" : "Crear sesión")}
                </Btn>
                {sessionId && (
                  <Btn onClick={firmar} disabled={locking} className="text-xs" style={{ background: PLUM }}>
                    <I name="lock" className="text-sm" />{locking ? "Firmando…" : "Firmar y cerrar"}
                  </Btn>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════
 * §M-4 — TelepsicologiaTools
 * ───────────────────────────────────────────────────────────────────────
 * Cuando la sesión es de modalidad "telepsicologia", muestra:
 *   • Botón "Generar sala Jitsi" — abre meet.jit.si/<token> en nueva pestaña
 *     El token es determinístico por sessionId para que paciente y
 *     terapeuta puedan acceder a la misma sala usando el mismo link.
 *   • Botón "Copiar link al portapapeles" — para enviar al paciente.
 *   • Aviso de consentimiento informado específico (Ley 1090 art. 36).
 * ═══════════════════════════════════════════════════════════════════════ */
function TelepsicologiaTools({ sessionId, isLocked }) {
  const toast = useToast();
  const [customUrl, setCustomUrl] = React.useState("");
  /* Token determinístico desde sessionId (8 chars). Si sessionId no
   * existe aún (sesión nueva), generamos uno aleatorio para esta vista. */
  const token = React.useMemo(() => {
    if (sessionId) return `neurosoft-${sessionId.slice(0, 8)}`;
    return `neurosoft-${Math.random().toString(36).slice(2, 10)}`;
  }, [sessionId]);
  const jitsiUrl = `https://meet.jit.si/${token}`;
  const url = customUrl.trim() || jitsiUrl;

  const copiar = async () => {
    try {
      await navigator.clipboard.writeText(url);
      // toast no está disponible aquí; usar feedback visual mínimo
      const el = document.getElementById(`tp-copy-${token}`);
      if (el) {
        const txt = el.textContent;
        el.textContent = "¡Copiado!";
        setTimeout(() => { el.textContent = txt; }, 1200);
      }
    } catch {
      toast.info("Copia manualmente el link de telepsicología.");
    }
  };

  return (
    <div className="mt-2 rounded p-2 text-xs"
      style={{ background: "rgba(13,148,136,0.06)", border: "1px solid rgba(13,148,136,0.18)" }}>
      <p className="font-bold mb-1" style={{ color: "#0D9488" }}>
        Videollamada (Jitsi, Meet o Zoom)
      </p>
      <input
        type="url"
        value={customUrl}
        onChange={(e) => setCustomUrl(e.target.value)}
        disabled={isLocked}
        placeholder="Pegar link Meet/Zoom o usar Jitsi por defecto"
        className="w-full text-[10px] font-mono mb-2 px-2 py-1.5 rounded border"
        style={{ background: "var(--ns-input)", borderColor: "var(--ns-card-b)", color: "var(--ns-text)" }}
      />
      <p className="font-mono text-[10px] mb-2 break-all" style={{ color: "var(--ns-muted)" }}>
        {url}
      </p>
      <div className="flex gap-1.5 flex-wrap">
        <a href={url} target="_blank" rel="noopener noreferrer"
          className="text-xs font-bold px-2 py-1 rounded inline-flex items-center gap-1"
          style={{ background: "#0D9488", color: "white" }}>
          Abrir sala
        </a>
        <button onClick={copiar} disabled={isLocked} id={`tp-copy-${token}`}
          className="text-xs font-bold px-2 py-1 rounded border"
          style={{ borderColor: "#0D9488", color: "#0D9488" }}>
          Copiar link
        </button>
      </div>
      <p className="text-[10px] mt-2" style={{ color: "var(--ns-muted)" }}>
        Recuerda obtener <strong>consentimiento informado específico</strong> de telepsicología
        (Ley 1090 art. 36): el paciente debe saber que es una llamada digital, los riesgos
        técnicos asociados, y que no se está grabando salvo autorización explícita.
      </p>
    </div>
  );
}
