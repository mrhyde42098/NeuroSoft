/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/RehabPage.jsx — Página principal de Rehabilitación
 * ───────────────────────────────────────────────────────────────────────
 * Tres sub-pestañas:
 *   • Plan          → seleccionar paciente, crear/editar plan, firmar, compartir
 *   • Actividades   → catálogo de actividades, ejecutar (Stroop por ahora)
 *   • Sesiones      → timeline + gráfica de evolución por dominio
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useMemo, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { useConfirm, useToast } from "../../contexts.jsx";
import { safeLS } from "../../utils/safeLS.js";
import {
  Btn, Card, EmptyState, I, Input, Label, MsgBanner,
  Sel, Skeleton, Spinner, TopBar, Txta,
} from "../../ui/primitives.jsx";
import { TEAL, COLORS } from "../../ui/tokens.js";
import StroopActivity from "./StroopActivity.jsx";
import NBackActivity from "./NBackActivity.jsx";
import FluencyActivity from "./FluencyActivity.jsx";
import TachadoActivity from "./TachadoActivity.jsx";
import CorsiBlocks from "../evaluation/CorsiBlocks.jsx";
import SpacedRetrievalActivity from "./SpacedRetrievalActivity.jsx";
import MentalRotationActivity from "./MentalRotationActivity.jsx";
import EkmanRecognitionActivity from "./EkmanRecognitionActivity.jsx";
import CPTActivity from "./CPTActivity.jsx";
import GoNoGoActivity from "./GoNoGoActivity.jsx";
import SetShiftingActivity from "./SetShiftingActivity.jsx";
import DenominacionClavesActivity from "./DenominacionClavesActivity.jsx";
import TowerOfLondonActivity from "./TowerOfLondonActivity.jsx";
import MindInEyesActivity from "./MindInEyesActivity.jsx";
import AvdDineroActivity from "./AvdDineroActivity.jsx";

const TABS = [
  { id: "plan",       label: "Plan",       icon: "assignment_ind" },
  { id: "actividades",label: "Actividades", icon: "extension"      },
  { id: "sesiones",   label: "Sesiones",    icon: "monitoring"     },
];

const DOMINIO_LABELS = {
  atencion:                "Atención",
  memoria:                 "Memoria",
  memoria_trabajo:         "Memoria de trabajo",
  funciones_ejecutivas:    "Funciones ejecutivas",
  lenguaje:                "Lenguaje",
  visoespacial:            "Visoespacial",
  velocidad_procesamiento: "Velocidad de procesamiento",
};

const DOMINIO_COLORS = {
  atencion:             "#6366f1",
  memoria:              "#0d9488",
  memoria_trabajo:      "#0891b2",
  funciones_ejecutivas: "#ec4899",
  lenguaje:             "#d97706",
  visoespacial:         "#7c3aed",
  velocidad_procesamiento: "#dc2626",
};

/* Mapeo slug → componente de actividad. Centraliza las 4 actividades MVP. */
const ACTIVITY_COMPONENTS = {
  stroop:             StroopActivity,
  n_back:             NBackActivity,
  fluency_verbal:     FluencyActivity,
  tachado:            TachadoActivity,
  corsi_forward:      CorsiBlocks,
  corsi_backward:     CorsiBlocks,
  spaced_retrieval:   SpacedRetrievalActivity,
  mental_rotation:    MentalRotationActivity,
  ekman_recognition:  EkmanRecognitionActivity,
  cpt:                CPTActivity,
  go_no_go:           GoNoGoActivity,
  set_shifting:       SetShiftingActivity,
  denominacion_claves: DenominacionClavesActivity,
  tower_of_london:    TowerOfLondonActivity,
  mente_ojos:         MindInEyesActivity,
  avd_dinero:         AvdDineroActivity,
};

/* ═══════════════════════════════════════════════════════════════
 * RehabPage (root)
 * ═══════════════════════════════════════════════════════════════ */
export default function RehabPage() {
  const toast = useToast();
  const [tab, setTab] = useState("plan");
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState(
    safeLS.get("ns_sel_patient") || ""
  );
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api.get("/api/v1/patients/panel")
      .then((d) => setPatients(d.pacientes || d || []))
      .catch(() => toast.error("Error cargando pacientes"));
    return () => safeLS.remove("ns_sel_patient");
  }, []);

  return (
    <>
      <TopBar title="Rehabilitación · Estimulación cognitiva">
        <span className="text-xs" style={{ color: "var(--ns-muted)" }}>
          Plan, actividades y seguimiento
        </span>
      </TopBar>
      <main className="p-8 space-y-6">
        <MsgBanner
          msg={msg}
          onDismiss={msg && msg !== "ok" ? () => setMsg("") : null}
        />

        {/* Selector de paciente */}
        <Card className="p-6">
          <div className="flex items-center gap-6">
            <div className="flex-1">
              <Label>Paciente</Label>
              <Sel
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
              >
                <option value="">— Seleccione —</option>
                {patients.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.nombre_completo ||
                      `${p.primer_nombre} ${p.primer_apellido}`}{" "}
                    — {p.numero_documento}
                  </option>
                ))}
              </Sel>
            </div>
          </div>
        </Card>

        {/* Tabs */}
        <div className="flex gap-2 flex-wrap">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className="px-6 py-3 rounded-full text-sm font-bold transition-all flex items-center gap-2"
              style={
                tab === t.id
                  ? { background: TEAL, color: "#fff", boxShadow: "0 8px 20px -4px rgba(13,148,136,0.3)" }
                  : { background: "var(--ns-subtle)", color: "var(--ns-muted)" }
              }
            >
              <I name={t.icon} className="text-base" />
              {t.label}
            </button>
          ))}
        </div>

        {!patientId ? (
          <EmptyState
            icon="person_search"
            title="Selecciona un paciente"
            description="Elige un paciente del listado para gestionar su plan de rehabilitación."
          />
        ) : tab === "plan" ? (
          <PlanTab patientId={patientId} setMsg={setMsg} />
        ) : tab === "actividades" ? (
          <ActivitiesTab patientId={patientId} setMsg={setMsg} />
        ) : (
          <SessionsTab patientId={patientId} />
        )}
      </main>
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════
 * PlanTab
 * ═══════════════════════════════════════════════════════════════ */
function PlanTab({ patientId, setMsg }) {
  const confirm = useConfirm();
  const toast = useToast();
  const [plans, setPlans] = useState([]);
  const [activities, setActivities] = useState([]);
  const [ld, setLd] = useState(true);
  const [editing, setEditing] = useState(null); // plan en edición
  const [shareLink, setShareLink] = useState(null);
  const [saving, setSaving] = useState(false);

  const reload = () => {
    setLd(true);
    Promise.all([
      api.get(`/api/v1/rehab/plans/by-patient/${patientId}`).catch(() => []),
      api.get("/api/v1/rehab/activities").catch(() => []),
    ]).then(([ps, acts]) => {
      setPlans(ps || []);
      setActivities(acts || []);
      setLd(false);
    });
  };

  useEffect(() => {
    reload();
  }, [patientId]);

  const newPlan = (prefill = null) => {
    const today = new Date().toISOString().split("T")[0];
    setEditing({
      patient_id: patientId,
      fecha_inicio: today,
      frecuencia_semanal: prefill?.frecuencia_semanal_sugerida || 2,
      objetivos: prefill?.objetivos_sugerencia || "",
      dominios: prefill?.dominios_sugeridos || [],
      actividades: prefill?.actividades || [],
      notas: prefill ? `Plan generado desde evaluación ${prefill.from_eval}.` : "",
      evaluation_id: prefill?.from_eval || null,
    });
  };

  /* Si hay sugerencia pendiente del flujo "Iniciar Rehab desde resultados",
   * abrir el editor pre-rellenado automáticamente. */
  useEffect(() => {
    const sug = safeLS.getJSON("ns_rehab_suggestion");
    if (!sug || !patientId) return;
    if (sug.patient_id && sug.patient_id !== patientId) return;
    newPlan(sug);
    safeLS.remove("ns_rehab_suggestion");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patientId]);

  const savePlan = async () => {
    setSaving(true);
    setMsg("");
    try {
      let result;
      if (editing.id) {
        // En PATCH no incluimos campos no editables
        const patch = { ...editing };
        delete patch.patient_id;
        delete patch.id;
        delete patch.evaluation_id;
        result = await api.patch(`/api/v1/rehab/plans/${editing.id}`, patch);
      } else {
        result = await api.post("/api/v1/rehab/plans", editing);
      }
      setMsg("ok");
      setEditing(null);
      reload();
    } catch (e) {
      setMsg(_parseError(e));
    }
    setSaving(false);
  };

  const signPlan = async (planId) => {
    if (!(await confirm({
      title: "Firmar plan de rehabilitación",
      message: "Una vez firmado, solo podrás cambiar el estado del plan (pausado, terminado).\nNo podrás modificar objetivos ni actividades.",
      confirmText: "Firmar",
      dangerous: true,
    }))) return;
    setSaving(true);
    try {
      await api.post(`/api/v1/rehab/plans/${planId}/sign`, { confirm: true });
      setMsg("Plan firmado");
      reload();
    } catch (e) {
      setMsg(_parseError(e));
    }
    setSaving(false);
  };

  const sharePlan = async (planId) => {
    setSaving(true);
    try {
      const link = await api.post(`/api/v1/rehab/plans/${planId}/share`, {
        plan_id: planId,
        expires_in_days: 30,
      });
      const url = `${window.location.origin}${link.public_url}`;
      setShareLink({ ...link, full_url: url });
    } catch (e) {
      setMsg(_parseError(e));
    }
    setSaving(false);
  };

  /* Descarga el PDF del plan firmado. Solo disponible cuando
   * `signed_at != null`; el backend devuelve 409 en caso contrario. */
  const downloadPlanPdf = async (planId) => {
    setSaving(true);
    try {
      const blob = await api.blob(`/api/v1/rehab/plans/${planId}/pdf`, "POST");
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `PlanRehab_${planId.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      setMsg(_parseError(e));
    }
    setSaving(false);
  };

  if (ld) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
      </div>
    );
  }

  /* ── Modal de share link ── */
  if (shareLink) {
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center">
        <div
          className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4"
          style={{ background: `${TEAL}15`, color: TEAL }}
        >
          <I name="share" className="text-3xl" />
        </div>
        <h3 className="text-xl font-extrabold mb-3">Link generado</h3>
        <p className="text-sm mb-6" style={{ color: "var(--ns-muted)" }}>
          Comparte este enlace con el paciente. Es válido hasta el{" "}
          <strong>{new Date(shareLink.expires_at).toLocaleDateString("es")}</strong>.
        </p>
        <div
          className="rounded-xl p-4 mb-4 break-all text-sm font-mono"
          style={{ background: "var(--ns-subtle)" }}
        >
          {shareLink.full_url}
        </div>
        <div className="flex justify-center gap-3">
          <Btn
            v="outline"
            onClick={() => {
              navigator.clipboard?.writeText(shareLink.full_url);
              setMsg("ok");
            }}
          >
            <I name="content_copy" />
            Copiar
          </Btn>
          <Btn onClick={() => setShareLink(null)}>Cerrar</Btn>
        </div>
      </Card>
    );
  }

  /* ── Editor del plan ── */
  if (editing) {
    return (
      <PlanEditor
        plan={editing}
        activities={activities}
        onChange={setEditing}
        onSave={savePlan}
        onCancel={() => setEditing(null)}
        saving={saving}
      />
    );
  }

  /* ── Listado de planes ── */
  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Btn onClick={newPlan}>
          <I name="add" />
          Nuevo plan
        </Btn>
      </div>
      {plans.length === 0 ? (
        <EmptyState
          icon="assignment_ind"
          title="Sin planes de rehabilitación"
          description="Crea el primer plan para este paciente y define dominios, actividades y frecuencia."
          cta={
            <Btn onClick={newPlan}>
              <I name="add" />
              Crear plan
            </Btn>
          }
        />
      ) : (
        plans.map((p) => (
          <Card
            key={p.id}
            className="p-6"
            style={{ borderLeft: `4px solid ${stateColor(p.estado)}` }}
          >
            <div className="flex items-start justify-between gap-4 mb-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className="text-[10px] font-extrabold uppercase tracking-wider px-2 py-1 rounded"
                    style={{
                      background: `${stateColor(p.estado)}15`,
                      color: stateColor(p.estado),
                    }}
                  >
                    {p.estado}
                  </span>
                  {p.signed_at && (
                    <span className="text-[10px] font-bold flex items-center gap-1" style={{ color: TEAL }}>
                      <I name="verified" fill className="text-sm" />
                      Firmado
                    </span>
                  )}
                </div>
                <p className="text-sm font-bold">
                  Inicio: {p.fecha_inicio} · {p.frecuencia_semanal} sesiones/semana
                </p>
                {p.objetivos && (
                  <p className="text-xs mt-1" style={{ color: "var(--ns-muted)" }}>
                    {p.objetivos}
                  </p>
                )}
                <div className="flex flex-wrap gap-1 mt-2">
                  {(p.dominios || []).map((d) => (
                    <span
                      key={d}
                      className="text-[10px] font-bold px-2 py-0.5 rounded"
                      style={{
                        background: `${DOMINIO_COLORS[d] || TEAL}15`,
                        color: DOMINIO_COLORS[d] || TEAL,
                      }}
                    >
                      {DOMINIO_LABELS[d] || d}
                    </span>
                  ))}
                </div>
                <p className="text-[10px] mt-2" style={{ color: "var(--ns-muted)" }}>
                  {(p.actividades || []).length} actividad(es) asignada(s)
                </p>
              </div>
              <div className="flex flex-col gap-2 shrink-0">
                {!p.signed_at && (
                  <>
                    <Btn
                      v="outline"
                      className="text-xs"
                      onClick={() => setEditing(p)}
                    >
                      <I name="edit" className="text-sm" />
                      Editar
                    </Btn>
                    <Btn
                      className="text-xs"
                      onClick={() => signPlan(p.id)}
                    >
                      <I name="draw" className="text-sm" />
                      Firmar
                    </Btn>
                  </>
                )}
                {p.signed_at && (
                  <>
                    <Btn
                      v="outline"
                      className="text-xs"
                      onClick={() => sharePlan(p.id)}
                    >
                      <I name="share" className="text-sm" />
                      Compartir
                    </Btn>
                    <Btn
                      v="outline"
                      className="text-xs"
                      onClick={() => downloadPlanPdf(p.id)}
                      disabled={saving}
                    >
                      <I name="picture_as_pdf" className="text-sm" />
                      Descargar PDF
                    </Btn>
                  </>
                )}
              </div>
            </div>
          </Card>
        ))
      )}
    </div>
  );
}

function stateColor(s) {
  return (
    {
      borrador:   "#9ca3af",
      activo:     "#0d9488",
      pausado:    "#d97706",
      finalizado: "#3b82f6",
      archivado:  "#6b7280",
    }[s] || "#6b7280"
  );
}

/* ═══════════════════════════════════════════════════════════════
 * PlanEditor
 * ═══════════════════════════════════════════════════════════════ */
function PlanEditor({ plan, activities, onChange, onSave, onCancel, saving }) {
  const set = (k, v) => onChange({ ...plan, [k]: v });
  const toggleDominio = (d) => {
    const cur = plan.dominios || [];
    set("dominios", cur.includes(d) ? cur.filter((x) => x !== d) : [...cur, d]);
  };
  const toggleActivity = (a) => {
    const cur = plan.actividades || [];
    const exists = cur.find((x) => x.slug === a.slug);
    if (exists) {
      set("actividades", cur.filter((x) => x.slug !== a.slug));
    } else {
      set("actividades", [...cur, {
        slug: a.slug,
        nombre: a.nombre,
        dominio: a.dominio,
        dificultad: a.dificultad_default,
        parametros: a.parametros_default || {},
      }]);
    }
  };

  const dominios = Object.keys(DOMINIO_LABELS);

  return (
    <Card className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-extrabold flex items-center gap-2">
          <I name="assignment_ind" style={{ color: TEAL }} />
          {plan.id ? "Editar plan" : "Nuevo plan de rehabilitación"}
        </h3>
        <Btn v="outline" onClick={onCancel}>
          <I name="close" className="text-sm" />
          Cancelar
        </Btn>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <Label>Fecha de inicio</Label>
          <Input
            type="date"
            value={plan.fecha_inicio}
            onChange={(e) => set("fecha_inicio", e.target.value)}
          />
        </div>
        <div>
          <Label>Fin estimado</Label>
          <Input
            type="date"
            value={plan.fecha_fin_estimada || ""}
            onChange={(e) => set("fecha_fin_estimada", e.target.value || null)}
          />
        </div>
        <div>
          <Label>Sesiones/semana</Label>
          <Input
            type="number"
            min={1}
            max={14}
            value={plan.frecuencia_semanal || 2}
            onChange={(e) => set("frecuencia_semanal", parseInt(e.target.value, 10) || 2)}
          />
        </div>
      </div>

      <div>
        <Label>Objetivos terapéuticos</Label>
        <Txta
          value={plan.objetivos || ""}
          onChange={(e) => set("objetivos", e.target.value)}
          placeholder="Mejorar atención sostenida; reducir tiempo de reacción; entrenar memoria de trabajo verbal."
        />
      </div>

      <div>
        <Label>Dominios cognitivos a intervenir</Label>
        <div className="grid grid-cols-3 gap-2">
          {dominios.map((d) => {
            const active = (plan.dominios || []).includes(d);
            return (
              <button
                key={d}
                onClick={() => toggleDominio(d)}
                className="px-4 py-3 rounded-xl text-sm font-bold transition-all border-2 text-left"
                style={
                  active
                    ? {
                        background: `${DOMINIO_COLORS[d]}15`,
                        borderColor: DOMINIO_COLORS[d],
                        color: DOMINIO_COLORS[d],
                      }
                    : {
                        background: "var(--ns-card)",
                        borderColor: "var(--ns-card-b)",
                        color: "var(--ns-muted)",
                      }
                }
              >
                {DOMINIO_LABELS[d]}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <Label>Actividades asignadas</Label>
        <div className="grid grid-cols-2 gap-3">
          {activities.map((a) => {
            const selected = (plan.actividades || []).some((x) => x.slug === a.slug);
            return (
              <button
                key={a.id}
                onClick={() => toggleActivity(a)}
                className="p-4 rounded-2xl text-left border-2 transition-all"
                style={
                  selected
                    ? { borderColor: TEAL, background: `${TEAL}08` }
                    : { borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }
                }
              >
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-bold text-sm">{a.nombre}</h4>
                  {selected && <I name="check_circle" fill style={{ color: TEAL }} />}
                </div>
                <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
                  {DOMINIO_LABELS[a.dominio] || a.dominio} · {a.duracion_min} min
                </p>
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <Label>Notas (opcional)</Label>
        <Txta
          value={plan.notas || ""}
          onChange={(e) => set("notas", e.target.value)}
        />
      </div>

      <div className="flex justify-end gap-3">
        <Btn v="outline" onClick={onCancel}>
          Cancelar
        </Btn>
        <Btn onClick={onSave} disabled={saving}>
          {saving ? "Guardando..." : "Guardar plan"}
        </Btn>
      </div>
    </Card>
  );
}

/* ═══════════════════════════════════════════════════════════════
 * ActivitiesTab
 * ═══════════════════════════════════════════════════════════════ */
function ActivitiesTab({ patientId, setMsg }) {
  const toast = useToast();
  const [activities, setActivities] = useState([]);
  const [ld, setLd] = useState(true);
  const [running, setRunning] = useState(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    api.get("/api/v1/rehab/activities")
      .then((d) => setActivities(d || []))
      .catch(() => toast.error("Error cargando actividades"))
      .finally(() => setLd(false));
  }, []);

  const filtered = useMemo(() => {
    if (!filter) return activities;
    return activities.filter((a) => a.dominio === filter);
  }, [activities, filter]);

  const handleFinish = async (result) => {
    try {
      await api.post("/api/v1/rehab/sessions", {
        activity_slug: running.slug,
        patient_id: patientId,
        resultado: result,
        duracion_seg: result.duracion_seg || null,
        modo: "en_consulta",
      });
      setMsg("Sesión registrada");
    } catch (e) {
      setMsg(_parseError(e));
    }
    setRunning(null);
  };

  if (running) {
    const ActivityComponent = ACTIVITY_COMPONENTS[running.slug];
    if (ActivityComponent) {
      return (
        <ActivityComponent
          params={running.parametros_default || {}}
          onFinish={handleFinish}
          onCancel={() => setRunning(null)}
        />
      );
    }
    /* Placeholder para actividades aún no implementadas */
    return (
      <Card className="p-8 text-center">
        <p className="font-bold text-lg mb-3">{running.nombre}</p>
        <p className="text-sm mb-4" style={{ color: "var(--ns-muted)" }}>
          Esta actividad aún no está implementada en el cliente.
        </p>
        <Btn v="outline" onClick={() => setRunning(null)}>
          Volver
        </Btn>
      </Card>
    );
  }

  if (ld) return <Skeleton className="h-64" />;

  const dominios = [...new Set(activities.map((a) => a.dominio))];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setFilter("")}
          className="px-4 py-2 rounded-full text-xs font-bold transition-all"
          style={{
            background: !filter ? TEAL : "var(--ns-subtle)",
            color: !filter ? "#fff" : "var(--ns-muted)",
          }}
        >
          Todos
        </button>
        {dominios.map((d) => (
          <button
            key={d}
            onClick={() => setFilter(d)}
            className="px-4 py-2 rounded-full text-xs font-bold transition-all"
            style={{
              background: filter === d ? DOMINIO_COLORS[d] || TEAL : "var(--ns-subtle)",
              color: filter === d ? "#fff" : "var(--ns-muted)",
            }}
          >
            {DOMINIO_LABELS[d] || d}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon="extension"
          title="Sin actividades en este filtro"
          description="Cambia el filtro o agrega una actividad nueva al catálogo."
        />
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((a) => {
            const isReady = !!ACTIVITY_COMPONENTS[a.slug];
            return (
              <Card key={a.id} className="p-5">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center mb-3"
                  style={{
                    background: `${DOMINIO_COLORS[a.dominio] || TEAL}15`,
                    color: DOMINIO_COLORS[a.dominio] || TEAL,
                  }}
                >
                  <I name={iconForActivity(a.slug)} className="text-2xl" />
                </div>
                <h4 className="font-extrabold text-sm mb-1">{a.nombre}</h4>
                <p className="text-[11px] mb-2" style={{ color: "var(--ns-muted)" }}>
                  {DOMINIO_LABELS[a.dominio] || a.dominio} · {a.duracion_min} min
                </p>
                <p
                  className="text-xs leading-snug mb-4 line-clamp-3"
                  style={{ color: "var(--ns-muted)" }}
                >
                  {a.descripcion}
                </p>
                <Btn
                  className="w-full text-xs"
                  v={isReady ? "primary" : "outline"}
                  onClick={() => setRunning(a)}
                  disabled={!isReady}
                >
                  <I name={isReady ? "play_arrow" : "schedule"} className="text-sm" />
                  {isReady ? "Iniciar" : "Próximamente"}
                </Btn>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}

function iconForActivity(slug) {
  return (
    {
      stroop:         "psychology",
      n_back:         "grid_view",
      fluency_verbal: "edit_note",
      tachado:        "highlight_alt",
    }[slug] || "extension"
  );
}

/* ═══════════════════════════════════════════════════════════════
 * SessionsTab — historial + gráfica longitudinal por dominio
 * ═══════════════════════════════════════════════════════════════ */
function SessionsTab({ patientId }) {
  const [sessions, setSessions] = useState([]);
  const [evolution, setEvolution] = useState(null);
  const [ld, setLd] = useState(true);

  useEffect(() => {
    setLd(true);
    Promise.all([
      api.get(`/api/v1/rehab/sessions/by-patient/${patientId}`).catch(() => []),
      api.get(`/api/v1/rehab/evolution/${patientId}`).catch(() => null),
    ]).then(([sess, evo]) => {
      setSessions(sess || []);
      setEvolution(evo);
      setLd(false);
    });
  }, [patientId]);

  if (ld) return <Skeleton className="h-64" />;
  if (sessions.length === 0) {
    return (
      <EmptyState
        icon="monitoring"
        title="Sin sesiones registradas"
        description="Las actividades realizadas en consulta o tarea-casa aparecerán aquí."
      />
    );
  }

  /* Agrupar por slug para mostrar evolución */
  const bySlug = {};
  sessions.forEach((s) => {
    bySlug[s.activity_slug] = bySlug[s.activity_slug] || [];
    bySlug[s.activity_slug].push(s);
  });

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-3xl font-extrabold" style={{ color: TEAL }}>
              {sessions.length}
            </p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Sesiones totales
            </p>
          </div>
          <div>
            <p className="text-3xl font-extrabold">
              {Math.round(
                sessions.reduce((a, s) => a + (s.score || 0), 0) /
                  Math.max(sessions.length, 1)
              )}
            </p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Score promedio
            </p>
          </div>
          <div>
            <p className="text-3xl font-extrabold">
              {sessions.filter((s) => s.modo === "tarea_casa").length}
            </p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Tarea-casa
            </p>
          </div>
        </div>
      </Card>

      {/* ─── Gráfica longitudinal por dominio ─── */}
      {evolution && evolution.dominios && evolution.dominios.length > 0 && (
        <EvolutionChart evolution={evolution} />
      )}

      {/* ── continuación: tabla de sesiones ── */}
      <Card className="overflow-hidden">
        <table className="w-full text-sm">
          <thead style={{ background: "var(--ns-subtle)" }}>
            <tr>
              <th className="px-4 py-3 text-left font-bold text-xs uppercase">Fecha</th>
              <th className="px-4 py-3 text-left font-bold text-xs uppercase">Actividad</th>
              <th className="px-4 py-3 text-center font-bold text-xs uppercase">Score</th>
              <th className="px-4 py-3 text-center font-bold text-xs uppercase">Aciertos</th>
              <th className="px-4 py-3 text-center font-bold text-xs uppercase">Errores</th>
              <th className="px-4 py-3 text-center font-bold text-xs uppercase">Modo</th>
            </tr>
          </thead>
          <tbody>
            {sessions.slice(0, 50).map((s) => (
              <tr key={s.id} className="border-b" style={{ borderColor: "var(--ns-card-b)" }}>
                <td className="px-4 py-3 text-xs">
                  {new Date(s.ts_inicio).toLocaleString("es", { dateStyle: "short", timeStyle: "short" })}
                </td>
                <td className="px-4 py-3 font-bold">{s.activity_slug}</td>
                <td className="px-4 py-3 text-center font-extrabold" style={{ color: TEAL }}>
                  {s.score ?? "—"}
                </td>
                <td className="px-4 py-3 text-center text-emerald-600 font-bold">
                  {s.aciertos ?? "—"}
                </td>
                <td className="px-4 py-3 text-center text-red-500 font-bold">
                  {s.errores ?? "—"}
                </td>
                <td className="px-4 py-3 text-center">
                  <span
                    className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded"
                    style={
                      s.modo === "tarea_casa"
                        ? { background: "#fef3c7", color: "#92400e" }
                        : { background: "#ecfdf5", color: "#065f46" }
                    }
                  >
                    {s.modo}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
 * EvolutionChart — gráfica SVG de scores promedio por dominio/semana
 * ═══════════════════════════════════════════════════════════════ */
function EvolutionChart({ evolution }) {
  const W = 720;
  const H = 240;
  const PAD_L = 40;
  const PAD_R = 20;
  const PAD_T = 20;
  const PAD_B = 40;

  /* Recolectar todas las semanas (eje X) */
  const weekSet = new Set();
  evolution.dominios.forEach((d) => d.puntos.forEach((p) => weekSet.add(p.semana)));
  const weeks = [...weekSet].sort();
  const xStep = (W - PAD_L - PAD_R) / Math.max(weeks.length - 1, 1);
  const xOf = (sem) => PAD_L + weeks.indexOf(sem) * xStep;
  const yOf = (score) => PAD_T + (1 - Math.min(100, Math.max(0, score)) / 100) * (H - PAD_T - PAD_B);

  const formatWeek = (w) => {
    const m = w.match(/^(\d{4})-W(\d{2})$/);
    if (!m) return w;
    return `S${m[2]}`;
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold flex items-center gap-2">
          <I name="show_chart" style={{ color: TEAL }} />
          Evolución por dominio cognitivo
        </h3>
        <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
          {evolution.total_sesiones} sesión(es) · {evolution.rango.desde} → {evolution.rango.hasta}
        </span>
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
        {/* Grilla horizontal cada 25 puntos */}
        {[0, 25, 50, 75, 100].map((v) => (
          <g key={v}>
            <line
              x1={PAD_L}
              y1={yOf(v)}
              x2={W - PAD_R}
              y2={yOf(v)}
              stroke="var(--ns-card-b)"
              strokeWidth="0.5"
              strokeDasharray={v === 0 || v === 100 ? "" : "3 4"}
            />
            <text
              x={PAD_L - 8}
              y={yOf(v) + 3}
              textAnchor="end"
              fontSize="9"
              fill="var(--ns-muted)"
            >
              {v}
            </text>
          </g>
        ))}

        {/* Línea de "promedio clínico" referencial en 70 */}
        <line
          x1={PAD_L}
          y1={yOf(70)}
          x2={W - PAD_R}
          y2={yOf(70)}
          stroke={TEAL}
          strokeWidth="1"
          strokeDasharray="6 4"
          strokeOpacity="0.4"
        />
        <text
          x={W - PAD_R}
          y={yOf(70) - 4}
          textAnchor="end"
          fontSize="9"
          fontWeight="bold"
          fill={TEAL}
          opacity="0.6"
        >
          objetivo
        </text>

        {/* Series por dominio */}
        {evolution.dominios.map((d, di) => {
          const color = DOMINIO_COLORS[d.dominio] || TEAL;
          const points = d.puntos
            .filter((p) => weeks.includes(p.semana))
            .map((p) => ({ x: xOf(p.semana), y: yOf(p.score_avg), v: p.score_avg, n: p.n }));
          if (points.length === 0) return null;
          return (
            <g key={di}>
              <polyline
                fill="none"
                stroke={color}
                strokeWidth="2.5"
                strokeLinejoin="round"
                strokeLinecap="round"
                points={points.map((p) => `${p.x},${p.y}`).join(" ")}
              />
              {points.map((p, pi) => (
                <g key={pi}>
                  <circle cx={p.x} cy={p.y} r="4" fill="#fff" stroke={color} strokeWidth="2" />
                  <text
                    x={p.x}
                    y={p.y - 8}
                    textAnchor="middle"
                    fontSize="9"
                    fontWeight="bold"
                    fill={color}
                  >
                    {Math.round(p.v)}
                  </text>
                </g>
              ))}
            </g>
          );
        })}

        {/* Etiquetas X */}
        {weeks.map((w, i) => (
          <text
            key={w}
            x={xOf(w)}
            y={H - 12}
            textAnchor="middle"
            fontSize="10"
            fill="var(--ns-muted)"
          >
            {formatWeek(w)}
          </text>
        ))}
      </svg>

      {/* Leyenda */}
      <div className="flex flex-wrap gap-3 mt-3">
        {evolution.dominios.map((d, i) => {
          const color = DOMINIO_COLORS[d.dominio] || TEAL;
          return (
            <div key={i} className="flex items-center gap-1.5 text-xs">
              <span className="w-3 h-3 rounded-full" style={{ background: color }} />
              <span className="font-bold">{DOMINIO_LABELS[d.dominio] || d.dominio}</span>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
