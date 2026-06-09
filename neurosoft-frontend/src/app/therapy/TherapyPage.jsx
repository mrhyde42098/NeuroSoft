/* ═══════════════════════════════════════════════════════════════════════
 * src/app/therapy/TherapyPage.jsx — Hub del módulo de Psicología Clínica
 * ───────────────────────────────────────────────────────────────────────
 * Página principal de sesiones terapéuticas. Diferente del módulo de
 * evaluación neuropsicológica. Aquí se gestiona:
 *
 *   • Plan terapéutico activo del paciente seleccionado
 *   • Listado de sesiones SOAP (historial)
 *   • Acceso rápido a "Nueva sesión" + "Nuevo plan"
 *   • Banner persistente si hay riesgo suicida activo
 *   • Catálogo de enfoques disponibles (CBT, EMDR, etc.)
 *
 * Consume los endpoints /api/v1/therapy/* implementados en
 * neurosoft-backend/app/presentation/api/v1/therapy.py
 *
 * Estilo: editorial (Lora serif para títulos, NAVY como protagonista,
 * TEAL como acento minoritario, radii contenidos 6-10px).
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useMemo, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { Btn, Card, I, Sel, TopBar, _Txta } from "../../ui/primitives.jsx";
import { TEAL, NAVY, ACCENTS } from "../../ui/tokens.js";
import { useToast } from "../../contexts.jsx";
import { safeLS } from "../../utils/safeLS.js";
import { usePatientsPanel } from "../../hooks/usePatientsPanel.js";
import { PatientSelect } from "../../ui/forms/PatientSelector.jsx";
import {
  ENFOQUES_TERAPEUTICOS, CATEGORIAS_ENFOQUE, NIVELES_EVIDENCIA, getEnfoque,
} from "../../data/enfoquesTerapeuticos.js";
import SesionSOAPForm from "./SesionSOAPForm.jsx";
import PlanTerapeuticoForm from "./PlanTerapeuticoForm.jsx";
import EnfoqueDetalle from "./EnfoqueDetalle.jsx";
import CSSRSForm from "./CSSRSForm.jsx"; // §M-3

const PLUM = ACCENTS.plum;   // color del módulo clínico

const RIESGO_BADGE = {
  ninguno:    { label: "Sin riesgo activo",   color: "var(--ns-muted)", bg: "var(--ns-subtle)" },
  leve:       { label: "Riesgo leve",         color: "#92400E",         bg: "rgba(180,83,9,0.10)" },
  moderado:   { label: "Riesgo moderado",     color: "#C2410C",         bg: "rgba(194,65,12,0.12)" },
  alto:       { label: "Riesgo alto",         color: "#9F1239",         bg: "rgba(159,18,57,0.12)" },
  inminente:  { label: "Riesgo inminente",    color: "#FFFFFF",         bg: "#7F1D1D" },
  /* Compatibilidad con notas SOAP antiguas */
  ideacion_pasiva:  { label: "Ideación pasiva",  color: "#92400E", bg: "rgba(180,83,9,0.10)" },
  ideacion_activa:  { label: "Ideación activa",  color: "#9F1239", bg: "rgba(159,18,57,0.10)" },
  plan:             { label: "Plan suicida",     color: "#7F1D1D", bg: "rgba(127,29,29,0.12)" },
  intento_reciente: { label: "Intento reciente", color: "#FFFFFF", bg: "#7F1D1D" },
};

export default function TherapyPage({ setPage }) {
  const toast = useToast();
  const { patients, loading: patientsLoading } = usePatientsPanel();
  const [patId, setPatId] = useState(() => safeLS.get("ns_sel_patient") || "");
  const [plans, setPlans] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [riskAssessments, setRiskAssessments] = useState([]);
  const [loading, setLoading] = useState(false);

  /* Modales / paneles */
  const [showNewSession, setShowNewSession] = useState(false);
  const [showNewPlan, setShowNewPlan] = useState(false);
  const [editingSession, setEditingSession] = useState(null);   /* id de sesión a abrir en panel */
  const [showCatalog, setShowCatalog] = useState(false);
  const [catalogFilter, setCatalogFilter] = useState("");
  const [showCSSRS, setShowCSSRS] = useState(false); // §M-3

  /* Cargar planes + sesiones + riesgo del paciente seleccionado */
  useEffect(() => {
    if (!patId) {
      setPlans([]); setSessions([]); setRiskAssessments([]);
      return;
    }
    setLoading(true);
    Promise.all([
      api.get(`/api/v1/therapy/plans?patient_id=${patId}`).catch(() => []),
      api.get(`/api/v1/therapy/sessions?patient_id=${patId}`).catch(() => []),
      api.get(`/api/v1/therapy/risk-assessments?patient_id=${patId}`).catch(() => []),
    ]).then(([p, s, r]) => {
      setPlans(p || []);
      setSessions(s || []);
      setRiskAssessments(r || []);
      setLoading(false);
    });
  }, [patId]);

  const lastCssrs = useMemo(() => riskAssessments.find((r) => r.instrumento === "c_ssrs") || riskAssessments[0] || null, [riskAssessments]);
  const cssrsCompletado = Boolean(lastCssrs?.fecha);
  /* Riesgo activo: último C-SSRS con nivel distinto de "ninguno". */
  const riesgoActivo = useMemo(() => {
    if (!lastCssrs?.nivel || lastCssrs.nivel === "ninguno") return null;
    return lastCssrs;
  }, [lastCssrs]);

  /* Plan activo (estado "activo") */
  const planActivo = plans.find(p => p.estado === "activo") || null;

  const handleSessionCreated = (newSession) => {
    setSessions(prev => [newSession, ...prev]);
    setShowNewSession(false);
    toast.success("Sesión registrada.");
  };

  const handlePlanCreated = (newPlan) => {
    setPlans(prev => [newPlan, ...prev]);
    setShowNewPlan(false);
    toast.success("Plan terapéutico creado.");
  };

  /* Catálogo filtrado */
  const enfoquesFiltrados = catalogFilter
    ? ENFOQUES_TERAPEUTICOS.filter(e => e.categoria === catalogFilter)
    : ENFOQUES_TERAPEUTICOS;

  return (
    <>
      <TopBar title="Psicología Clínica">
        <PatientSelect
          bare
          patients={patients}
          loading={patientsLoading}
          value={patId}
          onChange={(id) => { setPatId(id); safeLS.set("ns_sel_patient", id); }}
          selectClassName="text-xs w-52"
          placeholder="— Seleccionar paciente —"
          allowNew={!!setPage}
          onNewPatient={setPage ? () => setPage("register") : undefined}
        />
        <Btn v="outline" className="text-xs" onClick={() => setShowCatalog(true)}>
          <I name="menu_book" className="text-sm" />Enfoques
        </Btn>
        {patId && (
          <Btn className="text-xs whitespace-nowrap"
            style={{ background: NAVY }}
            onClick={() => setShowNewSession(true)}>
            <I name="add" className="text-sm" />Nueva sesión
          </Btn>
        )}
      </TopBar>

      <main className="p-6 lg:p-8 max-w-7xl mx-auto">
        {/* §editorial: encabezado con eyebrow + título serif + descripción */}
        <div className="mb-8 ns-section-rule">
          <p className="ns-eyebrow" style={{ color: PLUM }}>Módulo terapéutico</p>
          <h2 className="ns-serif text-3xl font-bold mt-1.5 mb-2" style={{ color: "var(--ns-text)" }}>
            Sesiones de psicoterapia
          </h2>
          <p className="text-sm max-w-2xl leading-relaxed" style={{ color: "var(--ns-muted)" }}>
            Gestión de notas SOAP, planes terapéuticos con objetivos SMART,
            seguimiento longitudinal de riesgo y evolución por sesión.
          </p>
        </div>

        {/* ⚠ Banner persistente si hay riesgo activo */}
        {riesgoActivo && (
          <div className="mb-6 rounded-lg border-l-[3px] flex items-start gap-3 p-4"
            style={{
              borderColor: RIESGO_BADGE[riesgoActivo.nivel]?.color || "#9F1239",
              background: RIESGO_BADGE[riesgoActivo.nivel]?.bg || "rgba(159,18,57,0.08)",
            }}>
            <I name="emergency" fill className="text-xl shrink-0" style={{ color: RIESGO_BADGE[riesgoActivo.nivel]?.color }} />
            <div className="flex-1">
              <p className="font-bold text-sm" style={{ color: RIESGO_BADGE[riesgoActivo.nivel]?.color }}>
                Riesgo activo: {RIESGO_BADGE[riesgoActivo.nivel]?.label}
              </p>
              <p className="text-xs mt-0.5" style={{ color: "var(--ns-muted)" }}>
                Última evaluación: {new Date(riesgoActivo.fecha).toLocaleString("es-CO")}
                {riesgoActivo.derivacion_emergencia && " · Derivación a emergencia registrada"}
              </p>
              {riesgoActivo.plan_seguridad && (
                <p className="text-xs mt-2 ns-serif-italic" style={{ color: "var(--ns-text)" }}>
                  Plan de seguridad: {riesgoActivo.plan_seguridad.slice(0, 200)}{riesgoActivo.plan_seguridad.length > 200 ? "…" : ""}
                </p>
              )}
            </div>
            {/* §M-3: re-evaluar */}
            <Btn onClick={() => setShowCSSRS(true)} className="shrink-0 text-xs"
              style={{ background: RIESGO_BADGE[riesgoActivo.nivel]?.color, color: "white", borderColor: RIESGO_BADGE[riesgoActivo.nivel]?.color }}>
              <I name="emergency" className="mr-1" />Re-evaluar
            </Btn>
          </div>
        )}

        {patId && cssrsCompletado && !riesgoActivo && (
          <div className="mb-6 flex items-center justify-between gap-3 p-3 rounded-lg border" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
            <div className="flex items-center gap-2 text-xs" style={{ color: "var(--ns-muted)" }}>
              <I name="verified" style={{ color: "#059669" }} />
              C-SSRS aplicado el {new Date(lastCssrs.fecha).toLocaleString("es-CO")} — nivel: {RIESGO_BADGE.ninguno.label}
            </div>
            <Btn variant="ghost" onClick={() => setShowCSSRS(true)} className="text-xs shrink-0">
              Re-evaluar
            </Btn>
          </div>
        )}
        {patId && !cssrsCompletado && !riesgoActivo && (
          <div className="mb-6 flex justify-end">
            <Btn variant="ghost" onClick={() => setShowCSSRS(true)} className="text-xs">
              <I name="shield" className="mr-1.5" style={{ color: "#9F1239" }} />
              Evaluar riesgo suicida (C-SSRS)
            </Btn>
          </div>
        )}

        {/* Sin paciente seleccionado */}
        {!patId && (
          <Card className="p-12 text-center" style={{ background: "var(--ns-paper, var(--ns-card))" }}>
            <I name="psychology_alt" className="text-5xl opacity-30 mb-3" />
            <h3 className="ns-serif text-xl font-bold mb-2">Selecciona un paciente</h3>
            <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
              Para empezar a registrar sesiones terapéuticas, primero elige un paciente del selector arriba.
            </p>
          </Card>
        )}

        {/* Paciente sin plan activo */}
        {patId && !planActivo && !loading && (
          <Card className="p-8 mb-6" style={{ background: `${PLUM}08`, border: `1px dashed ${PLUM}40` }}>
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-md flex items-center justify-center shrink-0"
                style={{ background: `${PLUM}15` }}>
                <I name="lightbulb" fill className="text-2xl" style={{ color: PLUM }} />
              </div>
              <div className="flex-1">
                <h3 className="ns-serif text-lg font-bold mb-1">Sin plan terapéutico activo</h3>
                <p className="text-sm mb-3" style={{ color: "var(--ns-muted)" }}>
                  Antes de la primera sesión, define un plan con enfoque clínico, diagnóstico
                  y objetivos SMART. Las sesiones quedarán vinculadas automáticamente.
                </p>
                <Btn onClick={() => setShowNewPlan(true)} className="text-xs" style={{ background: PLUM }}>
                  <I name="add" className="text-sm" />Crear plan terapéutico
                </Btn>
              </div>
            </div>
          </Card>
        )}

        {/* Plan activo + estadísticas */}
        {planActivo && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6">
            <Card className="p-5 lg:col-span-2" style={{ borderLeft: `3px solid ${PLUM}` }}>
              <div className="flex items-center justify-between mb-3">
                <p className="ns-eyebrow" style={{ color: PLUM }}>Plan activo</p>
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded"
                  style={{ background: "rgba(21,128,61,0.10)", color: "#166534" }}>
                  {planActivo.estado}
                </span>
              </div>
              <h3 className="ns-serif text-xl font-bold mb-1">
                {getEnfoque(planActivo.enfoque_principal)?.nombre || planActivo.enfoque_principal || "Sin enfoque definido"}
              </h3>
              <p className="text-xs mb-3" style={{ color: "var(--ns-muted)" }}>
                {planActivo.diagnostico_principal && `${planActivo.diagnostico_principal} · `}
                Inicio: {new Date(planActivo.fecha_inicio).toLocaleDateString("es-CO")}
                {planActivo.duracion_estimada_sesiones && ` · ${planActivo.duracion_estimada_sesiones} sesiones estimadas`}
              </p>
              {planActivo.motivo_consulta && (
                <p className="text-sm mt-2 ns-serif-italic leading-relaxed" style={{ color: "var(--ns-text)" }}>
                  «{planActivo.motivo_consulta.slice(0, 220)}{planActivo.motivo_consulta.length > 220 ? "…" : ""}»
                </p>
              )}
              {planActivo.objetivos && planActivo.objetivos.length > 0 && (
                <div className="mt-4 pt-3 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
                  <p className="ns-eyebrow mb-2">Objetivos terapéuticos ({planActivo.objetivos.length})</p>
                  <div className="space-y-2">
                    {planActivo.objetivos.slice(0, 3).map(o => (
                      <div key={o.id} className="flex items-center gap-3 text-xs">
                        <div className="flex-1 truncate">{o.descripcion}</div>
                        <div className="w-24 h-1.5 rounded-full overflow-hidden" style={{ background: "var(--ns-subtle)" }}>
                          <div className="h-full rounded-full" style={{ width: `${o.progreso_pct || 0}%`, background: PLUM }} />
                        </div>
                        <span className="text-[10px] font-bold w-9 text-right" style={{ color: "var(--ns-muted)" }}>{o.progreso_pct || 0}%</span>
                      </div>
                    ))}
                    {planActivo.objetivos.length > 3 && (
                      <p className="text-[10px] mt-1" style={{ color: "var(--ns-muted)" }}>
                        +{planActivo.objetivos.length - 3} objetivos adicionales
                      </p>
                    )}
                  </div>
                </div>
              )}
            </Card>

            <Card className="p-5 flex flex-col">
              <p className="ns-eyebrow mb-3">Indicadores</p>
              <div className="space-y-3 flex-1">
                <Stat label="Sesiones realizadas" value={sessions.length} />
                <Stat label="Sesiones firmadas" value={sessions.filter(s => s.locked_at).length} />
                <Stat label="Riesgo activo" value={riesgoActivo ? "Sí" : "No"}
                      color={riesgoActivo ? "#9F1239" : "#166534"} />
                <Stat label="Última sesión" value={
                  sessions[0] ? new Date(sessions[0].fecha).toLocaleDateString("es-CO") : "—"
                } />
              </div>
            </Card>
          </div>
        )}

        {/* Listado de sesiones */}
        {patId && (
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="ns-serif text-xl font-bold">Historial de sesiones</h3>
              {sessions.length > 0 && (
                <span className="text-xs" style={{ color: "var(--ns-muted)" }}>
                  {sessions.length} sesión{sessions.length !== 1 ? "es" : ""} registrada{sessions.length !== 1 ? "s" : ""}
                </span>
              )}
            </div>
            {loading && (
              <div className="text-center py-12" style={{ color: "var(--ns-muted)" }}>
                <div className="inline-block animate-spin w-6 h-6 border-2 border-current border-t-transparent rounded-full" />
              </div>
            )}
            {!loading && sessions.length === 0 && (
              <Card className="p-10 text-center" style={{ background: "var(--ns-subtle)" }}>
                <I name="event_note" className="text-4xl opacity-30 mb-2" />
                <p className="text-sm font-bold mb-1">Sin sesiones aún</p>
                <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
                  Click en "Nueva sesión" arriba para registrar la primera.
                </p>
              </Card>
            )}
            <div className="space-y-2">
              {sessions.map(s => (
                <SesionRow key={s.id} sesion={s} onOpen={() => setEditingSession(s.id)} />
              ))}
            </div>
          </div>
        )}

        {/* Catálogo de enfoques (modal) */}
        {showCatalog && (
          <CatalogoModal
            onClose={() => setShowCatalog(false)}
            filter={catalogFilter}
            setFilter={setCatalogFilter}
            enfoques={enfoquesFiltrados}
          />
        )}

        {/* Modal "Nueva sesión" */}
        {showNewSession && patId && (
          <SesionSOAPForm
            patientId={patId}
            planId={planActivo?.id}
            onSaved={handleSessionCreated}
            onCancel={() => setShowNewSession(false)}
          />
        )}

        {/* Modal "Editar sesión" */}
        {editingSession && (
          <SesionSOAPForm
            sessionId={editingSession}
            patientId={patId}
            onSaved={(updated) => {
              setSessions(prev => prev.map(s => s.id === updated.id ? updated : s));
              setEditingSession(null);
            }}
            onCancel={() => setEditingSession(null)}
          />
        )}

        {/* Modal "Nuevo plan" */}
        {showNewPlan && patId && (
          <PlanTerapeuticoForm
            patientId={patId}
            onSaved={handlePlanCreated}
            onCancel={() => setShowNewPlan(false)}
          />
        )}

        {/* §M-3 Modal C-SSRS riesgo suicida */}
        {showCSSRS && patId && (
          <CSSRSForm
            patientId={patId}
            onSaved={(saved) => {
              setRiskAssessments(prev => [saved, ...prev]);
              setShowCSSRS(false);
            }}
            onCancel={() => setShowCSSRS(false)}
          />
        )}
      </main>
    </>
  );
}

/* ─────────────────────── helpers visuales ─────────────────────── */

function Stat({ label, value, color }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span style={{ color: "var(--ns-muted)" }}>{label}</span>
      <span className="font-bold ns-mono" style={{ color: color || "var(--ns-text)" }}>
        {value}
      </span>
    </div>
  );
}

function SesionRow({ sesion, onOpen }) {
  const riesgo = RIESGO_BADGE[sesion.riesgo_suicida] || RIESGO_BADGE.ninguno;
  const fecha = new Date(sesion.fecha);
  return (
    <button
      onClick={onOpen}
      className="w-full p-4 rounded-md text-left transition-all border hover:shadow-sm"
      style={{
        background: sesion.locked_at ? "var(--ns-subtle)" : "var(--ns-card)",
        borderColor: "var(--ns-card-b)",
      }}
    >
      <div className="flex items-center gap-4">
        <div className="text-center shrink-0" style={{ minWidth: 56 }}>
          <p className="ns-eyebrow text-[9px]" style={{ color: "var(--ns-muted)" }}>
            {fecha.toLocaleDateString("es-CO", { day: "2-digit", month: "short" }).toUpperCase()}
          </p>
          <p className="ns-mono text-xs mt-0.5" style={{ color: "var(--ns-text)" }}>
            {fecha.toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" })}
          </p>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
              {sesion.modalidad}
            </span>
            {sesion.locked_at && (
              <span className="text-[10px] flex items-center gap-0.5" style={{ color: TEAL }}>
                <I name="lock" className="text-[10px]" />Firmada
              </span>
            )}
          </div>
          <p className="text-sm line-clamp-1" style={{ color: "var(--ns-text)" }}>
            {sesion.soap_subjetivo?.slice(0, 120) || sesion.soap_analisis?.slice(0, 120) || <em style={{ color: "var(--ns-muted)" }}>Sin notas</em>}
            {(sesion.soap_subjetivo || sesion.soap_analisis || "").length > 120 ? "…" : ""}
          </p>
        </div>
        {sesion.riesgo_suicida && sesion.riesgo_suicida !== "ninguno" && (
          <span className="text-[10px] font-bold uppercase px-2 py-1 rounded shrink-0"
            style={{ background: riesgo.bg, color: riesgo.color }}>
            {riesgo.label}
          </span>
        )}
        {sesion.duracion_min && (
          <span className="text-xs ns-mono shrink-0" style={{ color: "var(--ns-muted)" }}>
            {sesion.duracion_min}min
          </span>
        )}
      </div>
    </button>
  );
}

function CatalogoModal({ onClose, filter, setFilter, enfoques }) {
  const [selected, setSelected] = useState(null);
  /* §M-1: Panel académico extendido (videos, técnicas, casos, etc.) */
  const [detalleEnfoque, setDetalleEnfoque] = useState(null);
  const evidenciaCount = enfoques.reduce((acc, e) => ({ ...acc, [e.evidencia]: (acc[e.evidencia] || 0) + 1 }), {});
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(15,23,42,0.55)", backdropFilter: "blur(2px)" }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div onClick={e => e.stopPropagation()}
        className="w-full max-w-6xl max-h-[90vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden"
        style={{ background: "var(--ns-card)" }}>
        {/* Header */}
        <div className="p-6 border-b flex items-start justify-between gap-4" style={{ borderColor: "var(--ns-card-b)", background: `linear-gradient(135deg, ${PLUM}10, transparent)` }}>
          <div className="min-w-0">
            <p className="ns-eyebrow" style={{ color: PLUM }}>Biblioteca</p>
            <h3 className="ns-serif text-2xl font-bold">Enfoques terapéuticos</h3>
            <p className="text-sm mt-1 max-w-2xl leading-relaxed" style={{ color: "var(--ns-muted)" }}>
              Seleccione el enfoque no por moda, sino por problema clínico, fase del caso, evidencia disponible y recursos del paciente.
              Cada tarjeta resume indicación, estructura y medición sugerida.
            </p>
          </div>
          <button onClick={onClose} aria-label="Cerrar catálogo"
            className="p-2 rounded-md hover:bg-gray-100" style={{ color: "var(--ns-muted)" }}>
            <I name="close" />
          </button>
        </div>

        <div className="px-6 py-3 border-b grid grid-cols-2 sm:grid-cols-4 gap-3" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
          {[
            ["Total", enfoques.length, "menu_book", PLUM],
            ["Evidencia A", evidenciaCount.A || 0, "verified", "#166534"],
            ["Evidencia B", evidenciaCount.B || 0, "science", "#92400E"],
            ["Tradicional/C", (evidenciaCount.tradicional || 0) + (evidenciaCount.C || 0), "history_edu", "var(--ns-muted)"],
          ].map(([label, value, icon, color]) => (
            <div key={label} className="rounded-xl p-3 border" style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
              <div className="flex items-center gap-2">
                <I name={icon} className="text-base" style={{ color }} />
                <span className="text-[10px] font-bold uppercase tracking-wide" style={{ color: "var(--ns-muted)" }}>{label}</span>
              </div>
              <p className="text-2xl font-extrabold mt-1 tabular-nums" style={{ color }}>{value}</p>
            </div>
          ))}
        </div>

        {/* Filtros */}
        <div className="px-6 py-3 border-b flex gap-2 flex-wrap" style={{ borderColor: "var(--ns-card-b)" }}>
          <button onClick={() => setFilter("")}
            className={`text-xs px-3 py-1 rounded ${!filter ? "" : "hover:bg-gray-100"}`}
            style={!filter ? { background: PLUM, color: "white" } : { color: "var(--ns-muted)" }}>
            Todos
          </button>
          {CATEGORIAS_ENFOQUE.map(cat => (
            <button key={cat} onClick={() => setFilter(cat)}
              className={`text-xs px-3 py-1 rounded capitalize ${filter === cat ? "" : "hover:bg-gray-100"}`}
              style={filter === cat ? { background: PLUM, color: "white" } : { color: "var(--ns-muted)" }}>
              {cat.replace(/_/g, " ")}
            </button>
          ))}
        </div>

        {/* Listado */}
        <div className="flex-1 overflow-auto p-5 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {enfoques.map(e => (
            <button key={e.id}
              onClick={() => setSelected(e)}
              onDoubleClick={() => setDetalleEnfoque(e)}
              title="Click para vista previa · Doble click para panel académico completo"
              className="p-4 rounded-2xl text-left transition-all border hover:shadow-md relative min-h-[210px] flex flex-col"
              style={{
                background: selected?.id === e.id ? `${PLUM}10` : "var(--ns-card)",
                borderColor: selected?.id === e.id ? PLUM : "var(--ns-card-b)",
              }}>
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-[15px] leading-tight">{e.nombre}</p>
                  {e.sigla && (
                    <p className="text-[10px] ns-mono mt-0.5" style={{ color: PLUM }}>{e.sigla}</p>
                  )}
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded shrink-0 ml-2"
                  style={{
                    background: e.evidencia === "A" ? "rgba(21,128,61,0.12)" : e.evidencia === "B" ? "rgba(180,83,9,0.10)" : "var(--ns-subtle)",
                    color: e.evidencia === "A" ? "#166534" : e.evidencia === "B" ? "#92400E" : "var(--ns-muted)",
                  }}
                  title={NIVELES_EVIDENCIA[e.evidencia]}>
                  Evidencia {e.evidencia}
                </span>
              </div>
              <p className="text-[10px] uppercase tracking-wider mb-2" style={{ color: "var(--ns-muted)" }}>
                {e.categoria.replace(/_/g, " ")} · {e.duracion_tipica}
              </p>
              <p className="text-xs leading-snug flex-1" style={{ color: "var(--ns-muted)" }}>
                {e.indicaciones.slice(0, 2).join(" · ")}
                {e.indicaciones.length > 2 && ` · +${e.indicaciones.length - 2}`}
              </p>
              <div className="mt-3 pt-3 border-t grid grid-cols-2 gap-2 text-[10px]" style={{ borderColor: "var(--ns-card-b)" }}>
                <span className="font-bold" style={{ color: PLUM }}>
                  {e.estructura?.length || 0} fases
                </span>
                <span className="font-bold text-right" style={{ color: "var(--ns-muted)" }}>
                  {(e.outcome_recomendadas || []).slice(0, 2).join(" · ") || "Outcome clínico"}
                </span>
              </div>
            </button>
          ))}
        </div>

        {/* Footer / detalle del seleccionado */}
        {selected && (
          <div className="border-t p-5 max-h-[38vh] overflow-auto" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
            <div className="flex items-start justify-between mb-2 gap-3">
              <div className="flex-1 min-w-0">
                <p className="ns-eyebrow mb-1">Resumen clínico</p>
                <h4 className="ns-serif text-lg font-bold">{selected.nombre}</h4>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => setSelected(null)}
                  className="text-xs font-bold px-3 py-2 rounded flex items-center gap-1.5 transition-all"
                  style={{ background: "var(--ns-card)", border: "1px solid var(--ns-card-b)", color: "var(--ns-muted)" }}
                  title="Cerrar y volver al catálogo de enfoques">
                  <I name="close" className="text-base" />
                  Cerrar
                </button>
                <button
                  onClick={() => setDetalleEnfoque(selected)}
                  className="text-xs font-bold px-3 py-2 rounded flex items-center gap-1.5 hover:shadow-sm transition-all"
                  style={{ background: PLUM, color: "white" }}
                  title="Abrir panel académico con videos, técnicas, casos y bibliografía">
                  <I name="school" className="text-base" />
                  Ver más
                </button>
              </div>
            </div>
            {selected.notas && (
              <p className="text-sm mb-3 ns-serif-italic" style={{ color: "var(--ns-text)" }}>{selected.notas}</p>
            )}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="rounded-xl p-3 border" style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
                <p className="ns-eyebrow mb-2">Estructura típica</p>
                <ul className="space-y-1.5 leading-relaxed" style={{ color: "var(--ns-muted)" }}>
                  {selected.estructura.slice(0, 6).map((s, i) => <li key={i} className="flex gap-2"><span className="font-bold" style={{ color: PLUM }}>{i + 1}.</span><span>{s}</span></li>)}
                </ul>
              </div>
              <div className="rounded-xl p-3 border" style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
                <p className="ns-eyebrow mb-2">Técnicas clave</p>
                <ul className="space-y-1.5 leading-relaxed" style={{ color: "var(--ns-muted)" }}>
                  {selected.tecnicas_clave.slice(0, 5).map((t, i) => <li key={i} className="flex gap-2"><I name="check_circle" className="text-xs mt-0.5" style={{ color: PLUM }} /><span>{t}</span></li>)}
                </ul>
                {selected.outcome_recomendadas?.length > 0 && (
                  <>
                    <p className="ns-eyebrow mt-3 mb-1">Outcome recomendadas</p>
                    <p className="ns-mono text-[11px]" style={{ color: "var(--ns-text)" }}>
                      {selected.outcome_recomendadas.join(" · ")}
                    </p>
                  </>
                )}
              </div>
            </div>
            {selected.referencias?.length > 0 && (
              <div className="mt-3 pt-3 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
                <p className="ns-eyebrow mb-1">Referencias</p>
                <p className="text-[10px] ns-serif-italic leading-relaxed" style={{ color: "var(--ns-muted)" }}>
                  {selected.referencias[0]}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* §M-1: Panel académico extendido */}
      {detalleEnfoque && (
        <EnfoqueDetalle enfoque={detalleEnfoque} onClose={() => setDetalleEnfoque(null)} />
      )}
    </div>
  );
}
