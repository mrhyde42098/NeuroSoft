/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/RehabPage.jsx — Página principal de Rehabilitación
 * ───────────────────────────────────────────────────────────────────────
 * Tres sub-pestañas:
 *   • Plan          → seleccionar paciente, crear/editar plan, firmar, compartir
 *   • Actividades   → catálogo de actividades, ejecutar
 *   • Sesiones      → timeline + gráfica de evolución por dominio
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { safeLS } from "../../utils/safeLS.js";
import PatientSelector from "../../ui/forms/PatientSelector.jsx";
import {
  Card, EmptyState, I, MsgBanner, TopBar,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { TABS } from "./rehabConstants.js";
import RehabPlanTab from "./RehabPlanTab.jsx";
import RehabActivitiesTab from "./RehabActivitiesTab.jsx";
import RehabSessionsTab from "./RehabSessionsTab.jsx";

export default function RehabPage() {
  const [tab, setTab] = useState("plan");
  const [patientId, setPatientId] = useState(
    safeLS.get("ns_sel_patient") || "",
  );
  const [msg, setMsg] = useState("");

  useEffect(() => () => safeLS.remove("ns_sel_patient"), []);

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

        <Card className="p-6">
          <PatientSelector
            value={patientId}
            onChange={(id) => {
              setPatientId(id);
              if (id) safeLS.set("ns_sel_patient", id);
            }}
            placeholder="— Seleccione —"
          />
        </Card>

        <div className="flex gap-2 flex-wrap">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
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
          <RehabPlanTab patientId={patientId} setMsg={setMsg} />
        ) : tab === "actividades" ? (
          <RehabActivitiesTab patientId={patientId} setMsg={setMsg} />
        ) : (
          <RehabSessionsTab patientId={patientId} />
        )}
      </main>
    </>
  );
}
