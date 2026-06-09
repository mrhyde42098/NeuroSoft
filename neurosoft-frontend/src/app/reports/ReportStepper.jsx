import React from "react";
import { Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

export const REPORT_STEPS = [
  { label: "Paciente", icon: "person" },
  { label: "Evaluación", icon: "clinical_notes" },
  { label: "Previsualizar", icon: "preview" },
  { label: "Descargar", icon: "download" },
];

export default function ReportStepper({ step }) {
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between gap-2">
        {REPORT_STEPS.map((s, i) => {
          const active = i === step;
          const done = i < step;
          return (
            <React.Fragment key={s.label}>
              <div className="flex items-center gap-3 flex-shrink-0" style={{ opacity: active || done ? 1 : 0.5 }}>
                <div
                  className="w-9 h-9 rounded-full flex items-center justify-center font-extrabold text-sm transition-all"
                  style={
                    active
                      ? { background: TEAL, color: "#fff", boxShadow: "0 8px 20px -4px rgba(13,148,136,0.5)", transform: "scale(1.1)" }
                      : done
                      ? { background: "#10b981", color: "#fff" }
                      : { background: "var(--ns-subtle)", color: "var(--ns-muted)" }
                  }
                >
                  {done ? <I name="check" fill className="text-base" /> : <I name={s.icon} className="text-base" />}
                </div>
                <div className="text-left">
                  <p className="text-[9px] font-extrabold uppercase tracking-widest" style={{ color: active ? TEAL : "var(--ns-muted)" }}>
                    Paso {i + 1}
                  </p>
                  <p className="text-xs font-bold" style={{ color: active ? "var(--ns-text)" : "var(--ns-muted)" }}>
                    {s.label}
                  </p>
                </div>
              </div>
              {i < REPORT_STEPS.length - 1 && (
                <div className="flex-1 h-0.5 rounded-full mx-1" style={{ background: i < step ? "#10b981" : "var(--ns-subtle)" }} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </Card>
  );
}
