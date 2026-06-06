/* ═══════════════════════════════════════════════════════════════════════
 * src/app/therapy/EnfoqueDetalle.jsx
 * ───────────────────────────────────────────────────────────────────────
 * Panel académico extendido de un enfoque terapéutico.
 * Se abre cuando el clínico hace click en una terapia del catálogo.
 *
 * Tabs:
 *   1. Resumen         — descripción extendida, evidencia, indicaciones
 *   2. Cómo se aplica  — fases paso a paso
 *   3. Técnicas        — cada técnica con diálogo y plantilla
 *   4. Videos          — embebidos YouTube formativos
 *   5. Bibliografía    — libros, papers DOI, guías
 *   6. Casos prácticos — vignettes anonimizadas
 *   7. Recursos        — PDFs descargables, audios
 *
 * Para enfoques que NO tienen contenido extendido aún, los tabs
 * muestran mensaje "contenido en preparación" — siguen siendo navegables.
 *
 * Ver enfoquesTerapeuticos.js para schema completo de campos extendidos.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState, useMemo } from "react";
import { I } from "../../ui/primitives.jsx";
import { ACCENTS } from "../../ui/tokens.js";
import { NIVELES_EVIDENCIA } from "../../data/enfoquesTerapeuticos.js";

const PLUM = ACCENTS.plum;

const TABS = [
  { id: "resumen",        label: "Resumen",         icon: "menu_book" },
  { id: "aplicacion",     label: "Cómo se aplica",  icon: "checklist" },
  { id: "tecnicas",       label: "Técnicas",        icon: "psychology" },
  { id: "videos",         label: "Videos",          icon: "play_circle" },
  { id: "bibliografia",   label: "Bibliografía",    icon: "library_books" },
  { id: "casos",          label: "Casos prácticos", icon: "person_pin" },
  { id: "recursos",       label: "Recursos",        icon: "folder_zip" },
];

export default function EnfoqueDetalle({ enfoque, onClose }) {
  const [tab, setTab] = useState("resumen");
  /* Indicador si tiene contenido educativo extendido (hook al tope para regla-of-hooks) */
  const hasExtended = useMemo(() => ({
    aplicacion: !!enfoque?.fases_aplicacion?.length,
    tecnicas: !!enfoque?.tecnicas_detalladas?.length,
    videos: !!enfoque?.videos?.length,
    bibliografia: !!enfoque?.bibliografia?.length,
    casos: !!enfoque?.casos_practicos?.length,
    recursos: !!enfoque?.recursos_descargables?.length,
  }), [enfoque]);

  if (!enfoque) return null;

  const evColor = enfoque.evidencia === "A" ? "#166534"
                : enfoque.evidencia === "B" ? "#92400E"
                : enfoque.evidencia === "C" ? "#9333EA"
                : "var(--ns-muted)";
  const evBg = enfoque.evidencia === "A" ? "rgba(21,128,61,0.10)"
              : enfoque.evidencia === "B" ? "rgba(180,83,9,0.10)"
              : enfoque.evidencia === "C" ? "rgba(147,51,234,0.10)"
              : "var(--ns-subtle)";

  return (
    <div
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      className="fixed inset-0 z-[60] flex items-center justify-center p-4"
      style={{ background: "rgba(15,23,42,0.65)", backdropFilter: "blur(3px)" }}
    >
      <div
        className="w-full max-w-5xl max-h-[92vh] rounded-lg shadow-2xl flex flex-col overflow-hidden"
        style={{ background: "var(--ns-card)" }}
      >
        {/* ─── Header ─── */}
        <div className="p-5 border-b flex items-start gap-4" style={{ borderColor: "var(--ns-card-b)" }}>
          <div className="flex-1 min-w-0">
            <p className="ns-eyebrow mb-1" style={{ color: PLUM }}>Enfoque terapéutico</p>
            <h2 className="ns-serif text-2xl font-bold leading-tight">{enfoque.nombre}</h2>
            <div className="flex items-center gap-3 mt-2 flex-wrap">
              {enfoque.sigla && (
                <span className="text-xs ns-mono font-bold px-2 py-0.5 rounded" style={{ background: `${PLUM}15`, color: PLUM }}>
                  {enfoque.sigla}
                </span>
              )}
              <span className="text-xs font-bold px-2 py-0.5 rounded" style={{ background: evBg, color: evColor }}
                title={NIVELES_EVIDENCIA[enfoque.evidencia]}>
                Evidencia {enfoque.evidencia}
              </span>
              <span className="text-xs uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
                {enfoque.categoria.replace(/_/g, " ")} · {enfoque.duracion_tipica}
              </span>
            </div>
          </div>
          <button onClick={onClose} aria-label="Cerrar" title="Cerrar (Esc)"
            className="p-2 rounded-md transition-all hover:opacity-80" style={{ color: "var(--ns-muted)" }}>
            <I name="close" />
          </button>
        </div>

        {/* ─── Tabs ─── */}
        <div className="border-b flex overflow-x-auto" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
          {TABS.filter(t => t.id === "resumen" || hasExtended[t.id]).map(t => {
            const isActive = tab === t.id;
            const isMissing = false;
            return (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className="px-4 py-3 text-xs font-bold uppercase tracking-wider whitespace-nowrap flex items-center gap-1.5 transition-all border-b-2"
                style={{
                  color: isActive ? PLUM : isMissing ? "var(--ns-muted)" : "var(--ns-text)",
                  borderColor: isActive ? PLUM : "transparent",
                  background: isActive ? "var(--ns-card)" : "transparent",
                  opacity: isMissing ? 0.55 : 1,
                }}
              >
                <I name={t.icon} className="text-base" />
                {t.label}
                {isMissing && <span className="text-[9px] ml-1">∅</span>}
              </button>
            );
          })}
        </div>

        {/* ─── Contenido ─── */}
        <div className="flex-1 overflow-auto p-6">
          {tab === "resumen"      && <TabResumen      enfoque={enfoque} />}
          {tab === "aplicacion"   && <TabAplicacion   enfoque={enfoque} />}
          {tab === "tecnicas"     && <TabTecnicas     enfoque={enfoque} />}
          {tab === "videos"       && <TabVideos       enfoque={enfoque} />}
          {tab === "bibliografia" && <TabBibliografia enfoque={enfoque} />}
          {tab === "casos"        && <TabCasos        enfoque={enfoque} />}
          {tab === "recursos"     && <TabRecursos     enfoque={enfoque} />}
        </div>

        {/* ─── Footer ─── */}
        <div className="border-t p-3 text-center" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
          <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
            Contenido educativo seleccionado · Última revisión {enfoque.ultima_revision || "mayo 2026"}
          </p>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════
 * Tabs individuales
 * ═══════════════════════════════════════════════════════════════════════ */

function TabResumen({ enfoque }) {
  return (
    <div className="space-y-6 max-w-3xl">
      {enfoque.descripcion_extendida ? (
        <Section title="Descripción">
          <p className="ns-serif leading-relaxed text-[15px]" style={{ color: "var(--ns-text)" }}>
            {enfoque.descripcion_extendida}
          </p>
        </Section>
      ) : enfoque.notas ? (
        <Section title="Descripción">
          <p className="ns-serif-italic leading-relaxed" style={{ color: "var(--ns-text)" }}>{enfoque.notas}</p>
        </Section>
      ) : null}

      <div className="grid sm:grid-cols-2 gap-6">
        <Section title="Indicado para" iconColor="#166534">
          <BulletList items={enfoque.indicaciones} />
        </Section>
        <Section title="NO indicado / contraindicaciones" iconColor="#9F1239">
          <BulletList items={enfoque.no_indicado} />
        </Section>
      </div>

      {enfoque.efecto_tamano && Object.keys(enfoque.efecto_tamano).length > 0 && (
        <Section title="Tamaños del efecto (Cohen d / Hedges g)">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {Object.entries(enfoque.efecto_tamano).map(([condicion, d]) => (
              <div key={condicion} className="p-3 rounded border text-center" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
                <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: "var(--ns-muted)" }}>{condicion.replace(/_/g, " ")}</p>
                <p className="ns-mono text-2xl font-bold" style={{ color: PLUM }}>d = {d}</p>
              </div>
            ))}
          </div>
          <p className="text-[10px] mt-2" style={{ color: "var(--ns-muted)" }}>
            d ≥ 0.8 = efecto grande · 0.5-0.8 = mediano · 0.2-0.5 = pequeño (Cohen 1988)
          </p>
        </Section>
      )}

      <div className="grid sm:grid-cols-2 gap-6">
        <Section title="Estructura típica">
          <BulletList items={enfoque.estructura} />
        </Section>
        <Section title="Técnicas clave">
          <BulletList items={enfoque.tecnicas_clave} />
        </Section>
      </div>

      {enfoque.outcome_recomendadas?.length > 0 && (
        <Section title="Escalas de outcome recomendadas (pre/post)">
          <div className="flex flex-wrap gap-2">
            {enfoque.outcome_recomendadas.map(o => (
              <span key={o} className="text-xs ns-mono px-2 py-1 rounded border" style={{ borderColor: "var(--ns-card-b)", color: "var(--ns-text)" }}>
                {o}
              </span>
            ))}
          </div>
        </Section>
      )}
    </div>
  );
}

function TabAplicacion({ enfoque }) {
  if (!enfoque.fases_aplicacion?.length) {
    return <EmptyState
      titulo="Guía de aplicación en preparación"
      mensaje="Esta sección documentará paso a paso cómo se estructura el tratamiento, qué hacer en cada fase, y qué escalas aplicar en cada etapa."
    />;
  }
  return (
    <div className="space-y-5 max-w-3xl">
      <p className="ns-serif-italic text-sm" style={{ color: "var(--ns-muted)" }}>
        Guía de aplicación clínica fase por fase. Tiempos y objetivos típicos basados en manuales de referencia.
      </p>
      {enfoque.fases_aplicacion.map((f, i) => (
        <div key={i} className="rounded border p-4" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }}>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 rounded-full flex items-center justify-center font-extrabold text-sm"
              style={{ background: PLUM, color: "white" }}>
              {f.fase}
            </div>
            <div className="flex-1">
              <h4 className="font-bold ns-serif text-lg">{f.nombre}</h4>
              {f.duracion_sesiones && (
                <p className="text-[11px] uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
                  ≈ {f.duracion_sesiones} sesiones
                </p>
              )}
            </div>
          </div>

          {f.objetivos?.length > 0 && (
            <div className="mb-3">
              <p className="ns-eyebrow mb-1">Objetivos</p>
              <BulletList items={f.objetivos} />
            </div>
          )}

          <div className="grid sm:grid-cols-2 gap-4">
            {f.tareas_clinico?.length > 0 && (
              <div>
                <p className="ns-eyebrow mb-1">Qué hace el clínico</p>
                <BulletList items={f.tareas_clinico} />
              </div>
            )}
            {f.tareas_paciente?.length > 0 && (
              <div>
                <p className="ns-eyebrow mb-1">Tareas para el paciente</p>
                <BulletList items={f.tareas_paciente} />
              </div>
            )}
          </div>

          {f.criterios_avance && (
            <div className="mt-3 pt-3 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
              <p className="ns-eyebrow mb-1">Criterios para pasar a la siguiente fase</p>
              <p className="text-sm" style={{ color: "var(--ns-text)" }}>{f.criterios_avance}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function TabTecnicas({ enfoque }) {
  if (!enfoque.tecnicas_detalladas?.length) {
    return <EmptyState
      titulo="Técnicas detalladas en preparación"
      mensaje="Esta sección incluirá cada técnica con su descripción, ejemplos de diálogo terapeuta-paciente, ejercicios para casa y plantillas descargables."
      hint={enfoque.tecnicas_clave?.length > 0 ? `Mientras tanto, técnicas clave del enfoque: ${enfoque.tecnicas_clave.slice(0, 3).join(", ")}…` : null}
    />;
  }
  return (
    <div className="space-y-4 max-w-3xl">
      {enfoque.tecnicas_detalladas.map((t, i) => (
        <details key={i} className="rounded border p-4" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }} open={i === 0}>
          <summary className="font-bold ns-serif text-base cursor-pointer flex items-center gap-2" style={{ color: "var(--ns-text)" }}>
            <I name="psychology" className="text-base" style={{ color: PLUM }} />
            {t.nombre}
          </summary>
          <div className="pt-3 pl-7 space-y-3 text-sm">
            <p style={{ color: "var(--ns-text)" }}>{t.descripcion}</p>
            {t.cuando_usar && (
              <div>
                <p className="ns-eyebrow mb-0.5">Cuándo usar</p>
                <p style={{ color: "var(--ns-muted)" }}>{t.cuando_usar}</p>
              </div>
            )}
            {t.ejemplo_dialogo && (
              <div className="p-3 rounded" style={{ background: "var(--ns-subtle)" }}>
                <p className="ns-eyebrow mb-1">Ejemplo de diálogo</p>
                <p className="ns-serif-italic text-[13px] whitespace-pre-line" style={{ color: "var(--ns-text)" }}>
                  {t.ejemplo_dialogo}
                </p>
              </div>
            )}
            {t.ejercicio_casa && (
              <div>
                <p className="ns-eyebrow mb-0.5">Ejercicio para casa</p>
                <p style={{ color: "var(--ns-muted)" }}>{t.ejercicio_casa}</p>
              </div>
            )}
            {t.plantilla_pdf && (
              <a href={t.plantilla_pdf} target="_blank" rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-xs font-bold"
                style={{ color: PLUM }}>
                <I name="download" className="text-sm" /> Descargar plantilla PDF
              </a>
            )}
          </div>
        </details>
      ))}
    </div>
  );
}

function youtubeVideoId(url) {
  const m = (url || "").match(/(?:embed\/|v=|youtu\.be\/)([A-Za-z0-9_-]{11})/);
  return m ? m[1] : null;
}

function youtubeEmbedUrl(url) {
  const id = youtubeVideoId(url);
  return id ? `https://www.youtube-nocookie.com/embed/${id}?rel=0&modestbranding=1` : url;
}

function TabVideos({ enfoque }) {
  if (!enfoque.videos?.length) {
    return <EmptyState
      titulo="Videos formativos en preparación"
      mensaje="Aquí encontrarás videos seleccionados de profesores reconocidos del enfoque (autores, institutos, conferencias). Solo material con permisos públicos de YouTube."
    />;
  }
  return (
    <div className="space-y-5 max-w-3xl">
      <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
        Videos formativos seleccionados. Reproducidos directamente desde YouTube — no se almacenan en NeuroSoft.
      </p>
      {enfoque.videos.map((v, i) => (
        <div key={i} className="rounded border overflow-hidden" style={{ borderColor: "var(--ns-card-b)" }}>
          <div className="aspect-video bg-black">
            <iframe
              src={youtubeEmbedUrl(v.url_youtube)}
              title={v.titulo}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerPolicy="strict-origin-when-cross-origin"
              allowFullScreen
              style={{ width: "100%", height: "100%", border: "none" }}
            />
          </div>
          <div className="p-3">
            <h4 className="font-bold text-sm">{v.titulo}</h4>
            <p className="text-xs mt-1" style={{ color: "var(--ns-muted)" }}>
              {[v.autor, v.duracion, v.idioma === "en" ? "Inglés" : v.idioma === "es" ? "Español" : v.idioma].filter(Boolean).join(" · ")}
            </p>
            {v.descripcion && (
              <p className="text-xs mt-1.5" style={{ color: "var(--ns-text)" }}>{v.descripcion}</p>
            )}
            {youtubeVideoId(v.url_youtube) && (
              <a href={`https://www.youtube.com/watch?v=${youtubeVideoId(v.url_youtube)}`} target="_blank" rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-[11px] font-bold mt-2 hover:underline" style={{ color: PLUM }}>
                <I name="open_in_new" className="text-sm" />Abrir en YouTube si no reproduce aquí
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function TabBibliografia({ enfoque }) {
  const items = enfoque.bibliografia?.length ? enfoque.bibliografia
              : enfoque.referencias?.map(r => ({ tipo: "ref", titulo: r }));
  if (!items?.length) {
    return <EmptyState titulo="Bibliografía en preparación" mensaje="Se documentarán libros fundacionales, papers seminales con DOI y guías clínicas (NICE/APA/Cochrane)." />;
  }
  return (
    <div className="space-y-3 max-w-3xl">
      {items.map((b, i) => {
        if (b.tipo === "ref" || !b.tipo) {
          return (
            <div key={i} className="text-sm ns-serif-italic pl-3 border-l-2" style={{ color: "var(--ns-text)", borderColor: PLUM }}>
              {b.titulo}
            </div>
          );
        }
        return (
          <div key={i} className="rounded border p-3 flex items-start gap-3" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }}>
            <I name={
              b.tipo === "libro" ? "menu_book"
              : b.tipo === "paper" ? "article"
              : b.tipo === "guia" ? "rule"
              : b.tipo === "capitulo" ? "auto_stories"
              : "library_books"
            } className="text-xl mt-0.5" style={{ color: PLUM }} />
            <div className="flex-1 min-w-0">
              <p className="font-bold text-sm">{b.titulo}</p>
              <p className="text-xs mt-0.5" style={{ color: "var(--ns-muted)" }}>
                {[b.autor || b.autores, b.editorial, b.edicion && `${b.edicion}ª ed.`, b.anio].filter(Boolean).join(" · ")}
              </p>
              <div className="flex gap-3 mt-1">
                {b.isbn && <span className="text-[10px] ns-mono" style={{ color: "var(--ns-muted)" }}>ISBN {b.isbn}</span>}
                {b.doi && (
                  <a href={`https://doi.org/${b.doi}`} target="_blank" rel="noreferrer"
                    className="text-[10px] ns-mono" style={{ color: PLUM }}>
                    DOI {b.doi}
                  </a>
                )}
                {b.url && (
                  <a href={b.url} target="_blank" rel="noreferrer"
                    className="text-[10px] ns-mono" style={{ color: PLUM }}>
                    Enlace
                  </a>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function TabCasos({ enfoque }) {
  if (!enfoque.casos_practicos?.length) {
    return <EmptyState titulo="Casos prácticos en preparación" mensaje="Se incluirán vignettes clínicas anonimizadas con motivo de consulta, hipótesis, plan aplicado y evolución." />;
  }
  return (
    <div className="space-y-5 max-w-3xl">
      {enfoque.casos_practicos.map((c, i) => (
        <div key={i} className="rounded border p-4" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }}>
          <p className="ns-eyebrow mb-1" style={{ color: PLUM }}>Caso {i + 1}</p>
          <h4 className="font-bold ns-serif text-lg mb-2">{c.titulo}</h4>

          {c.motivo_consulta && (
            <div className="mb-3">
              <p className="ns-eyebrow mb-1">Motivo de consulta</p>
              <p className="text-sm ns-serif-italic" style={{ color: "var(--ns-text)" }}>"{c.motivo_consulta}"</p>
            </div>
          )}
          {c.hipotesis && (
            <div className="mb-3">
              <p className="ns-eyebrow mb-1">Hipótesis clínica</p>
              <p className="text-sm" style={{ color: "var(--ns-text)" }}>{c.hipotesis}</p>
            </div>
          )}
          {c.plan_aplicado && (
            <div className="mb-3">
              <p className="ns-eyebrow mb-1">Plan aplicado</p>
              {Array.isArray(c.plan_aplicado)
                ? <BulletList items={c.plan_aplicado} />
                : <p className="text-sm" style={{ color: "var(--ns-text)" }}>{c.plan_aplicado}</p>}
            </div>
          )}
          {c.evolucion && (
            <div className="mb-3 p-3 rounded" style={{ background: "rgba(13,148,136,0.08)" }}>
              <p className="ns-eyebrow mb-1">Evolución</p>
              <p className="text-sm" style={{ color: "var(--ns-text)" }}>{c.evolucion}</p>
            </div>
          )}
          {c.reflexion && (
            <div className="border-t pt-3" style={{ borderColor: "var(--ns-card-b)" }}>
              <p className="ns-eyebrow mb-1">Reflexión clínica</p>
              <p className="text-sm ns-serif-italic" style={{ color: "var(--ns-muted)" }}>{c.reflexion}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function TabRecursos({ enfoque }) {
  if (!enfoque.recursos_descargables?.length) {
    return <EmptyState titulo="Recursos descargables en preparación" mensaje="Aquí encontrarás registros para paciente (registro de pensamientos, diario de emociones), worksheets, audios (mindfulness, defusión, relajación) y plantillas." />;
  }
  const grouped = enfoque.recursos_descargables.reduce((acc, r) => {
    const k = r.tipo || "otros";
    (acc[k] = acc[k] || []).push(r);
    return acc;
  }, {});
  const labels = {
    plantilla: "Plantillas",
    paciente: "Hojas para paciente",
    audio: "Audios",
    video: "Videos descargables",
    psicoeducacion: "Psicoeducación",
    otros: "Otros recursos",
  };
  const icons = {
    plantilla: "edit_note",
    paciente: "person",
    audio: "headphones",
    video: "videocam",
    psicoeducacion: "info",
    otros: "folder",
  };
  return (
    <div className="space-y-5 max-w-3xl">
      {Object.entries(grouped).map(([tipo, list]) => (
        <div key={tipo}>
          <h4 className="ns-eyebrow mb-2 flex items-center gap-2">
            <I name={icons[tipo] || "folder"} className="text-base" style={{ color: PLUM }} />
            {labels[tipo] || tipo}
          </h4>
          <div className="space-y-2">
            {list.map((r, i) => (
              <a key={i} href={r.url} target="_blank" rel="noreferrer"
                className="block p-3 rounded border hover:shadow-sm transition-all flex items-center justify-between"
                style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }}>
                <span className="text-sm font-medium" style={{ color: "var(--ns-text)" }}>{r.titulo}</span>
                <I name="download" style={{ color: PLUM }} />
              </a>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── Componentes auxiliares ─── */

function Section({ title, iconColor, children }) {
  return (
    <div>
      <p className="ns-eyebrow mb-2" style={{ color: iconColor || "var(--ns-muted)" }}>{title}</p>
      {children}
    </div>
  );
}

function BulletList({ items }) {
  if (!items?.length) return <p className="text-xs" style={{ color: "var(--ns-muted)" }}>—</p>;
  return (
    <ul className="space-y-1 text-sm leading-relaxed" style={{ color: "var(--ns-text)" }}>
      {items.map((it, i) => <li key={i}>· {it}</li>)}
    </ul>
  );
}

function EmptyState({ titulo, mensaje, hint }) {
  return (
    <div className="max-w-md mx-auto py-12 text-center">
      <I name="construction" className="text-5xl opacity-30 mb-3" style={{ color: PLUM }} />
      <h3 className="font-bold mb-2">{titulo}</h3>
      <p className="text-sm leading-relaxed" style={{ color: "var(--ns-muted)" }}>{mensaje}</p>
      {hint && (
        <p className="text-xs ns-serif-italic mt-4 pt-4 border-t inline-block max-w-xs" style={{ color: "var(--ns-muted)", borderColor: "var(--ns-card-b)" }}>
          {hint}
        </p>
      )}
    </div>
  );
}
