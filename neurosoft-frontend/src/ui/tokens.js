/* ═══════════════════════════════════════════════════════════════════════
 * src/ui/tokens.js — Design tokens v2 (paleta editorial + tipografía mixta)
 * ───────────────────────────────────────────────────────────────────────
 * Sistema visual NeuroSoft 2026 — más editorial, menos "card-saturado".
 *
 * Principios:
 *   - NAVY como protagonista (no TEAL). TEAL es acento minoritario.
 *   - Radii contenidos (4-14px) — bordes más serios, menos juguetones.
 *   - Tipografía mixta: Manrope (sans) para cuerpo + Lora (serif) para H1/H2.
 *   - Sombras menos prominentes, bordes 1px en lugar de 2px.
 *   - Espaciado más denso — feel "clínico profesional", no "app de bienestar".
 *
 * Cambios respecto a v1:
 *   - radiusSm 8→6, radiusMd 12→10, radiusLg 24→14, radiusXl 28→18
 *   - INK = nuevo color de texto principal (más oscuro que NAVY)
 *   - Nueva escala SHADOWS con focus en blue undertones (no negro puro)
 *   - PAPER = nuevo fondo de superficies (más cálido que blanco puro)
 * ═══════════════════════════════════════════════════════════════════════ */

/* ─── Paleta de marca ───────────────────────────────────────────────── */
export const CREAM      = "#FDFBF7";  // fondo cálido principal
export const PAPER      = "#FCFAF4";  // superficie de cards (más cálido que white)
export const TEAL       = "#0D9488";  // acento principal — usar con moderación
export const TEAL_LIGHT = "#67E8F9";
export const TEAL_DARK  = "#0F766E";
export const NAVY       = "#1E293B";  // texto principal en claro
export const INK        = "#0F172A";  // texto editorial (más oscuro)
export const STONE      = "#475569";  // texto secundario
export const ASH        = "#94A3B8";  // texto terciario / placeholders

/* ─── Tonalidades de acento (uso limitado, semántica) ──────────────── */
export const ACCENTS = {
  amber:  "#B45309",   // pálidos cálidos (no naranja saturado)
  ruby:   "#9F1239",   // alerta seria (no rojo brillante)
  forest: "#15803D",   // afirmación seria (no verde saturado)
  plum:   "#6D28D9",   // psicoterapia (color del módulo clínico)
  ocean:  "#0369A1",   // referencias / citas
};

/* ─── Colores semánticos (clínicos) ────────────────────────────────── */
export const COLORS = {
  brand: TEAL,
  brandLight: TEAL_LIGHT,
  brandDeep: NAVY,
  cream: CREAM,
  paper: PAPER,
  success: ACCENTS.forest,
  warning: ACCENTS.amber,
  danger:  ACCENTS.ruby,
  info:    ACCENTS.ocean,
  /* Niveles de interpretación clínica */
  superior:    TEAL,
  promedio:    ACCENTS.forest,
  limitrofe:   ACCENTS.amber,
  bajo:        "#B45309",
  deficitario: ACCENTS.ruby,
};

/* ─── Geometría — radii contenidos ─────────────────────────────────── */
export const SIZES = {
  sidebar:  288,
  topbar:   80,
  /* Radii v2: más conservadores. Una Card grande ya no es ovalada. */
  radiusXs: 4,
  radiusSm: 6,
  radiusMd: 10,
  radiusLg: 14,
  radiusXl: 18,
  radiusFull: 9999,
};

/* ─── Sombras — undertones azulados ───────────────────────────────── */
export const SHADOWS = {
  // Más sutiles que el default Tailwind. Tono azul-gris en lugar de negro puro.
  xs: "0 1px 2px rgba(30, 41, 59, 0.04)",
  sm: "0 1px 3px rgba(30, 41, 59, 0.06), 0 1px 2px rgba(30, 41, 59, 0.04)",
  md: "0 4px 8px -2px rgba(30, 41, 59, 0.08), 0 2px 4px -2px rgba(30, 41, 59, 0.04)",
  lg: "0 10px 20px -6px rgba(30, 41, 59, 0.10), 0 4px 8px -4px rgba(30, 41, 59, 0.06)",
  xl: "0 20px 40px -12px rgba(30, 41, 59, 0.14)",
  // Sombra de "card editorial" — muy sutil, casi imperceptible
  editorial: "0 1px 0 rgba(30, 41, 59, 0.03), 0 1px 3px rgba(30, 41, 59, 0.04)",
  // Focus ring
  focus: "0 0 0 3px rgba(13, 148, 136, 0.18)",
};

/* ─── Tipografía ──────────────────────────────────────────────────── */
export const TYPOGRAPHY = {
  fontSans:    `'Manrope', ui-sans-serif, system-ui, -apple-system, sans-serif`,
  fontSerif:   `'Lora', 'Georgia', 'Times New Roman', serif`,  // para títulos H1/H2 en informes
  fontMono:    `'JetBrains Mono', 'SF Mono', ui-monospace, monospace`,
  /* Escala tipográfica (tighter que default) */
  scale: {
    h1:      { size: 28, lineHeight: 36, weight: 700, letter: -0.02 },
    h2:      { size: 22, lineHeight: 30, weight: 700, letter: -0.015 },
    h3:      { size: 17, lineHeight: 24, weight: 600, letter: -0.01 },
    h4:      { size: 14, lineHeight: 20, weight: 700, letter: 0 },
    body:    { size: 14, lineHeight: 22, weight: 400, letter: 0 },
    bodySm:  { size: 12, lineHeight: 18, weight: 400, letter: 0 },
    label:   { size: 10, lineHeight: 14, weight: 700, letter: 0.08 },   // UPPERCASE con tracking
    micro:   { size: 9,  lineHeight: 12, weight: 700, letter: 0.10 },   // datos/etiquetas
  },
};

/* ─── Espaciado canónico ──────────────────────────────────────────── */
export const SPACING = {
  card:    { sm: 16, md: 20, lg: 28 },   // padding de Cards
  section: { sm: 16, md: 24, lg: 40 },   // separación entre secciones
  gap:     { xs: 4, sm: 8, md: 12, lg: 16, xl: 24 },
};
