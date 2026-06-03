/* ═══════════════════════════════════════════════════════════════════════
 * src/app/aprender/PruebasDisponiblesPage.jsx
 * ───────────────────────────────────────────────────────────────────────
 * Catálogo navegable de TODAS las pruebas con baremos disponibles en
 * NeuroSoft. Lee del endpoint /api/v1/baremos/pruebas y permite:
 *   - Filtrar por población (infantil / adulto joven / adulto mayor)
 *   - Filtrar por fuente normativa (Neuronorma Colombia, ENI-2, WISC-IV, …)
 *   - Filtrar por tipo de cálculo (rango_puntaje, z_score, suma_a_indice…)
 *   - Buscar por nombre / id
 *
 * El objetivo: que el clínico responda en 5 segundos "¿NeuroSoft tiene
 * esta prueba con baremos colombianos?".
 *
 * Diseño: editorial coherente con BibliotecaPage — tablero limpio,
 * tipografía mixta serif/sans, chips por categoría, badge de población.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useMemo, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { I, TopBar } from "../../ui/primitives.jsx";
import { TEAL, NAVY, ACCENTS } from "../../ui/tokens.js";
import { useToast } from "../../contexts.jsx";

const PLUM = ACCENTS?.plum || "#6D28D9";

const POBLACION_META = {
  infantil:     { label: "Infantil",         c: "#6366f1", ic: "child_care",   rango: "5–16 años" },
  adulto_joven: { label: "Adulto joven",     c: TEAL,      ic: "person",       rango: "17–55 años" },
  adulto_mayor: { label: "Adulto mayor",     c: ACCENTS?.amber || "#B45309", ic: "elderly", rango: "50–90 años" },
};

const TIPO_CALCULO_META = {
  rango_puntaje:           { lb: "Escalar (PD → PE)",   hint: "Baremos por edad y bracket de meses (WISC, ENI-2, K-ABC)." },
  wais_range:              { lb: "Rango por edad",      hint: "Tablas por bandas de edad (WAIS-III + índices)." },
  desconocido:             { lb: "Neuronorma AM",       hint: "Tablas Neuronorma con ajuste por escolaridad." },
  z_score:                 { lb: "Puntaje Z",           hint: "Media y SD por edad — TMT, FCRO, BTA." },
  suma_a_indice:           { lb: "Suma → Índice (CI)",  hint: "Sumatoria de escalares al índice (CI compuesto)." },
  escolaridad_pc50:        { lb: "Punto de corte 50",   hint: "Tabla por edad + escolaridad (Dígitos, Denominación)." },
  puntaje_directo_a_t:     { lb: "Directo → Puntaje T", hint: "Conversión a escala T (media 50, sd 10)." },
  puntaje_doble_resultado: { lb: "PD → PE + Percentil", hint: "Devuelve dos valores (GADS, MoCA…)." },
  clasificacion_fija:      { lb: "Clasificación fija",  hint: "Categorías sin ajustes (Beck BDI-II, Yesavage)." },
  edad_sexo:               { lb: "Edad × Sexo",         hint: "Baremos diferenciados por sexo." },
};

const FUENTE_META = {
  neuronorma_colombia:  { lb: "Neuronorma Colombia",  c: ACCENTS?.amber || "#B45309", autores: "Peña-Casanova, Montañés et al.", anio: 2021 },
  arango_lasprilla_2015:{ lb: "Arango-Lasprilla LATAM", c: TEAL, autores: "Arango-Lasprilla, Rivera et al.", anio: 2015 },
  eni_2_colombia:       { lb: "ENI-2",                 c: "#6366f1", autores: "Matute, Rosselli, Ardila, Ostrosky", anio: 2013 },
  wisc_iv_pearson:      { lb: "WISC-IV (Pearson)",     c: NAVY, autores: "Wechsler (adapt. Pearson)", anio: 2003 },
  wais_iii_pearson:     { lb: "WAIS-III (Pearson)",    c: NAVY, autores: "Wechsler (adapt. Pearson)", anio: 1999 },
  moca_pedraza_colombia:{ lb: "MoCA-S Bogotá",         c: PLUM, autores: "Pedraza et al.", anio: 2016 },
  otro:                 { lb: "Otra fuente",           c: "#475569", autores: "—", anio: null },
};

export default function PruebasDisponiblesPage() {
  const toast = useToast();
  const [catalogo, setCatalogo] = useState(null);
  const [error, setError] = useState(null);
  const [fuentes, setFuentes] = useState([]);
  // Filtros
  const [poblacion, setPoblacion] = useState("");
  const [fuente, setFuente] = useState("");
  const [texto, setTexto] = useState("");
  // Detalle modal
  const [pruebaSel, setPruebaSel] = useState(null);

  useEffect(() => {
    Promise.all([
      api.get("/api/v1/baremos/pruebas"),
      api.get("/api/v1/baremos/sources").catch(() => []),
    ])
      .then(([cat, src]) => {
        setCatalogo(cat);
        setFuentes(src || []);
      })
      .catch(e => {
        const m = _parseError(e);
        setError(m);
        toast.error(m);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filtradas = useMemo(() => {
    if (!catalogo) return [];
    const q = texto.trim().toLowerCase();
    return catalogo.pruebas.filter(p => {
      if (poblacion && p.poblacion !== poblacion) return false;
      if (fuente && p.fuente_estimada !== fuente) return false;
      if (!q) return true;
      return (
        (p.nombre || "").toLowerCase().includes(q) ||
        (p.id || "").toLowerCase().includes(q)
      );
    });
  }, [catalogo, poblacion, fuente, texto]);

  // Agrupado por población para visualización
  const agrupadas = useMemo(() => {
    const g = { infantil: [], adulto_joven: [], adulto_mayor: [] };
    filtradas.forEach(p => {
      if (g[p.poblacion]) g[p.poblacion].push(p);
    });
    return g;
  }, [filtradas]);

  if (error && !catalogo) {
    return (
      <>
        <TopBar title="Pruebas disponibles" />
        <main className="p-8 max-w-2xl mx-auto" style={{ background: "var(--ns-bg)", minHeight: "100vh" }}>
          <div className="rounded-md border p-8 text-center"
            style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
            <I name="error_outline" className="text-4xl mb-3" style={{ color: "#dc2626" }} />
            <p className="ns-serif text-lg italic" style={{ color: "var(--ns-text)" }}>
              No se pudo cargar el catálogo de pruebas
            </p>
            <p className="text-xs mt-2" style={{ color: "var(--ns-muted)" }}>{error}</p>
          </div>
        </main>
      </>
    );
  }

  if (!catalogo) {
    return (
      <>
        <TopBar title="Pruebas disponibles" />
        <main className="p-8 flex flex-col items-center justify-center gap-3" style={{ background: "var(--ns-bg)", minHeight: "100vh" }}>
          <div className="animate-spin w-9 h-9 border-4 rounded-full"
            style={{ borderColor: `${TEAL}33`, borderTopColor: TEAL }} />
          <p className="ns-eyebrow" style={{ color: TEAL }}>Cargando catálogo</p>
        </main>
      </>
    );
  }

  return (
    <>
      <TopBar title="Aprender · Pruebas disponibles" />
      <main className="p-6 lg:p-8 max-w-7xl mx-auto space-y-7"
        style={{ background: "var(--ns-bg)", minHeight: "100vh" }}>

        {/* Header editorial */}
        <div className="ns-section-rule">
          <p className="ns-eyebrow" style={{ color: TEAL }}>Catálogo clínico</p>
          <h2 className="ns-serif text-3xl font-bold mt-1 mb-2" style={{ color: "var(--ns-text)" }}>
            Pruebas con <span className="ns-serif-italic" style={{ color: TEAL }}>baremos colombianos</span>
          </h2>
          <p className="text-sm max-w-2xl" style={{ color: "var(--ns-muted)" }}>
            NeuroSoft tiene cargadas{" "}
            <span className="ns-serif text-base font-bold" style={{ color: "var(--ns-text)" }}>
              {catalogo.total}
            </span>{" "}
            pruebas con baremos para población colombiana. Cada una se procesa con la estrategia de cálculo
            correcta y se interpreta según la fuente normativa correspondiente.
          </p>
        </div>

        {/* KPIs por población */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(POBLACION_META).map(([k, m]) => {
            const total = catalogo.por_poblacion[k] || 0;
            return (
              <button key={k} onClick={() => setPoblacion(poblacion === k ? "" : k)}
                className="text-left p-5 rounded-md border transition-all hover:shadow-sm"
                style={{
                  background: "var(--ns-card)",
                  borderColor: poblacion === k ? m.c : "var(--ns-card-b)",
                  borderLeftWidth: 3,
                  borderLeftColor: m.c,
                }}>
                <div className="flex items-start justify-between mb-2">
                  <I name={m.ic} className="text-base opacity-60" style={{ color: m.c }} />
                  {poblacion === k && (
                    <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded-sm"
                      style={{ background: `${m.c}15`, color: m.c }}>
                      Filtrado
                    </span>
                  )}
                </div>
                <p className="ns-serif text-3xl font-bold tabular-nums leading-none" style={{ color: "var(--ns-text)" }}>
                  {total}
                </p>
                <p className="ns-eyebrow mt-2">{m.label}</p>
                <p className="text-[10px] ns-serif-italic mt-1" style={{ color: "var(--ns-muted)" }}>
                  {m.rango}
                </p>
              </button>
            );
          })}
        </div>

        {/* Filtros */}
        <div className="rounded-md border p-4"
          style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
          <div className="flex items-center gap-3 mb-3">
            <I name="search" className="text-lg" style={{ color: TEAL }} />
            <input
              type="text"
              value={texto}
              onChange={e => setTexto(e.target.value)}
              placeholder="Busca por nombre o código de prueba (ej. WISC, TMT, Stroop, ViTMTA…)"
              className="flex-1 px-3 py-2 rounded-md text-sm"
              style={{
                background: "var(--ns-input)",
                border: "1px solid var(--ns-card-b)",
                color: "var(--ns-text)",
              }}
            />
            {(texto || poblacion || fuente) && (
              <button onClick={() => { setTexto(""); setPoblacion(""); setFuente(""); }}
                className="text-xs flex items-center gap-1 px-2 py-1 rounded"
                style={{ color: "var(--ns-muted)" }}>
                <I name="close" className="text-sm" /> Limpiar filtros
              </button>
            )}
          </div>

          {/* Chips de fuente */}
          <div>
            <p className="ns-eyebrow mb-2">Fuente normativa</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(FUENTE_META).map(([k, m]) => {
                const activo = fuente === k;
                return (
                  <button key={k} onClick={() => setFuente(activo ? "" : k)}
                    className="text-xs font-semibold px-3 py-1.5 rounded-md transition-all"
                    style={{
                      background: activo ? m.c : "transparent",
                      color: activo ? "#fff" : m.c,
                      border: `1px solid ${m.c}50`,
                    }}>
                    {m.lb}
                    {m.anio && <span className="ns-serif-italic font-normal ml-1 opacity-70"> · {m.anio}</span>}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Resultados resumen */}
        <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
          <span className="ns-serif text-base font-bold tabular-nums" style={{ color: "var(--ns-text)" }}>
            {filtradas.length}
          </span>{" "}
          prueba{filtradas.length !== 1 ? "s" : ""} {texto && `coinciden con “${texto}”`}
        </p>

        {/* Listado agrupado por población */}
        {filtradas.length === 0 ? (
          <div className="rounded-md border p-12 text-center"
            style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
            <I name="search_off" className="text-4xl mb-3" style={{ color: "var(--ns-muted)" }} />
            <p className="ns-serif text-lg italic" style={{ color: "var(--ns-muted)" }}>
              Sin resultados con los filtros actuales.
            </p>
          </div>
        ) : (
          Object.entries(agrupadas).map(([pop, lista]) => {
            if (lista.length === 0) return null;
            const m = POBLACION_META[pop];
            return (
              <section key={pop}>
                <div className="flex items-baseline gap-3 mb-3">
                  <I name={m.ic} style={{ color: m.c }} />
                  <h3 className="ns-serif text-lg font-bold" style={{ color: "var(--ns-text)" }}>
                    {m.label}
                  </h3>
                  <span className="ns-serif-italic text-sm" style={{ color: "var(--ns-muted)" }}>
                    {lista.length} prueba{lista.length !== 1 ? "s" : ""} · {m.rango}
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {lista.map(p => <PruebaCard key={p.id} prueba={p} popMeta={m} onClick={() => setPruebaSel(p)} />)}
                </div>
              </section>
            );
          })
        )}

        {/* Fuentes — ficha al pie */}
        {fuentes.length > 0 && (
          <div className="rounded-md p-5 mt-8"
            style={{ background: "var(--ns-subtle)", borderLeft: `3px solid ${TEAL}` }}>
            <p className="ns-eyebrow mb-2" style={{ color: TEAL }}>Fuentes normativas integradas</p>
            <ul className="text-xs space-y-1.5" style={{ color: "var(--ns-text)" }}>
              {fuentes.map(s => (
                <li key={s.id}>
                  · <span className="ns-serif font-bold">{s.nombre}</span>{" "}
                  <span className="ns-serif-italic" style={{ color: "var(--ns-muted)" }}>
                    ({s.autores}, {s.anio})
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </main>

      {/* Detalle modal */}
      {pruebaSel && (
        <PruebaDetalle prueba={pruebaSel} onClose={() => setPruebaSel(null)} />
      )}
    </>
  );
}

function PruebaCard({ prueba, popMeta, onClick }) {
  const fm = FUENTE_META[prueba.fuente_estimada] || FUENTE_META.otro;
  const tm = TIPO_CALCULO_META[prueba.tipo_calculo] || { lb: prueba.tipo_calculo };
  return (
    <button onClick={onClick}
      className="text-left p-4 rounded-md border transition-all hover:shadow-sm"
      style={{
        background: "var(--ns-card)",
        borderColor: "var(--ns-card-b)",
        borderLeftWidth: 3,
        borderLeftColor: popMeta.c,
      }}>
      <div className="flex items-start justify-between mb-1">
        <span className="text-[10px] font-semibold uppercase tracking-wider"
          style={{ color: fm.c }}>
          {fm.lb}
        </span>
        <I name="open_in_new" className="text-xs opacity-30" />
      </div>
      <h4 className="ns-serif text-sm font-bold leading-snug mt-1" style={{ color: "var(--ns-text)" }}>
        {prueba.nombre}
      </h4>
      <div className="flex items-center gap-2 mt-2">
        <span className="text-[10px] ns-mono" style={{ color: "var(--ns-muted)" }}>
          {prueba.id}
        </span>
        <span className="text-[10px]" style={{ color: "var(--ns-muted)" }}>·</span>
        <span className="text-[10px] ns-serif-italic" style={{ color: "var(--ns-muted)" }}>
          {tm.lb}
        </span>
      </div>
    </button>
  );
}

function PruebaDetalle({ prueba, onClose }) {
  const fm = FUENTE_META[prueba.fuente_estimada] || FUENTE_META.otro;
  const tm = TIPO_CALCULO_META[prueba.tipo_calculo] || { lb: prueba.tipo_calculo, hint: "" };
  const pm = POBLACION_META[prueba.poblacion] || { label: prueba.poblacion, c: "#475569" };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(15,23,42,0.55)", backdropFilter: "blur(2px)" }}
      onClick={onClose}>
      <div onClick={e => e.stopPropagation()}
        className="w-full max-w-lg rounded-lg shadow-2xl overflow-hidden"
        style={{ background: "var(--ns-card)" }}>
        {/* Header */}
        <div className="px-6 py-4 border-b" style={{ borderColor: "var(--ns-card-b)" }}>
          <div className="flex items-center justify-between mb-2">
            <p className="ns-eyebrow" style={{ color: pm.c }}>{pm.label}</p>
            <button onClick={onClose} className="p-1.5 rounded-md hover:bg-gray-100"
              style={{ color: "var(--ns-muted)" }}>
              <I name="close" className="text-base" />
            </button>
          </div>
          <h3 className="ns-serif text-xl font-bold" style={{ color: "var(--ns-text)" }}>
            {prueba.nombre}
          </h3>
          <p className="text-xs ns-mono mt-1" style={{ color: "var(--ns-muted)" }}>
            ID: {prueba.id}
          </p>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4">
          <div>
            <p className="ns-eyebrow mb-1.5">Fuente normativa</p>
            <p className="ns-serif text-base font-bold" style={{ color: fm.c }}>{fm.lb}</p>
            <p className="text-xs ns-serif-italic mt-0.5" style={{ color: "var(--ns-muted)" }}>
              {fm.autores} {fm.anio ? `· ${fm.anio}` : ""}
            </p>
          </div>

          <div>
            <p className="ns-eyebrow mb-1.5">Tipo de cálculo</p>
            <p className="text-sm font-semibold" style={{ color: "var(--ns-text)" }}>{tm.lb}</p>
            {tm.hint && (
              <p className="text-xs mt-1 leading-relaxed" style={{ color: "var(--ns-muted)" }}>
                {tm.hint}
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3 pt-3 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
            <div>
              <p className="ns-eyebrow mb-1">Métrica de salida</p>
              <p className="text-sm font-semibold ns-serif" style={{ color: "var(--ns-text)" }}>
                {prueba.tipo_metrica}
              </p>
            </div>
            <div>
              <p className="ns-eyebrow mb-1">Claves de baremo</p>
              <p className="ns-serif text-lg font-bold tabular-nums" style={{ color: TEAL }}>
                {prueba.n_baremos.toLocaleString("es-CO")}
              </p>
            </div>
          </div>

          <div className="rounded-md p-3"
            style={{ background: `${TEAL}08`, borderLeft: `3px solid ${TEAL}` }}>
            <p className="text-[11px] leading-relaxed" style={{ color: "var(--ns-text)" }}>
              <I name="info" className="text-xs mr-1" style={{ color: TEAL }} />
              Cuando aplicas esta prueba en una evaluación, NeuroSoft escoge la celda de baremo
              que corresponde a la edad / escolaridad / sexo del paciente (según la estrategia)
              y devuelve el escalar, percentil o índice equivalente.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
