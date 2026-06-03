/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/PublicRehabViewer.jsx — Vista pública del paciente
 * ───────────────────────────────────────────────────────────────────────
 * Se monta en la ruta /shared/rehab/{token} (definida en App.jsx).
 * NO requiere login; consume `/api/v1/public/rehab/{token}` y
 * `/api/v1/public/rehab/{token}/result` (whitelisted en main.py).
 *
 * UI minimalista enfocada en el paciente:
 *   - Saludo personalizado por primer nombre
 *   - Lista de actividades asignadas en su plan
 *   - Al iniciar una actividad, lanza el componente correspondiente
 *   - Al terminar, envía el resultado al backend y muestra confirmación
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { API } from "../../api/client.js";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL, TEAL_LIGHT, NAVY, CREAM, _COLORS } from "../../ui/tokens.js";
import StroopActivity from "./StroopActivity.jsx";
import NBackActivity from "./NBackActivity.jsx";
import FluencyActivity from "./FluencyActivity.jsx";
import TachadoActivity from "./TachadoActivity.jsx";
import CorsiBlocks from "../evaluation/CorsiBlocks.jsx";
import SpacedRetrievalActivity from "./SpacedRetrievalActivity.jsx";
import MentalRotationActivity from "./MentalRotationActivity.jsx";
import EkmanRecognitionActivity from "./EkmanRecognitionActivity.jsx";

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
};

const ICONS = {
  stroop: "psychology",
  n_back: "grid_view",
  fluency_verbal: "edit_note",
  corsi_forward: "grid_view",
  corsi_backward: "grid_view",
  tachado: "highlight_alt",
};

export default function PublicRehabViewer({ token }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [running, setRunning] = useState(null);
  const [completed, setCompleted] = useState(new Set());
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    fetch(`${API}/api/v1/public/rehab/${token}`)
      .then((r) => r.json().then((b) => ({ ok: r.ok, body: b })))
      .then(({ ok, body }) => {
        if (!ok) throw body;
        setData(body);
      })
      .catch((e) => {
        const code = e?.detail?.code || "";
        if (code === "REHAB_LINK_EXPIRED") {
          setError("El link ha expirado. Pídele uno nuevo a tu profesional.");
        } else if (code === "REHAB_LINK_NOT_FOUND") {
          setError("El link no existe o ya fue revocado.");
        } else {
          setError("No se pudo cargar el plan.");
        }
      });
  }, [token]);

  const handleFinish = async (result) => {
    try {
      const res = await fetch(`${API}/api/v1/public/rehab/${token}/result`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          activity_slug: running.slug,
          parametros: result.params,
          resultado: result,
          duracion_seg: result.duracion_seg,
        }),
      });
      if (!res.ok) throw await res.json();
      setCompleted((s) => new Set([...s, running.slug]));
      setFeedback({ type: "ok", msg: "¡Actividad enviada! Tu profesional la verá pronto." });
    } catch {
      setFeedback({
        type: "err",
        msg: "No se pudo enviar tu resultado. Intenta de nuevo en un momento.",
      });
    }
    setRunning(null);
    setTimeout(() => setFeedback(null), 5000);
  };

  /* ─── ERROR ─────────────────────────────────────────── */
  if (error) {
    return (
      <Shell>
        <Card className="p-12 max-w-lg mx-auto text-center">
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6"
            style={{ background: "#fee2e2", color: "#dc2626" }}
          >
            <I name="error_outline" className="text-3xl" />
          </div>
          <h2 className="text-xl font-extrabold mb-3">Link no disponible</h2>
          <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
            {error}
          </p>
        </Card>
      </Shell>
    );
  }

  /* ─── LOADING ───────────────────────────────────────── */
  if (!data) {
    return (
      <Shell>
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-10 h-10 border-4 border-teal-200 border-t-teal-600 rounded-full" />
        </div>
      </Shell>
    );
  }

  /* ─── RUNNING ───────────────────────────────────────── */
  if (running) {
    const Comp = ACTIVITY_COMPONENTS[running.slug];
    if (Comp) {
      return (
        <Shell>
          <Comp
            params={running.parametros || {}}
            onFinish={handleFinish}
            onCancel={() => setRunning(null)}
          />
        </Shell>
      );
    }
    return (
      <Shell>
        <Card className="p-8 text-center max-w-lg mx-auto">
          <p className="font-bold mb-3">Actividad aún no disponible</p>
          <Btn onClick={() => setRunning(null)}>Volver</Btn>
        </Card>
      </Shell>
    );
  }

  /* ─── HOME ──────────────────────────────────────────── */
  return (
    <Shell>
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold mb-2">
          Hola{data.patient_first_name ? `, ${data.patient_first_name}` : ""} 👋
        </h1>
        <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
          Estas son tus actividades de esta semana. Hazlas con calma, en un lugar tranquilo.
        </p>
      </div>

      {feedback && (
        <Card
          className="p-4 mb-6 max-w-2xl mx-auto"
          style={{
            borderLeft: `4px solid ${feedback.type === "ok" ? "#10b981" : "#dc2626"}`,
          }}
        >
          <p className="text-sm font-bold flex items-center gap-2" style={{ color: feedback.type === "ok" ? "#065f46" : "#991b1b" }}>
            <I name={feedback.type === "ok" ? "check_circle" : "error"} fill className="text-base" />
            {feedback.msg}
          </p>
        </Card>
      )}

      {(!data.actividades || data.actividades.length === 0) ? (
        <Card className="p-12 max-w-lg mx-auto text-center">
          <I name="hourglass_empty" className="text-5xl mb-4" style={{ color: "var(--ns-muted)" }} />
          <p className="font-bold mb-2">Tu profesional aún no ha asignado actividades.</p>
          <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
            Vuelve a abrir este link más tarde.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto">
          {data.actividades.map((a, i) => {
            const done = completed.has(a.slug);
            return (
              <Card key={i} className="p-6">
                <div className="flex items-start gap-4">
                  <div
                    className="w-14 h-14 rounded-2xl flex items-center justify-center shrink-0"
                    style={{ background: `${TEAL}15`, color: TEAL }}
                  >
                    <I name={ICONS[a.slug] || "extension"} className="text-2xl" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-extrabold text-base mb-1">{a.nombre || a.slug}</h3>
                    {a.dominio && (
                      <p className="text-xs mb-3" style={{ color: "var(--ns-muted)" }}>
                        {a.dominio.replace(/_/g, " ")}
                      </p>
                    )}
                    {done ? (
                      <span
                        className="inline-flex items-center gap-1 text-xs font-bold px-3 py-1 rounded-full"
                        style={{ background: "#ecfdf5", color: "#065f46" }}
                      >
                        <I name="check_circle" fill className="text-sm" />
                        Hecha
                      </span>
                    ) : (
                      <Btn
                        className="text-xs"
                        onClick={() => setRunning(a)}
                        disabled={!ACTIVITY_COMPONENTS[a.slug]}
                      >
                        <I name="play_arrow" className="text-sm" />
                        {ACTIVITY_COMPONENTS[a.slug] ? "Comenzar" : "Próximamente"}
                      </Btn>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      <p className="text-center text-[10px] mt-12 font-bold uppercase tracking-widest" style={{ color: "var(--ns-muted)" }}>
        NeuroSoft · Estimulación cognitiva
      </p>
    </Shell>
  );
}

/* Wrapper visual sin sidebar — para que el paciente no vea controles internos */
function Shell({ children }) {
  return (
    <div
      className="min-h-screen"
      style={{
        background: CREAM,
        fontFamily: "'Manrope',sans-serif",
        color: NAVY,
      }}
    >
      <header
        className="sticky top-0 z-40 px-6 py-4 border-b flex items-center gap-3"
        style={{ background: "rgba(253,251,247,0.92)", backdropFilter: "blur(12px)", borderColor: "rgba(0,0,0,0.06)" }}
      >
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{ background: NAVY }}
        >
          <I name="psychology" fill className="text-xl" style={{ color: TEAL_LIGHT }} />
        </div>
        <div>
          <p className="font-extrabold leading-none">
            Neuro<span style={{ color: TEAL }}>Soft</span>
          </p>
          <p className="text-[10px] font-bold uppercase tracking-widest" style={{ color: "#94a3b8" }}>
            Tus actividades
          </p>
        </div>
      </header>
      <main className="p-6 max-w-4xl mx-auto">{children}</main>
    </div>
  );
}
