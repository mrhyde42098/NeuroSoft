/* ═══════════════════════════════════════════════════════════════════════
 * CubosPatterns.jsx — Estímulos SVG nativos para Diseño con Cubos
 * ───────────────────────────────────────────────────────────────────────
 * Renderiza los 14 diseños del subtest Diseño con Cubos (Kohs) para
 * WISC-IV y WAIS-III. Los patrones son geometría pura (triángulos
 * rojos/blancos) — NO son reproducciones literales de los diseños
 * originales con copyright, sino recreaciones geométricamente análogas
 * de dificultad progresiva, aptas para entrenamiento y referencia
 * visual en la aplicación NeuroSoft.
 *
 * Vocabulario de caras (como en los cubos de Kohs):
 *   W   = cara totalmente blanca
 *   R   = cara totalmente roja
 *   TL  = triángulo rojo en esquina superior-izquierda (diagonal ↘)
 *   TR  = triángulo rojo en esquina superior-derecha (diagonal ↙)
 *   BL  = triángulo rojo en esquina inferior-izquierda (diagonal ↙)
 *   BR  = triángulo rojo en esquina inferior-derecha (diagonal ↘)
 *
 * Autor: NeuroSoft — 2026
 * ═══════════════════════════════════════════════════════════════════════ */

import React from "react";

const RED = "#D32F2F";
const WHITE = "#FFFFFF";
const STROKE = "#1E293B";

/* ─── Renderizador de una sola cara ─────────────────────────────────── */
function Face({ x, y, size, type }) {
  const x2 = x + size, y2 = y + size;
  // Fondo + marco
  const rect = (
    <rect x={x} y={y} width={size} height={size}
          fill={WHITE} stroke={STROKE} strokeWidth="1.2" />
  );
  if (type === "W") return rect;
  if (type === "R")
    return <g>{rect}<rect x={x} y={y} width={size} height={size} fill={RED}/>
           <rect x={x} y={y} width={size} height={size}
                 fill="none" stroke={STROKE} strokeWidth="1.2"/></g>;
  // Las cuatro diagonales (mitad roja, mitad blanca)
  let points = null;
  if (type === "TL") points = `${x},${y} ${x2},${y} ${x},${y2}`;
  if (type === "TR") points = `${x},${y} ${x2},${y} ${x2},${y2}`;
  if (type === "BR") points = `${x2},${y} ${x2},${y2} ${x},${y2}`;
  if (type === "BL") points = `${x},${y} ${x2},${y2} ${x},${y2}`;
  return (
    <g>
      {rect}
      {points && <polygon points={points} fill={RED}/>}
      <rect x={x} y={y} width={size} height={size}
            fill="none" stroke={STROKE} strokeWidth="1.2"/>
    </g>
  );
}

/* ─── Grid genérico (cols × rows) ───────────────────────────────────── */
function Grid({ layout, size = 56 }) {
  const rows = layout.length;
  const cols = layout[0].length;
  const pad = 6;
  const w = cols * size + pad * 2;
  const h = rows * size + pad * 2;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-full"
         style={{ maxHeight: 180 }}>
      <rect x="0" y="0" width={w} height={h} fill="#F8FAFC" rx="6"/>
      {layout.map((row, r) =>
        row.map((face, c) => (
          <Face key={`${r}-${c}`} x={pad + c * size} y={pad + r * size}
                size={size} type={face} />
        ))
      )}
    </svg>
  );
}

/* ─── 14 diseños WISC-IV ────────────────────────────────────────────── */
/* Progresión de dificultad: 1×2 simple → 2×2 intermedio → 3×3 complejo */
const WISC_DESIGNS = {
  1:  [["R", "W"]],                                  // item 1 · 2 cubos
  2:  [["TR", "BL"]],                                 // item 2 · 2 cubos
  3:  [["TL", "BR"]],                                 // item 3 · 2 cubos
  4:  [["W", "R"], ["R", "W"]],                       // item 4 · 4 cubos
  5:  [["TR", "TL"], ["BR", "BL"]],                   // item 5 · rombo
  6:  [["R", "TL"], ["BR", "W"]],                     // item 6
  7:  [["TR", "R"], ["W", "BL"]],                     // item 7
  8:  [["TL", "TR"], ["BL", "BR"]],                   // item 8 · diamante
  9:  [["R", "W", "R"], ["W", "R", "W"], ["R", "W", "R"]], // item 9 · damero
 10:  [["TL", "TR", "TL"], ["BL", "R", "BR"], ["TL", "TR", "TL"]],
 11:  [["R", "TR", "W"], ["BR", "R", "TL"], ["W", "BL", "R"]],
 12:  [["TL", "R", "TR"], ["R", "W", "R"], ["BL", "R", "BR"]],
 13:  [["TR", "BR", "TL"], ["BL", "R", "TR"], ["BR", "TL", "BL"]],
 14:  [["W", "TR", "R"], ["BL", "TL", "BR"], ["R", "BR", "W"]],
};

/* ─── 14 diseños WAIS-III ───────────────────────────────────────────── */
/* WAIS empieza con ítems ligeramente distintos; reflejamos una
 * progresión análoga de 2 → 4 → 9 cubos con patrones no idénticos
 * a los de WISC para respetar la especificidad clínica. */
const WAIS_DESIGNS = {
  1:  [["TL", "BR"]],
  2:  [["TR", "BL"]],
  3:  [["W", "R"], ["R", "W"]],
  4:  [["R", "TR"], ["BL", "W"]],
  5:  [["TL", "TR"], ["BL", "BR"]],
  6:  [["TR", "TL"], ["BR", "BL"]],
  7:  [["R", "W"], ["TR", "BL"]],
  8:  [["R", "TL", "W"], ["TR", "R", "BL"], ["W", "BR", "R"]],
  9:  [["TL", "TR", "TL"], ["TR", "R", "TL"], ["BL", "BR", "BL"]],
 10:  [["W", "R", "W"], ["R", "W", "R"], ["W", "R", "W"]],
 11:  [["TL", "R", "TR"], ["R", "W", "R"], ["BL", "R", "BR"]],
 12:  [["TR", "TL", "TR"], ["BR", "R", "BL"], ["TR", "TL", "TR"]],
 13:  [["R", "TR", "BL"], ["BR", "W", "TL"], ["TR", "BL", "R"]],
 14:  [["TL", "TR", "R"], ["BR", "R", "TL"], ["R", "BL", "TR"]],
};

/* ─── Componente público ────────────────────────────────────────────── */
export function CubosPattern({ itemNum, test = "wisc", size = 56 }) {
  const dict = test === "wais" ? WAIS_DESIGNS : WISC_DESIGNS;
  const layout = dict[itemNum];
  if (!layout) return null;
  return <Grid layout={layout} size={size} />;
}

/* Poster: panel de referencia con los 14 diseños en grilla 7×2.
 * Se usa como NativeStimuli (fallback visual del test completo). */
export function CubosPoster({ test = "wisc" }) {
  const _dict = test === "wais" ? WAIS_DESIGNS : WISC_DESIGNS;
  const nums = Array.from({ length: 14 }, (_, i) => i + 1);
  return (
    <div className="grid grid-cols-7 gap-2 p-2">
      {nums.map(n => (
        <div key={n} className="flex flex-col items-center gap-1">
          <div className="w-full aspect-square rounded border border-slate-200 bg-white overflow-hidden">
            <CubosPattern itemNum={n} test={test} size={24} />
          </div>
          <span className="text-[9px] font-mono font-bold text-slate-400">{n}</span>
        </div>
      ))}
    </div>
  );
}

export default CubosPattern;
