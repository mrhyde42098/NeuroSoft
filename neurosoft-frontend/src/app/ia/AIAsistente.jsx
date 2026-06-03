/* ═══════════════════════════════════════════════════════════════════════
 * src/app/ia/AIAsistente.jsx — Asistente IA compacto con prompts especializados
 * ───────────────────────────────────────────────────────────────────────
 * §ai-prompts (2026-05-18): UI consume `GET /api/v1/ai/prompts` (catálogo
 * curado en backend) y permite al clínico ejecutar prompts especializados:
 *
 *   - mejorar_observacion_clinica  → pulir redacción manteniendo hallazgos
 *   - sugerir_dx_dsm5              → propone candidatos diagnósticos
 *   - explicar_discrepancia        → traduce discrepancia entre índices
 *   - redactar_recomendaciones     → recomendaciones por dominio
 *   - narrativa_integradora        → síntesis 6 dominios
 *   - revisar_pediatrico           → adapta lenguaje para infantil
 *
 * Cada prompt requiere variables específicas. Este componente recibe un
 * objeto `context` con todo lo disponible y el usuario elige el prompt;
 * el resultado se muestra inline para que el clínico copie/edite/integre.
 *
 * Diseño: panel desplegable con dropdown de prompts + área de salida +
 * disclaimer obligatorio cuando se usa.
 *
 * Props:
 *   - context     → { texto, edad, escolaridad, puntajes, observaciones,
 *                     motivo, dominios, fortalezas, etc. } (opcional, se
 *                     pasa solo lo que se tenga)
 *   - onApply     → (texto) => void  (callback al pulsar "Aplicar al texto")
 *   - compact     → boolean (modo minimal sin disclaimer expandido)
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { I } from "../../ui/primitives.jsx";
import { ACCENTS, TEAL, NAVY } from "../../ui/tokens.js";
import { useToast } from "../../contexts.jsx";
import { specializedAI, listSpecializedPrompts } from "./PanelIA.jsx";

const PLUM = ACCENTS?.plum || "#6D28D9";

export default function AIAsistente({ context = {}, onApply, compact = false }) {
  const toast = useToast();
  const [catalog, setCatalog] = useState(null);
  const [selected, setSelected] = useState("");
  const [output, setOutput] = useState("");
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState(false);
  const [provider, setProvider] = useState("");

  useEffect(() => {
    if (open && !catalog) {
      listSpecializedPrompts()
        .then(setCatalog)
        .catch(e => toast.error("No se pudo cargar el catálogo IA: " + (e.message || e)));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  /* Variables requeridas por cada prompt (se construyen desde context). */
  const buildVariables = (promptId) => {
    const c = context;
    const fmt = (v) => v == null ? "" : (typeof v === "string" ? v : JSON.stringify(v, null, 2));
    switch (promptId) {
      case "mejorar_observacion_clinica":
      case "revisar_pediatrico":
        return { texto: fmt(c.texto || c.observaciones || "") };
      case "sugerir_dx_dsm5":
        return {
          edad: fmt(c.edad),
          escolaridad: fmt(c.escolaridad),
          puntajes: fmt(c.puntajes),
          observaciones: fmt(c.observaciones),
          motivo: fmt(c.motivo),
        };
      case "explicar_discrepancia":
        return {
          nombre_a: fmt(c.nombre_a),
          valor_a: fmt(c.valor_a),
          nombre_b: fmt(c.nombre_b),
          valor_b: fmt(c.valor_b),
          diferencia: fmt(c.diferencia),
          significancia: fmt(c.significancia || "0.05"),
          contexto: fmt(c.contexto || c.observaciones),
        };
      case "redactar_recomendaciones":
        return {
          edad: fmt(c.edad),
          escolaridad: fmt(c.escolaridad),
          dominios_bajos: fmt(c.dominios_bajos || c.debilidades),
          fortalezas: fmt(c.fortalezas),
          contexto: fmt(c.contexto || c.observaciones),
        };
      case "narrativa_integradora":
        return {
          edad: fmt(c.edad),
          escolaridad: fmt(c.escolaridad),
          dominios: fmt(c.dominios),
          observaciones: fmt(c.observaciones),
        };
      default:
        return {};
    }
  };

  const ejecutar = async () => {
    if (!selected) {
      toast.warn("Elige un tipo de asistencia primero.");
      return;
    }
    const vars = buildVariables(selected);
    const empty = Object.entries(vars).filter(([, v]) => !v || !String(v).trim());
    if (empty.length > 0) {
      toast.warn(`Faltan datos: ${empty.map(e => e[0]).join(", ")}. Llena observaciones / puntajes primero.`);
      return;
    }
    setBusy(true);
    setOutput("");
    try {
      const r = await specializedAI(selected, vars);
      setOutput(r.content || "(sin respuesta)");
      setProvider(`${r.provider} · ${r.model}`);
    } catch (e) {
      toast.error("Error IA: " + (e.message || e));
    }
    setBusy(false);
  };

  const aplicar = () => {
    if (output && onApply) {
      onApply(output);
      toast.success("Texto aplicado.");
    }
  };

  if (!open) {
    return (
      <button onClick={() => setOpen(true)}
        className="text-xs font-semibold px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all hover:shadow-sm"
        style={{ background: `${PLUM}12`, color: PLUM, border: `1px solid ${PLUM}40` }}>
        <I name="auto_awesome" className="text-sm" />
        Asistente IA clínico
      </button>
    );
  }

  const selectedPrompt = catalog?.prompts?.find(p => p.id === selected);

  return (
    <div className="rounded-md border p-4 space-y-3"
      style={{ background: `${PLUM}06`, borderColor: `${PLUM}30` }}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <I name="auto_awesome" style={{ color: PLUM }} />
          <p className="ns-eyebrow" style={{ color: PLUM }}>Asistente IA clínico</p>
        </div>
        <button onClick={() => { setOpen(false); setOutput(""); setSelected(""); }}
          className="p-1 rounded hover:bg-gray-100" style={{ color: "var(--ns-muted)" }}>
          <I name="close" className="text-sm" />
        </button>
      </div>

      {!catalog ? (
        <p className="text-xs ns-serif-italic" style={{ color: "var(--ns-muted)" }}>
          Cargando catálogo de prompts…
        </p>
      ) : (
        <>
          <div>
            <p className="ns-eyebrow mb-1.5">Tipo de asistencia</p>
            <select value={selected} onChange={e => { setSelected(e.target.value); setOutput(""); }}
              className="w-full px-3 py-2 rounded-md text-sm"
              style={{ background: "var(--ns-input)", border: "1px solid var(--ns-card-b)", color: "var(--ns-text)" }}>
              <option value="">— Elige un tipo —</option>
              {catalog.prompts.map(p => (
                <option key={p.id} value={p.id}>{p.label}</option>
              ))}
            </select>
            {selectedPrompt && (
              <p className="text-[11px] ns-serif-italic mt-1.5" style={{ color: "var(--ns-muted)" }}>
                {selectedPrompt.description}
              </p>
            )}
          </div>

          <button onClick={ejecutar} disabled={busy || !selected}
            className="w-full py-2 rounded-md text-sm font-semibold transition-all disabled:opacity-50"
            style={{ background: PLUM, color: "#fff" }}>
            {busy ? (
              <span className="flex items-center justify-center gap-2">
                <span className="inline-block w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Generando…
              </span>
            ) : (
              <span className="flex items-center justify-center gap-1.5">
                <I name="play_arrow" className="text-sm" />
                Generar con IA
              </span>
            )}
          </button>

          {output && (
            <div className="space-y-2">
              <div className="rounded-md p-3 border" style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
                <p className="ns-eyebrow mb-1.5" style={{ color: TEAL }}>Salida IA</p>
                <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: "var(--ns-text)" }}>
                  {output}
                </p>
              </div>

              <div className="flex items-center justify-between gap-2">
                <span className="text-[10px] ns-mono" style={{ color: "var(--ns-muted)" }}>
                  {provider}
                </span>
                <div className="flex gap-2">
                  <button onClick={() => navigator.clipboard?.writeText(output)}
                    className="text-xs font-semibold px-3 py-1 rounded-md"
                    style={{ background: "var(--ns-subtle)", color: NAVY }}>
                    <I name="content_copy" className="text-xs mr-1" />
                    Copiar
                  </button>
                  {onApply && (
                    <button onClick={aplicar}
                      className="text-xs font-semibold px-3 py-1 rounded-md"
                      style={{ background: TEAL, color: "#fff" }}>
                      <I name="check" className="text-xs mr-1" />
                      Aplicar al texto
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* §clinical-disclaimer-v2: nota interna para el clínico — NO
            * aparece en el PDF como "se usó IA". El PDF lleva una cláusula
            * estándar de responsabilidad profesional (Ley 1090) sin
            * mencionar herramientas técnicas. */}
          {!compact && (
            <div className="rounded-md p-3 border-l-2" style={{ background: "var(--ns-subtle)", borderColor: ACCENTS?.amber || "#B45309" }}>
              <p className="ns-eyebrow mb-1" style={{ color: ACCENTS?.amber || "#B45309" }}>
                Recuerda
              </p>
              <p className="text-[11px] leading-relaxed" style={{ color: "var(--ns-muted)" }}>
                Esta es una herramienta de apoyo a tu redacción. Revisa, valida y modifica
                el resultado antes de incorporarlo al informe — tu juicio clínico es lo que
                respalda lo que firmas.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
