/* Card editorial — cabecera tipográfica, sin border-l-4 de color */
import React from "react";
import { I } from "./primitives.jsx";
import { TYPOGRAPHY } from "./tokens.js";

export default function SectionCard({
  title,
  subtitle,
  icon,
  eyebrow,
  children,
  className = "",
  headerRight,
  collapsible = false,
  defaultOpen = true,
}) {
  const [open, setOpen] = React.useState(defaultOpen);

  return (
    <section
      className={`rounded-xl border ${className}`}
      style={{
        background: "var(--ns-card)",
        borderColor: "var(--ns-card-b)",
        boxShadow: "0 1px 0 rgba(30,41,59,0.03), 0 1px 3px rgba(30,41,59,0.04)",
      }}
    >
      {(title || eyebrow) && (
        <header
          className="flex items-start justify-between gap-3 px-5 pt-4 pb-3 border-b"
          style={{ borderColor: "var(--ns-card-b)" }}
        >
          <div className="min-w-0 flex-1">
            {eyebrow && (
              <p
                className="mb-1 uppercase tracking-widest"
                style={{
                  fontSize: TYPOGRAPHY.scale.label.size,
                  fontWeight: TYPOGRAPHY.scale.label.weight,
                  letterSpacing: "0.08em",
                  color: "var(--ns-muted)",
                }}
              >
                {eyebrow}
              </p>
            )}
            {title && (
              <h2
                className="flex items-center gap-2"
                style={{
                  fontFamily: TYPOGRAPHY.fontSerif,
                  fontSize: TYPOGRAPHY.scale.h3.size,
                  fontWeight: TYPOGRAPHY.scale.h3.weight,
                  color: "var(--ns-text)",
                }}
              >
                {icon && <I name={icon} className="text-lg opacity-70" />}
                {title}
              </h2>
            )}
            {subtitle && (
              <p className="mt-1 text-sm" style={{ color: "var(--ns-muted)" }}>
                {subtitle}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {headerRight}
            {collapsible && (
              <button
                type="button"
                onClick={() => setOpen((o) => !o)}
                className="p-1 rounded-md hover:bg-black/5"
                aria-expanded={open}
              >
                <I name={open ? "expand_less" : "expand_more"} />
              </button>
            )}
          </div>
        </header>
      )}
      {(!collapsible || open) && (
        <div className="p-5">{children}</div>
      )}
    </section>
  );
}
