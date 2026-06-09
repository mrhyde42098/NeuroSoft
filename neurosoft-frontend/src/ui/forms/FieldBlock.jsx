import React from "react";
import { I } from "../primitives.jsx";
import { TEAL } from "../tokens.js";

/** Agrupa campos en sección visual con título e icono. */
export default function FieldBlock({ title, icon, children, className = "" }) {
  return (
    <div
      className={`rounded-2xl p-5 border space-y-4 ${className}`}
      style={{ borderColor: `${TEAL}28`, background: `${TEAL}06` }}
    >
      {title ? (
        <p className="text-xs font-bold flex items-center gap-2" style={{ color: TEAL }}>
          {icon ? <I name={icon} className="text-sm" /> : null}
          {title}
        </p>
      ) : null}
      {children}
    </div>
  );
}
