/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/GuideFormatter.jsx
 * ───────────────────────────────────────────────────────────────────────
 * Convierte los strings de INSTRUCCIONES (clinical.js) en contenido
 * estructurado y legible: listas, tablas de edades, tiempos resaltados.
 *
 * Los datos originales son texto plano del estilo:
 *   "Edad 6-7: inicio 1. Edad 8-9: inicio 3. Tiempos: 1-5=30s · 4-8=60s."
 *
 * Este componente los parsea y renderiza con bullets, badges y jerarquia.
 * ═══════════════════════════════════════════════════════════════════════ */

import React from "react";
import { I } from "../../ui/primitives.jsx";

/* ─── Parser de texto a bullets ─── */
function parseBullets(text) {
  if (!text) return [];
  // Dividir por punto seguido de espacio o mayuscula
  const parts = text.split(/\.\s+(?=[A-ZÁÉÍÓÚ0-9])/).filter(Boolean);
  if (parts.length <= 1) {
    // Intentar dividir por " · " o "; "
    const alt = text.split(/\s*·\s*/).filter(Boolean);
    if (alt.length > 1) return alt.map(p => p.trim());
    return [text.trim()];
  }
  return parts.map(p => p.trim().replace(/\.$/, ""));
}

/* ─── Parser de pares edad-inicio ─── */
function parseAgeStart(text) {
  const ages = [];
  const re = /(\d+-\d+)\s*(?:años?\s*)?:?\s*inicio\s*(?:ítem\s*)?(\d+)/gi;
  let m;
  while ((m = re.exec(text)) !== null) {
    ages.push({ range: m[1], item: m[2] });
  }
  return ages;
}

/* ─── Parser de tiempos ─── */
function parseTimes(text) {
  const times = [];
  const re = /(?:ítems?\s*)?(\d+(?:-\d+)?)\s*=\s*(\d+)\s*s/gi;
  let m;
  while ((m = re.exec(text)) !== null) {
    times.push({ items: m[1], seconds: m[2] });
  }
  return times;
}

/* ─── Extraer numero maximo ─── */
function parseMax(text) {
  const m = text.match(/[Mm]ax:?\s*(\d+)/);
  return m ? m[1] : null;
}

export default function GuideFormatter({ instructions }) {
  if (!instructions) return <p className="text-xs italic text-gray-400">Sin datos de administracion.</p>;

  const { mat, inst, disc, tip, puntaje } = instructions;

  return (
    <div className="space-y-4 text-xs leading-relaxed" style={{ color: "var(--ns-text)" }}>

      {/* ── MATERIALES ── */}
      {mat && (
        <div className="p-3 rounded-xl" style={{ background: "var(--ns-subtle)" }}>
          <div className="flex items-center gap-2 mb-2">
            <I name="inventory_2" className="text-base" style={{ color: "#0D9488" }} />
            <span className="font-extrabold uppercase tracking-wider text-[11px]" style={{ color: "#0D9488" }}>Materiales</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {parseBullets(mat).map((b, i) => (
              <span key={i} className="px-2 py-1 rounded-lg text-[11px]"
                style={{ background: "var(--ns-card)", border: "1px solid var(--ns-card-b)" }}>{b}</span>
            ))}
          </div>
        </div>
      )}

      {/* ── INSTRUCCIONES ── */}
      {inst && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <I name="play_circle" className="text-base" style={{ color: "#7c3aed" }} />
            <span className="font-extrabold uppercase tracking-wider text-[11px]" style={{ color: "#7c3aed" }}>Instrucciones</span>
          </div>
          <ul className="space-y-1.5">
            {parseBullets(inst).map((b, i) => (
              <li key={i} className="flex items-start gap-2 text-xs">
                <span className="mt-0.5 shrink-0 w-1 h-1 rounded-full" style={{ background: "#7c3aed" }} />
                <span>{b}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ── DISCONTINUACION ── */}
      {disc && (
        <div className="p-3 rounded-xl border-l-3" style={{ borderColor: "#ef4444", background: "rgba(239,68,68,0.04)" }}>
          <div className="flex items-center gap-2 mb-1">
            <I name="block" className="text-base" style={{ color: "#dc2626" }} />
            <span className="font-extrabold uppercase tracking-wider text-[11px]" style={{ color: "#dc2626" }}>Discontinuar</span>
          </div>
          <p className="text-xs font-semibold" style={{ color: "#991b1b" }}>{disc}</p>
        </div>
      )}

      {/* ── PUNTUACION ── */}
      {puntaje && (
        <div>
          <div className="flex items-center gap-2 mb-1">
            <I name="calculate" className="text-base" style={{ color: "#d97706" }} />
            <span className="font-extrabold uppercase tracking-wider text-[11px]" style={{ color: "#d97706" }}>Puntuacion</span>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            {parseBullets(puntaje).map((b, i) => (
              <span key={i} className="text-xs font-semibold">{b}</span>
            ))}
            {parseMax(puntaje) && (
              <span className="text-xs font-extrabold px-2 py-0.5 rounded-lg"
                style={{ background: "rgba(217,119,6,0.12)", color: "#92400e" }}>
                Max: {parseMax(puntaje)}
              </span>
            )}
          </div>
        </div>
      )}

      {/* ── TIPS CLINICOS ── */}
      {tip && (
        <div className="p-3 rounded-xl" style={{ background: "rgba(13,148,136,0.06)", border: "1px solid rgba(13,148,136,0.15)" }}>
          <div className="flex items-center gap-2 mb-2">
            <I name="lightbulb" className="text-base" style={{ color: "#0D9488" }} />
            <span className="font-extrabold uppercase tracking-wider text-[11px]" style={{ color: "#0D9488" }}>Tips Clinicos</span>
          </div>

          {/* Edades de inicio como tabla */}
          {(() => {
            const ages = parseAgeStart(tip);
            if (ages.length > 0) return (
              <div className="mb-2">
                <p className="text-[10px] font-bold uppercase mb-1" style={{ color: "#0D9488" }}>Edad de inicio</p>
                <div className="flex flex-wrap gap-1.5">
                  {ages.map((a, i) => (
                    <span key={i} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-semibold"
                      style={{ background: "var(--ns-card)", border: "1px solid var(--ns-card-b)" }}>
                      {a.range} años → ítem {a.item}
                    </span>
                  ))}
                </div>
              </div>
            );
            return null;
          })()}

          {/* Tiempos como mini tabla */}
          {(() => {
            const times = parseTimes(tip);
            if (times.length > 0) return (
              <div className="mb-2">
                <p className="text-[10px] font-bold uppercase mb-1" style={{ color: "#0D9488" }}>Tiempos por item</p>
                <div className="flex flex-wrap gap-1.5">
                  {times.map((t, i) => (
                    <span key={i} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-semibold"
                      style={{ background: "rgba(245,158,11,0.1)", color: "#92400e", border: "1px solid rgba(245,158,11,0.2)" }}>
                      Items {t.items}: {t.seconds}s
                    </span>
                  ))}
                </div>
              </div>
            );
            return null;
          })()}

          {/* Resto del tip como bullets */}
          {(() => {
            const ages = parseAgeStart(tip);
            const times = parseTimes(tip);
            // Filtrar partes del texto que ya se mostraron como tabla
            let remaining = tip;
            ages.forEach(a => { remaining = remaining.replace(new RegExp(`Edad\\s*${a.range}[^.]*\\.?`, 'i'), ""); });
            times.forEach(t => { remaining = remaining.replace(new RegExp(`[^.]*${t.items}\\s*=\\s*${t.seconds}\\s*s[^.]*\\.?`, 'i'), ""); });
            remaining = remaining.replace(/Tiempos?:[^.]*\.?/i, "").replace(/^\s*[·,]\s*/, "").trim();
            const bullets = parseBullets(remaining).filter(b => b.length > 3);
            if (bullets.length === 0) return null;
            return (
              <ul className="space-y-1 mt-2">
                {bullets.map((b, i) => (
                  <li key={i} className="flex items-start gap-2 text-[11px]">
                    <span className="mt-0.5 shrink-0 w-1 h-1 rounded-full" style={{ background: "#0D9488" }} />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
            );
          })()}
        </div>
      )}
    </div>
  );
}
