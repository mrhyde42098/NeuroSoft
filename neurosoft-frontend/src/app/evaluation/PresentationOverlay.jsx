/* Modal pantalla completa para presentar estímulo al paciente */

import React, { useEffect } from "react";
import { I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

export default function PresentationOverlay({
  open,
  onClose,
  stimulus,
  label,
  onPrev,
  onNext,
  hasPrev,
  hasNext,
}) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowLeft" && hasPrev && onPrev) onPrev();
      if (e.key === "ArrowRight" && hasNext && onNext) onNext();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose, onPrev, onNext, hasPrev, hasNext]);

  if (!open || !stimulus) return null;

  return (
    <div
      className="fixed inset-0 z-[200] flex flex-col"
      style={{ background: "rgba(15, 23, 42, 0.92)" }}
      role="dialog"
      aria-modal="true"
      aria-label="Presentación de estímulo"
    >
      <div className="flex items-center justify-between px-4 py-3 text-white">
        <p className="text-sm font-bold truncate flex-1">{label || stimulus.nombre}</p>
        <div className="flex items-center gap-2">
          {hasPrev && (
            <button
              type="button"
              onClick={onPrev}
              className="p-2 rounded-lg hover:bg-white/10"
              aria-label="Ítem anterior"
            >
              <I name="chevron_left" />
            </button>
          )}
          {hasNext && (
            <button
              type="button"
              onClick={onNext}
              className="p-2 rounded-lg hover:bg-white/10"
              aria-label="Ítem siguiente"
            >
              <I name="chevron_right" />
            </button>
          )}
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-white/10 font-bold text-xs px-3"
            style={{ background: TEAL }}
          >
            Cerrar (Esc)
          </button>
        </div>
      </div>
      <div className="flex-1 flex items-center justify-center p-6 min-h-0">
        {stimulus.contenido_base64 ? (
          <img
            src={stimulus.contenido_base64}
            alt={stimulus.nombre || "Estímulo"}
            className="max-w-full max-h-full object-contain rounded-lg shadow-2xl bg-white"
          />
        ) : (
          <p className="text-white/70 text-sm">Sin imagen</p>
        )}
      </div>
    </div>
  );
}
