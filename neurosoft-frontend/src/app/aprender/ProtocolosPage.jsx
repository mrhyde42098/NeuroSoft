/* Protocolos clínicos paso a paso — consume protocolosClinicos.js */
import React, { useState } from "react";
import { Btn, I, TopBar } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { PROTOCOLOS, AREAS_PROTOCOLOS } from "../../data/protocolosClinicos.js";

export default function ProtocolosPage() {
  const [area, setArea] = useState("");
  const [sel, setSel] = useState(null);

  const filtered = PROTOCOLOS.filter((p) => !area || p.area === area);

  if (sel) {
    return (
      <>
        <TopBar title={sel.nombre}>
          <Btn variant="ghost" onClick={() => setSel(null)} className="text-xs">
            <I name="arrow_back" className="mr-1" />Volver
          </Btn>
        </TopBar>
        <main className="p-8 max-w-3xl mx-auto space-y-4">
          <p className="text-sm leading-relaxed" style={{ color: "var(--ns-muted)" }}>{sel.descripcion}</p>
          <div className="flex flex-wrap gap-2 text-[10px]">
            <span className="px-2 py-0.5 rounded-full font-bold" style={{ background: `${TEAL}15`, color: TEAL }}>
              Evidencia {sel.nivel_evidencia}
            </span>
            {sel.tiempo_estimado_min > 0 && (
              <span className="px-2 py-0.5 rounded-full" style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
                ~{sel.tiempo_estimado_min} min
              </span>
            )}
          </div>
          <ol className="space-y-4">
            {sel.pasos.map((paso) => (
              <li key={paso.orden} className="p-4 rounded-xl border" style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
                <p className="text-xs font-bold mb-1" style={{ color: TEAL }}>
                  Paso {paso.orden} — {paso.titulo}
                </p>
                <p className="text-sm leading-relaxed mb-2">{paso.descripcion}</p>
                {paso.instrumentos?.length > 0 && (
                  <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
                    <strong>Instrumentos:</strong> {paso.instrumentos.join(" · ")}
                  </p>
                )}
                {paso.tecnicas?.length > 0 && (
                  <p className="text-[10px] mt-1" style={{ color: "var(--ns-muted)" }}>
                    <strong>Técnicas:</strong> {paso.tecnicas.join(" · ")}
                    {paso.sesiones ? ` · Sesiones ${paso.sesiones}` : ""}
                  </p>
                )}
                {paso.tiempo_min != null && (
                  <p className="text-[10px] mt-1" style={{ color: "var(--ns-muted)" }}>~{paso.tiempo_min} min</p>
                )}
              </li>
            ))}
          </ol>
          {sel.referencias?.length > 0 && (
            <div className="pt-2 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
              <p className="text-[10px] font-bold mb-1" style={{ color: "var(--ns-muted)" }}>Referencias</p>
              <ul className="text-[10px] space-y-0.5" style={{ color: "var(--ns-muted)" }}>
                {sel.referencias.map((r) => <li key={r}>· {r}</li>)}
              </ul>
            </div>
          )}
        </main>
      </>
    );
  }

  return (
    <>
      <TopBar title="Protocolos clínicos" />
      <main className="p-8 max-w-5xl mx-auto space-y-4">
        <p className="text-sm max-w-2xl" style={{ color: "var(--ns-muted)" }}>
          Guías paso a paso para evaluación neuropsicológica e intervención psicológica. Basadas en guías internacionales y normativa colombiana.
        </p>
        <div className="flex flex-wrap gap-2">
          <button type="button" onClick={() => setArea("")}
            className="px-3 py-1.5 rounded-full text-xs font-bold"
            style={!area ? { background: TEAL, color: "#fff" } : { background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
            Todas
          </button>
          {AREAS_PROTOCOLOS.map((a) => (
            <button key={a.id} type="button" onClick={() => setArea(a.id)}
              className="px-3 py-1.5 rounded-full text-xs font-bold"
              style={area === a.id ? { background: TEAL, color: "#fff" } : { background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
              {a.label}
            </button>
          ))}
        </div>
        <div className="grid md:grid-cols-2 gap-3">
          {filtered.map((p) => (
            <button key={p.id} type="button" onClick={() => setSel(p)}
              className="text-left p-5 rounded-xl border hover:shadow-md transition-all"
              style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
              <p className="font-bold text-sm mb-1">{p.nombre}</p>
              <p className="text-xs line-clamp-2" style={{ color: "var(--ns-muted)" }}>{p.descripcion}</p>
              <p className="text-[10px] mt-2 font-bold" style={{ color: TEAL }}>
                {p.pasos.length} pasos · Evidencia {p.nivel_evidencia}
              </p>
            </button>
          ))}
        </div>
      </main>
    </>
  );
}
