import React, { useEffect, useMemo, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { useConfirm, useToast } from "../../contexts.jsx";
import {
  Btn, Card, EmptyState, I, Input, Label, MsgBanner,
  Sel, Skeleton, TopBar, Txta,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { DOMINIO_COLORS, DOMINIO_LABELS, ACTIVITY_COMPONENTS } from "./rehabConstants.js";
import { safeLS } from "../../utils/safeLS.js";

export default function PlanTab({ patientId, setMsg }) {
  const confirm = useConfirm();
  const _toast = useToast();
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
      let _result;
      if (editing.id) {
        // En PATCH no incluimos campos no editables
        const patch = { ...editing };
        delete patch.patient_id;
        delete patch.id;
        delete patch.evaluation_id;
        _result = await api.patch(`/api/v1/rehab/plans/${editing.id}`, patch);
      } else {
        _result = await api.post("/api/v1/rehab/plans", editing);
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
