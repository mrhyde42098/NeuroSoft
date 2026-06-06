/* Indicador editorial — número grande, sin borde de color */
import React, { useRef, useState } from "react";
import { I } from "./primitives.jsx";
import { TYPOGRAPHY } from "./tokens.js";
import Popover from "./Popover.jsx";

export default function StatTile({
  label,
  value,
  icon,
  onClick,
  popoverContent,
  hint,
}) {
  const [popOpen, setPopOpen] = useState(false);
  const ref = useRef(null);

  const inner = (
  <div
    ref={ref}
    className={`relative rounded-xl border p-4 transition-shadow ${onClick || popoverContent ? "cursor-pointer hover:shadow-md" : ""}`}
    style={{
      background: "var(--ns-card)",
      borderColor: "var(--ns-card-b)",
    }}
    onClick={() => {
      if (popoverContent) setPopOpen((o) => !o);
      onClick?.();
    }}
    role={onClick || popoverContent ? "button" : undefined}
    tabIndex={onClick || popoverContent ? 0 : undefined}
    onKeyDown={(e) => {
      if ((e.key === "Enter" || e.key === " ") && (onClick || popoverContent)) {
        e.preventDefault();
        if (popoverContent) setPopOpen((o) => !o);
        onClick?.();
      }
    }}
  >
    <div className="flex items-start justify-between gap-2">
      <div>
        <p
          className="uppercase tracking-widest mb-1"
          style={{
            fontSize: TYPOGRAPHY.scale.label.size,
            fontWeight: TYPOGRAPHY.scale.label.weight,
            color: "var(--ns-muted)",
          }}
        >
          {label}
        </p>
        <p
          style={{
            fontFamily: TYPOGRAPHY.fontSerif,
            fontSize: 32,
            fontWeight: 700,
            lineHeight: 1.1,
            color: "var(--ns-text)",
          }}
        >
          {value ?? "—"}
        </p>
        {hint && (
          <p className="text-xs mt-1" style={{ color: "var(--ns-muted)" }}>
            {hint}
          </p>
        )}
      </div>
      {icon && (
        <span
          className="w-9 h-9 rounded-lg flex items-center justify-center"
          style={{ background: "var(--ns-bg)", color: "var(--ns-muted)" }}
        >
          <I name={icon} />
        </span>
      )}
    </div>
    {popoverContent && (
      <Popover open={popOpen} onClose={() => setPopOpen(false)} anchorRef={ref}>
        {popoverContent}
      </Popover>
    )}
  </div>
  );
  return inner;
}
