/* Popover accesible — Esc cierra, click-outside cierra */
import React, { useEffect, useRef } from "react";

export default function Popover({ open, onClose, anchorRef, children, className = "" }) {
  const panelRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e) => { if (e.key === "Escape") onClose?.(); };
    const onClick = (e) => {
      if (panelRef.current?.contains(e.target)) return;
      if (anchorRef?.current?.contains(e.target)) return;
      onClose?.();
    };
    window.addEventListener("keydown", onKey);
    document.addEventListener("mousedown", onClick);
    return () => {
      window.removeEventListener("keydown", onKey);
      document.removeEventListener("mousedown", onClick);
    };
  }, [open, onClose, anchorRef]);

  if (!open) return null;

  return (
    <div
      ref={panelRef}
      role="dialog"
      className={`absolute z-50 mt-2 min-w-[200px] rounded-lg border p-3 shadow-lg ${className}`}
      style={{
        background: "var(--ns-card)",
        borderColor: "var(--ns-card-b)",
        boxShadow: "0 10px 20px -6px rgba(30,41,59,0.12)",
      }}
    >
      {children}
    </div>
  );
}
