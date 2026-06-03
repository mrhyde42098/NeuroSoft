/* ═══════════════════════════════════════════════════════════════════════
 * src/app/dashboard/WhatNewModal.jsx
 * ───────────────────────────────────────────────────────────────────────
 * Modal que se muestra UNA VEZ cuando la app detecta que se instaló
 * una versión nueva (comparando con la última versión vista en safeLS).
 *
 * Funcionamiento:
 *   1. El Dashboard compara `api_version` actual con `ns_last_seen_version`
 *   2. Si son diferentes → muestra este modal
 *   3. Al cerrar → guarda la versión actual en safeLS
 *   4. No se vuelve a mostrar para esta versión
 *
 * Accesible también desde:
 *   - Sidebar → "Registro de cambios"
 *   - HelpPage → "Novedades"
 * ═══════════════════════════════════════════════════════════════════════ */

import React from "react";
import { I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { CHANGELOG, latestVersion } from "../../data/changelog.js";
import { safeLS } from "../../utils/safeLS.js";

export default function WhatNewModal({ show, onClose, version = null }) {
  if (!show) return null;

  const entry = version ? CHANGELOG.find((c) => c.version === version) : latestVersion();
  if (!entry) return null;

  const dismiss = () => {
    safeLS.set("ns_last_seen_version", entry.version);
    onClose?.();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.5)", backdropFilter: "blur(4px)" }}
      onClick={dismiss}
    >
      <div
        className="rounded-2xl shadow-2xl max-w-lg w-full max-h-[80vh] overflow-hidden"
        style={{ background: "var(--ns-card)" }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header con gradiente */}
        <div
          className="p-6 text-center"
          style={{
            background: `linear-gradient(135deg, ${entry.color}15, ${TEAL}10)`,
          }}
        >
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-3"
            style={{ background: `${entry.color}20` }}>
            <I name={entry.icono} className="text-3xl" style={{ color: entry.color }} fill />
          </div>
          <h2 className="text-xl font-extrabold" style={{ color: "var(--ns-text)" }}>
            ¡Novedades en NeuroSoft!
          </h2>
          <p className="text-sm mt-1" style={{ color: "var(--ns-muted)" }}>
            {entry.titulo} · {new Date(entry.fecha).toLocaleDateString("es-CO", { year: "numeric", month: "long", day: "numeric" })}
          </p>
        </div>

        {/* Lista de cambios */}
        <div className="p-6 overflow-y-auto" style={{ maxHeight: "50vh" }}>
          <p className="text-xs font-extrabold uppercase tracking-wider mb-3" style={{ color: "var(--ns-muted)" }}>
            Novedades de esta versión
          </p>
          <ul className="space-y-2.5">
            {entry.cambios.map((c, i) => (
              <li key={i} className="flex items-start gap-3 text-sm leading-relaxed" style={{ color: "var(--ns-text)" }}>
                <span className="mt-1 shrink-0 w-1.5 h-1.5 rounded-full" style={{ background: entry.color }} />
                <span>{c}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Footer */}
        <div className="p-4 border-t flex items-center justify-between" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
          <span className="text-xs" style={{ color: "var(--ns-muted)" }}>
            {new Date(entry.fecha).toLocaleDateString("es-CO", { year: "numeric", month: "long", day: "numeric" })}
          </span>
          <button
            onClick={dismiss}
            className="px-5 py-2 rounded-full text-sm font-bold text-white hover:opacity-90 transition-all"
            style={{ background: entry.color }}
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
}
