/* ═══════════════════════════════════════════════════════════════
 * src/ui/SelloProtegidoBadge.jsx — Marca visual discreta
 * ───────────────────────────────────────────────────────────────
 * §S5.1x: Identifica visualmente los ítems verbatim con copyright
 * sin interrumpir el flujo clínico. Diferencia respecto al
 * modal original (ahora solo one-time acceptance en install):
 *
 *   • No interrumpe la sesión.
 *   • Se ve como sello en esquina, no como popup.
 *   • Tooltip explica el porqué al hacer hover.
 *   • aria-label para lectores de pantalla.
 *
 * Modos:
 *   - inline: badge pequeño en línea con el texto
 *   - corner: badge absoluto en esquina superior derecha
 *   - footer: línea fina al pie del ítem
 * ═══════════════════════════════════════════════════════════════ */

import React from "react";
import { I } from "./primitives.jsx";

export function SelloProtegidoBadge({ testId, mode = "inline", size = "sm" }) {
  if (!testId) return null;

  const sizes = {
    xs: { fontSize: "9px", px: "4px", py: "1px", icon: "11px" },
    sm: { fontSize: "10px", px: "6px", py: "2px", icon: "12px" },
    md: { fontSize: "11px", px: "8px", py: "3px", icon: "14px" },
  };
  const s = sizes[size] || sizes.sm;

  const baseStyle = {
    display: "inline-flex",
    alignItems: "center",
    gap: "3px",
    fontSize: s.fontSize,
    fontWeight: 700,
    letterSpacing: "0.05em",
    textTransform: "uppercase",
    padding: `${s.py} ${s.px}`,
    borderRadius: "4px",
    background: "rgba(217, 119, 6, 0.12)",
    color: "#B45309",
    border: "1px solid rgba(217, 119, 6, 0.35)",
    cursor: "help",
    userSelect: "none",
  };

  const ariaLabel =
    "Material con copyright. El acceso a este ítem queda registrado en la " +
    "bitácora de auditoría clínica. Verifique la referencia al manual original " +
    "antes de aplicar o baremar.";

  const content = (
    <>
      <I name="copyright" className="material-symbols-outlined" style={{ fontSize: s.icon }} />
      © {testId}
    </>
  );

  if (mode === "corner") {
    return (
      <div
        role="img"
        aria-label={ariaLabel}
        title="Material con copyright — uso clínico exclusivamente. Acceso registrado en auditoría."
        style={{
          position: "absolute",
          top: "8px",
          right: "8px",
          ...baseStyle,
        }}
      >
        {content}
      </div>
    );
  }

  if (mode === "footer") {
    return (
      <p
        role="img"
        aria-label={ariaLabel}
        title="Material con copyright — uso clínico exclusivamente."
        style={{
          ...baseStyle,
          marginTop: "6px",
          fontStyle: "italic",
          opacity: 0.85,
        }}
      >
        {content}
      </p>
    );
  }

  // inline (default)
  return (
    <span
      role="img"
      aria-label={ariaLabel}
      title="Material con copyright — uso clínico exclusivamente."
      style={baseStyle}
    >
      {content}
    </span>
  );
}
