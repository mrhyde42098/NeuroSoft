/* Botón de acción rápida — icono + título + subtítulo */
import React from "react";
import { I } from "./primitives.jsx";
import { TYPOGRAPHY } from "./tokens.js";

export default function ActionTile({ icon, title, subtitle, onClick, badge }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="text-left rounded-xl border p-4 w-full transition-all hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500/40"
      style={{
        background: "var(--ns-card)",
        borderColor: "var(--ns-card-b)",
      }}
    >
      <div className="flex items-start gap-3">
        <span
          className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
          style={{ background: "var(--ns-bg)", color: "#0D9488" }}
        >
          <I name={icon} />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span
              className="font-semibold truncate"
              style={{ fontSize: TYPOGRAPHY.scale.body.size, color: "var(--ns-text)" }}
            >
              {title}
            </span>
            {badge && (
              <span className="text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded bg-black/5" style={{ color: "var(--ns-muted)" }}>
                {badge}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="text-xs mt-0.5 line-clamp-2" style={{ color: "var(--ns-muted)" }}>
              {subtitle}
            </p>
          )}
        </div>
        <I name="chevron_right" className="text-lg opacity-40 shrink-0 mt-1" />
      </div>
    </button>
  );
}
