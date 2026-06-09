import React from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

/**
 * Shell común para actividades cognitivas: intro → contenido → acciones.
 */
export function ActivityIntro({ icon, title, description, children, onStart, onCancel }) {
  return (
    <Card className="p-8 max-w-2xl mx-auto text-center">
      <div
        className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
        style={{ background: `${TEAL}15`, color: TEAL }}
      >
        <I name={icon} className="text-4xl" />
      </div>
      <h3 className="text-2xl font-extrabold mb-3">{title}</h3>
      {description ? (
        <p className="text-sm leading-relaxed mb-6" style={{ color: "var(--ns-muted)" }}>
          {description}
        </p>
      ) : null}
      {children}
      <div className="flex justify-center gap-3 mt-6">
        {onCancel ? (
          <Btn v="outline" onClick={onCancel}>
            Cancelar
          </Btn>
        ) : null}
        <Btn onClick={onStart}>
          <I name="play_arrow" />
          Comenzar
        </Btn>
      </div>
    </Card>
  );
}

export function ActivityDone({ title, children, onClose }) {
  return (
    <Card className="p-8 max-w-2xl mx-auto text-center">
      <div
        className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
        style={{ background: "#10b98115", color: "#10b981" }}
      >
        <I name="check_circle" fill className="text-4xl" />
      </div>
      <h3 className="text-2xl font-extrabold mb-4">{title}</h3>
      {children}
      {onClose ? (
        <Btn className="mt-6" onClick={onClose}>
          Cerrar
        </Btn>
      ) : null}
    </Card>
  );
}

export function ActivityFooter({ onCancel, children }) {
  return (
    <div className="flex justify-between items-center gap-3 mt-4">
      {onCancel ? (
        <Btn v="outline" onClick={onCancel}>
          Cancelar
        </Btn>
      ) : (
        <span />
      )}
      <div className="flex gap-2">{children}</div>
    </div>
  );
}
