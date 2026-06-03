/* ═══════════════════════════════════════════════════════════════════════
 * PatronFCRO.jsx — Figura Compleja de Rey-Osterrieth (SVG nativo)
 * ───────────────────────────────────────────────────────────────────────
 * Renderización geométrica de la FCRO con los 18 elementos del sistema
 * de calificación de Osterrieth/Taylor. La figura es una reconstrucción
 * abstracta basada en primitivas geométricas públicas (rectángulos,
 * cruces, triángulos) — NO reproduce los trazos exactos del material
 * original con copyright, sino una versión geométricamente análoga
 * apta para referencia clínica y entrenamiento dentro de NeuroSoft.
 *
 * Numeración Taylor (18 elementos):
 *   1  Cruz exterior (superior izquierda)
 *   2  Rectángulo grande
 *   3  Cruz diagonal (X del rectángulo)
 *   4  Línea media horizontal
 *   5  Línea media vertical
 *   6  Pequeño rectángulo interno (cuadrante superior izquierdo)
 *   7  Segmento pequeño sobre el rectángulo
 *   8  Cuatro líneas paralelas (cuadrante superior izquierdo)
 *   9  Triángulo superior derecho (adosado arriba)
 *  10  Línea pequeña dentro del rectángulo (cuadrante sup-der)
 *  11  Círculo con 3 puntos
 *  12  Cinco líneas paralelas cruzando el rectángulo (inf-der)
 *  13  Triángulo sobre lado derecho del rectángulo
 *  14  Rombo junto al rectángulo (extremo del triángulo 13)
 *  15  Segmento horizontal dentro del triángulo 13
 *  16  Segmento horizontal dentro del rectángulo
 *  17  Cruz inferior derecha
 *  18  Cuadrado inferior izquierdo
 *
 * Props:
 *   scores      — { e0..e17: number } puntuaciones 0 / 0.5 / 1 / 2
 *   showNumbers — muestra etiquetas numéricas (útil al calificar)
 *   highlight   — índice del elemento a resaltar (hover en la lista)
 *   size        — "sm" | "md" — alto máximo del SVG
 * ═══════════════════════════════════════════════════════════════════════ */

import React from "react";

const STROKE = "#1E293B";        // gris-azulado oscuro (default)
const HL     = "#D97706";        // ámbar — elemento resaltado
const OK     = "#059669";        // verde — puntaje ≥ 1
const MID    = "#F59E0B";        // naranja — puntaje 0.5
const BAD    = "#DC2626";        // rojo — puntaje 0
const STROKE_BASE = 2.2;         // grosor por defecto (sube visibilidad)
const STROKE_HL   = 3.4;

function colorFor(v) {
  if (v === undefined || v === null || Number.isNaN(v)) return STROKE;
  if (v >= 1)     return OK;
  if (v === 0.5)  return MID;
  if (v === 0)    return BAD;
  return STROKE;
}

/* ─── Envoltorio que aplica color/grosor a cada elemento ─────────────── */
function El({ idx, scores, highlight, children }) {
  const v = scores ? parseFloat(scores[`e${idx}`]) : undefined;
  const isHL = highlight === idx;
  const stroke = isHL ? HL : colorFor(v);
  const w = isHL ? STROKE_HL : STROKE_BASE;
  return (
    <g stroke={stroke}
       strokeWidth={w}
       strokeLinecap="round"
       strokeLinejoin="round"
       fill="none"
       style={{ transition: "stroke 150ms, stroke-width 150ms" }}
       data-element={idx + 1}>
      {children}
      {/* §fcro-fix: los puntos del círculo (idx=10) necesitan fill explícito.
        * Antes usábamos fill="currentColor" que se renderizaba como negro o
        * desaparecía en dark mode. Ahora se inyecta por idx específico abajo. */}
    </g>
  );
}

/* Componente especial para el círculo + 3 puntos (idx=10) que sí necesita fill */
function CirculoTresPuntos({ idx, scores, highlight }) {
  const v = scores ? parseFloat(scores[`e${idx}`]) : undefined;
  const isHL = highlight === idx;
  const stroke = isHL ? HL : colorFor(v);
  const w = isHL ? STROKE_HL : STROKE_BASE;
  return (
    <g data-element={idx + 1}
       style={{ transition: "stroke 150ms, stroke-width 150ms, fill 150ms" }}>
      {/* §fcro-redraw-v2: círculo CENTRADO en el cuadrante sup-der del rectángulo
        * grande (entre línea media vertical x=295 y borde derecho x=435).
        * Centro = 365, justo entre la línea media y el borde. */}
      <circle cx="365" cy="125" r="22"
              stroke={stroke} strokeWidth={w} fill="none"/>
      <circle cx="358" cy="118" r="2.2" fill={stroke} stroke="none"/>
      <circle cx="372" cy="118" r="2.2" fill={stroke} stroke="none"/>
      <circle cx="365" cy="132" r="2.2" fill={stroke} stroke="none"/>
    </g>
  );
}

/* ─── Componente principal ──────────────────────────────────────────── */
/* §fcro-redraw (2026-05-18): rediseño completo basado en la figura de
 * referencia Osterrieth-Taylor. Cambios respecto a la versión anterior:
 *   - El rectángulo pequeño (elemento 6) está ADOSADO al lado izquierdo
 *     del rectángulo grande, sobre la línea media horizontal (no en el
 *     cuadrante superior-izquierdo flotante).
 *   - Las 4 líneas paralelas (elemento 8) van DENTRO del rectángulo 6.
 *   - El segmento 7 sale por arriba del rectángulo 6.
 *   - Las 5 líneas paralelas (elemento 12) son OBLICUAS (no verticales)
 *     en el cuadrante inferior derecho, como en la figura real.
 *   - La cruz inferior (elemento 17) está al centro-inferior del
 *     rectángulo, no abajo a la derecha.
 *   - El elemento 18 es una línea/tick inferior, no un cuadrado. */
export function FCROFigure({ scores = {}, showNumbers = true, highlight = -1, size = "md" }) {
  const fontSize = size === "sm" ? 9 : 11;
  return (
    <svg viewBox="0 0 560 320"
         className="w-full h-full"
         style={{ maxHeight: size === "sm" ? 180 : 360 }}
         xmlns="http://www.w3.org/2000/svg">
      <rect x="0" y="0" width="560" height="320" fill="#FFFFFF" rx="4"/>

      {/* 1 · Cruz exterior libre (superior izquierda, fuera del rectángulo) */}
      <El idx={0} scores={scores} highlight={highlight}>
        <line x1="55"  y1="80" x2="115" y2="80"/>
        <line x1="85"  y1="50" x2="85"  y2="110"/>
      </El>

      {/* 2 · Rectángulo grande (el marco principal) */}
      <El idx={1} scores={scores} highlight={highlight}>
        <rect x="155" y="80" width="280" height="160"/>
      </El>

      {/* 3 · Cruz diagonal (X completa dentro del rectángulo) */}
      <El idx={2} scores={scores} highlight={highlight}>
        <line x1="155" y1="80"  x2="435" y2="240"/>
        <line x1="435" y1="80"  x2="155" y2="240"/>
      </El>

      {/* 4 · Línea media horizontal */}
      <El idx={3} scores={scores} highlight={highlight}>
        <line x1="155" y1="160" x2="435" y2="160"/>
      </El>

      {/* 5 · Línea media vertical */}
      <El idx={4} scores={scores} highlight={highlight}>
        <line x1="295" y1="80"  x2="295" y2="240"/>
      </El>

      {/* 6 · Pequeño rectángulo adosado al lado IZQUIERDO del rectángulo grande,
            cruzando la línea media horizontal */}
      <El idx={5} scores={scores} highlight={highlight}>
        <rect x="110" y="130" width="45" height="60"/>
      </El>

      {/* 7 · Segmento que sobresale POR ARRIBA del rectángulo pequeño */}
      <El idx={6} scores={scores} highlight={highlight}>
        <line x1="132" y1="110" x2="132" y2="130"/>
      </El>

      {/* 8 · Cuatro líneas horizontales DENTRO del rectángulo pequeño */}
      <El idx={7} scores={scores} highlight={highlight}>
        <line x1="110" y1="142" x2="155" y2="142"/>
        <line x1="110" y1="154" x2="155" y2="154"/>
        <line x1="110" y1="166" x2="155" y2="166"/>
        <line x1="110" y1="178" x2="155" y2="178"/>
      </El>

      {/* 9 · Triángulo adosado sobre el borde superior, mitad derecha */}
      <El idx={8} scores={scores} highlight={highlight}>
        <polygon points="315,80 395,80 355,35"/>
      </El>

      {/* 10 · Línea pequeña horizontal dentro del cuadrante sup-der */}
      <El idx={9} scores={scores} highlight={highlight}>
        <line x1="305" y1="110" x2="345" y2="110"/>
      </El>

      {/* 11 · Círculo con 3 puntos (cuadrante sup-der) */}
      <CirculoTresPuntos idx={10} scores={scores} highlight={highlight}/>

      {/* 12 · Cinco líneas paralelas oblicuas en cuadrante inferior-derecho.
            §fcro-redraw-v2: pendiente CORREGIDA — van de abajo-izquierda a
            arriba-derecha (siguiendo la dirección de la diagonal principal
            del rectángulo, como en la figura Osterrieth-Taylor). */}
      <El idx={11} scores={scores} highlight={highlight}>
        <line x1="305" y1="170" x2="355" y2="240"/>
        <line x1="320" y1="170" x2="370" y2="240"/>
        <line x1="335" y1="170" x2="385" y2="240"/>
        <line x1="350" y1="170" x2="400" y2="240"/>
        <line x1="365" y1="170" x2="415" y2="240"/>
      </El>

      {/* 13 · Triángulo sobre lado derecho del rectángulo (apunta a la derecha) */}
      <El idx={12} scores={scores} highlight={highlight}>
        <polygon points="435,100 435,180 510,140"/>
      </El>

      {/* 14 · Rombo en el extremo derecho del triángulo 13 */}
      <El idx={13} scores={scores} highlight={highlight}>
        <polygon points="510,140 525,125 540,140 525,155"/>
      </El>

      {/* 15 · Segmento horizontal dentro del triángulo 13 */}
      <El idx={14} scores={scores} highlight={highlight}>
        <line x1="450" y1="140" x2="495" y2="140"/>
      </El>

      {/* 16 · Línea horizontal que sale POR LA IZQUIERDA del rectángulo,
            en el cuadrante inferior-izquierdo */}
      <El idx={15} scores={scores} highlight={highlight}>
        <line x1="155" y1="200" x2="270" y2="200"/>
      </El>

      {/* 17 · Cruz pequeña en la parte inferior-central del rectángulo */}
      <El idx={16} scores={scores} highlight={highlight}>
        <line x1="240" y1="220" x2="270" y2="220"/>
        <line x1="255" y1="210" x2="255" y2="230"/>
      </El>

      {/* 18 · Línea vertical recta que baja desde el vértice inferior-izquierdo
            del rectángulo grande hacia abajo-izquierda (como en la figura real,
            es un trazo simple sobresaliente, no un cuadrado ni un tick). */}
      <El idx={17} scores={scores} highlight={highlight}>
        <line x1="200" y1="240" x2="200" y2="290"/>
      </El>

      {/* Etiquetas numéricas — recolocadas para no superponerse con líneas */}
      {showNumbers && (
        <g fontFamily="ui-monospace, SFMono-Regular, monospace"
           fontSize={fontSize}
           fontWeight="700"
           fill="#475569"
           pointerEvents="none">
          <text x="55"  y="42">1</text>
          <text x="440" y="76">2</text>
          <text x="220" y="170">3</text>
          <text x="440" y="158">4</text>
          <text x="300" y="76">5</text>
          <text x="120" y="125">6</text>
          <text x="125" y="105">7</text>
          <text x="158" y="138">8</text>
          <text x="353" y="32">9</text>
          <text x="348" y="105">10</text>
          <text x="408" y="125">11</text>
          <text x="395" y="208">12</text>
          <text x="490" y="138">13</text>
          <text x="540" y="118">14</text>
          <text x="450" y="135">15</text>
          <text x="215" y="197">16</text>
          <text x="275" y="216">17</text>
          <text x="207" y="280">18</text>
        </g>
      )}
    </svg>
  );
}

export default FCROFigure;
