import React, { useEffect, useMemo, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { useConfirm, useToast } from "../../contexts.jsx";
import {
  Btn, Card, EmptyState, I, Input, Label, MsgBanner,
  Sel, Skeleton, TopBar, Txta,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { DOMINIO_COLORS, DOMINIO_LABELS, ACTIVITY_COMPONENTS } from "./rehabConstants.js";

export default function ActivitiesTab({ patientId, setMsg }) {
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
