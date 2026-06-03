/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/TachadoActivity.jsx — Test de cancelación / tachado
 * ───────────────────────────────────────────────────────────────────────
 * Mide atención sostenida y selectiva, búsqueda visual.
 *
 * Mecánica:
 *   1. Se genera una matriz rows×cols con letras al azar.
 *   2. El paciente debe hacer click sobre cada `target` (p.ej. la letra A).
 *   3. Al terminar (botón "Listo"): se cuentan aciertos, falsos positivos,
 *      omisiones y se mide tiempo total.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { _useEffect, useMemo, useRef, useState } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

const generateGrid = (rows, cols, target, targetRatio = 0.18) => {
  const total = rows * cols;
  const grid = [];
  for (let i = 0; i < total; i++) {
    if (Math.random() < targetRatio) {
      grid.push(target);
    } else {
      let other;
      do {
        other = ALPHABET[Math.floor(Math.random() * ALPHABET.length)];
      } while (other === target);
      grid.push(other);
    }
  }
  return grid;
};

export default function TachadoActivity({ params = {}, onFinish, onCancel }) {
  const target = (params.target || "A").toUpperCase();
  const rows = params.rows ?? 10;
  const cols = params.cols ?? 15;

  const gridRef = useRef(generateGrid(rows, cols, target));
  const [phase, setPhase] = useState("intro");
  const [marked, setMarked] = useState(new Set());
  const startedAtRef = useRef(0);

  const total = rows * cols;
  const targetCount = useMemo(
    () => gridRef.current.filter((c) => c === target).length,
    [target]
  );

  const toggle = (i) => {
    setMarked((s) => {
      const next = new Set(s);
      if (next.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });
  };

  const finish = () => {
    const elapsed = Math.floor((Date.now() - startedAtRef.current) / 1000);
    let hits = 0;
    let fps = 0;
    marked.forEach((i) => {
      if (gridRef.current[i] === target) hits += 1;
      else fps += 1;
    });
    const omis = targetCount - hits;
    const score = targetCount
      ? Math.max(0, Math.round(((hits - 0.5 * fps) / targetCount) * 100))
      : 0;
    const result = {
      score,
      aciertos: hits,
      errores: fps,
      omisiones: omis,
      total_targets: targetCount,
      total_celdas: total,
      duracion_seg: elapsed,
      params: { target, rows, cols },
    };
    setPhase("done");
    if (onFinish) onFinish(result);
  };

  /* ─── INTRO ─────────────────────────────────────────────── */
  if (phase === "intro") {
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center">
        <div
          className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
          style={{ background: `${TEAL}15`, color: TEAL }}
        >
          <I name="highlight_alt" className="text-4xl" />
        </div>
        <h3 className="text-2xl font-extrabold mb-3">Tachado · Atención sostenida</h3>
        <p className="text-sm leading-relaxed mb-6" style={{ color: "var(--ns-muted)" }}>
          Verás una matriz con letras. Haz <strong>click</strong> sobre cada letra
          objetivo. Trabaja de izquierda a derecha y de arriba abajo, sin
          saltarte ninguna.
        </p>
        <div
          className="rounded-2xl p-6 mb-8"
          style={{ background: `${TEAL}10`, border: `2px solid ${TEAL}40` }}
        >
          <p className="text-[10px] font-bold uppercase tracking-widest mb-2" style={{ color: "var(--ns-muted)" }}>
            Objetivo
          </p>
          <p className="text-7xl font-extrabold" style={{ color: TEAL }}>
            {target}
          </p>
        </div>
        <p className="text-xs mb-8" style={{ color: "var(--ns-muted)" }}>
          Si te equivocas, vuelve a hacer click para deseleccionar.
        </p>
        <div className="flex justify-center gap-3">
          {onCancel && (
            <Btn v="outline" onClick={onCancel}>
              Cancelar
            </Btn>
          )}
          <Btn
            onClick={() => {
              startedAtRef.current = Date.now();
              setPhase("running");
            }}
          >
            <I name="play_arrow" />
            Comenzar
          </Btn>
        </div>
      </Card>
    );
  }

  /* ─── DONE ──────────────────────────────────────────────── */
  if (phase === "done") {
    let hits = 0,
      fps = 0;
    marked.forEach((i) => {
      if (gridRef.current[i] === target) hits += 1;
      else fps += 1;
    });
    const omis = targetCount - hits;
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center">
        <div
          className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
          style={{ background: "#10b98115", color: "#10b981" }}
        >
          <I name="check_circle" fill className="text-4xl" />
        </div>
        <h3 className="text-2xl font-extrabold mb-2">¡Sesión completada!</h3>
        <div className="grid grid-cols-3 gap-3 mt-8">
          <Card className="p-4">
            <p className="text-3xl font-extrabold" style={{ color: TEAL }}>{hits}/{targetCount}</p>
            <p className="text-[10px] font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Aciertos
            </p>
          </Card>
          <Card className="p-4">
            <p className="text-3xl font-extrabold text-red-500">{fps}</p>
            <p className="text-[10px] font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Falsos positivos
            </p>
          </Card>
          <Card className="p-4">
            <p className="text-3xl font-extrabold text-orange-500">{omis}</p>
            <p className="text-[10px] font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Omisiones
            </p>
          </Card>
        </div>
      </Card>
    );
  }

  /* ─── RUNNING ───────────────────────────────────────────── */
  return (
    <div className="max-w-3xl mx-auto">
      <Card className="p-4 mb-4">
        <div className="flex items-center justify-between text-sm">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
              Objetivo:
            </span>{" "}
            <span className="text-2xl font-extrabold ml-2" style={{ color: TEAL }}>
              {target}
            </span>
          </div>
          <div className="text-xs font-bold" style={{ color: TEAL }}>
            {marked.size} marcadas
          </div>
        </div>
      </Card>

      <Card className="p-4 overflow-x-auto">
        <div
          className="grid gap-1.5 mx-auto"
          style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`, maxWidth: 720 }}
        >
          {gridRef.current.map((c, i) => {
            const isMarked = marked.has(i);
            return (
              <button
                key={i}
                onClick={() => toggle(i)}
                className="aspect-square rounded font-extrabold text-base transition-all hover:scale-105"
                style={{
                  background: isMarked ? TEAL : "var(--ns-subtle)",
                  color: isMarked ? "#fff" : "var(--ns-text)",
                  boxShadow: isMarked ? "0 4px 12px -2px rgba(13,148,136,0.4)" : "none",
                }}
              >
                {c}
              </button>
            );
          })}
        </div>
      </Card>

      <div className="flex justify-end mt-6">
        <Btn onClick={finish}>
          <I name="check" />
          Listo
        </Btn>
      </div>
    </div>
  );
}
