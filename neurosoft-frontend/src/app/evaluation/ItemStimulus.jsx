/* Miniatura de estímulo por ítem + acción pantalla completa */

import React from "react";
import { I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

export default function ItemStimulus({ stimulus, onExpand, compact = false }) {
  if (!stimulus?.contenido_base64) return null;
  const h = compact ? "h-14 w-14" : "h-20 w-20";
  return (
    <div className="shrink-0 flex flex-col items-center gap-0.5">
      <button
        type="button"
        onClick={onExpand}
        className={`${h} rounded-lg border overflow-hidden bg-white hover:ring-2 transition-all`}
        style={{ borderColor: "var(--ns-card-b)", ["--tw-ring-color"]: TEAL }}
        title={stimulus.nombre || "Ver estímulo en pantalla completa"}
        aria-label="Ampliar estímulo"
      >
        <img
          src={stimulus.contenido_base64}
          alt={stimulus.nombre || "Estímulo"}
          className="w-full h-full object-contain"
        />
      </button>
      {!compact && (
        <button
          type="button"
          onClick={onExpand}
          className="text-[9px] font-bold flex items-center gap-0.5"
          style={{ color: TEAL }}
        >
          <I name="fullscreen" className="text-[10px]" />
          Ampliar
        </button>
      )}
    </div>
  );
}
