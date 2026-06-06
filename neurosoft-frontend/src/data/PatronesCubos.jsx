/* ═══════════════════════════════════════════════════════════════════════
 * PatronesCubos.jsx — Estímulos SVG para Diseño con Cubos (Kohs)
 * ───────────────────────────────────────────────────────────────────────
 * ⚠️  AVISO IMPORTANTE — NATURALEZA DE ESTOS ESTÍMULOS
 *
 * Estos 14 diseños son recreaciones ESQUEMÁTICAS (no idénticas) de los
 * patrones de la prueba original con copyright activo (WISC-IV y
 * WAIS-III, Pearson Education). Se incluyen como referencia visual
 * de progresión de dificultad 1×1 → 2×2 → 3×3 dentro de la app, NO
 * para sustituir el material físico original.
 *
 * Para aplicación clínica real de Diseño con Cubos use el kit oficial
 * de cubos de la prueba (4 cubos para WISC-IV ítems 1-4 y 9 cubos
 * para ítems 5-14). NeuroSoft no distribuye ni distribuye el material
 * copyrighted; estos SVGs son útiles para:
 *   - Mostrar al clínico cómo se ve cada ítem al recordar la prueba
 *   - Entrenamiento y familiarización con la prueba
 *   - Documentación visual al margen de los protocolos propios
 *
 * Vocabulario de caras (como en los cubos de Kohs):
 *   W   = cara totalmente blanca
 *   R   = cara totalmente roja
 *   TL  = triángulo rojo en esquina superior-izquierda (diagonal ↘)
 *   TR  = triángulo rojo en esquina superior-derecha (diagonal ↙)
 *   BL  = triángulo rojo en esquina inferior-izquierda (diagonal ↗)
 *   BR  = triángulo rojo en esquina inferior-derecha (diagonal ↖)
 *
 * §cubos-2026-06-05: añadidos disclaimers en CubosPattern y CubosPoster
 *   para que el clínico NO confunda los SVGs esquemáticos con el
 *   material original. Riesgo clínico-médico-legal documentado en
 *   `docs/AUDITORIA_PDFs.md` (sub-sección V2).
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
  const rect = (
    <rect x={x} y={y} width={size} height={size}
          fill={WHITE} stroke={STROKE} strokeWidth="1.2" />
  );
  if (type === "W") return rect;
  if (type === "R")
    return <g>{rect}<rect x={x} y={y} width={size} height={size} fill={RED}/>
           <rect x={x} y={y} width={size} height={size}
                 fill="none" stroke={STROKE} strokeWidth="1.2"/></g>;
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

/* ─── 14 diseños WISC-IV (progresión esquemática) ───────────────────── */
/* Items 1-2: 1×2 (2 cubos). Items 3-4: 2×2 (4 cubos). Items 5-14: 3×3
 * con cubos sólidos. La progresión 1×2 → 4 → 9 respeta la estructura
 * de dificultad del WISC-IV; los patrones exactos son aproximaciones. */
const WISC_DESIGNS = {
  1:  [["R", "W"]],
  2:  [["TR", "BL"]],
  3:  [["TL", "BR"]],
  4:  [["W", "R"], ["R", "W"]],
  5:  [["TR", "TL"], ["BR", "BL"]],
  6:  [["R", "TL"], ["BR", "W"]],
  7:  [["TR", "R"], ["W", "BL"]],
  8:  [["TL", "TR"], ["BL", "BR"]],
  9:  [["R", "W", "R"], ["W", "R", "W"], ["R", "W", "R"]],
 10:  [["TL", "TR", "TL"], ["BL", "R", "BR"], ["TL", "TR", "TL"]],
 11:  [["R", "TR", "W"], ["BR", "R", "TL"], ["W", "BL", "R"]],
 12:  [["TL", "R", "TR"], ["R", "W", "R"], ["BL", "R", "BR"]],
 13:  [["TR", "BR", "TL"], ["BL", "R", "TR"], ["BR", "TL", "BL"]],
 14:  [["W", "TR", "R"], ["BL", "TL", "BR"], ["R", "BR", "W"]],
};

/* ─── 14 diseños WAIS-III (progresión esquemática) ──────────────────── */
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
export function CubosPattern({ itemNum, test = "wisc", size = 56, showDisclaimer = false }) {
  const dict = test === "wais" ? WAIS_DESIGNS : WISC_DESIGNS;
  const layout = dict[itemNum];
  if (!layout) return null;
  return (
    <div className="flex flex-col gap-1">
      {showDisclaimer && (
        <div className="text-[9px] text-amber-700 bg-amber-50 border border-amber-200 rounded px-1.5 py-0.5 leading-tight">
          Esquemático — use el kit oficial para aplicación clínica
        </div>
      )}
      <Grid layout={layout} size={size} />
    </div>
  );
}

/* Poster: panel de referencia con los 14 diseños en grilla 7×2. */
export function CubosPoster({ test = "wisc" }) {
  const nums = Array.from({ length: 14 }, (_, i) => i + 1);
  return (
    <div className="flex flex-col gap-2">
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
    </div>
  );
}

export default CubosPattern;
