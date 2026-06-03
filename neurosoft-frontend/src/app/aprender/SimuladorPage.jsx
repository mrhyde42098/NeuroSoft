/* ═══════════════════════════════════════════════════════════════════════
 * src/app/aprender/SimuladorPage.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §M-2 Simulador de casos clínicos — entrenamiento interpretativo.
 *
 * Flujo:
 *   1. Listado de casos por dificultad y población
 *   2. Vista de caso: sociodemográficos + MC + antecedentes + observación + perfil
 *   3. Estudiante escribe su interpretación (libre)
 *   4. "Ver interpretación experta" — reveal con análisis paso a paso
 *
 * No requiere backend — todo client-side con casosSimulador.js
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState } from "react";
import { Btn, Card, I, TopBar, Txta } from "../../ui/primitives.jsx";
import { TEAL, NAVY } from "../../ui/tokens.js";
import { CASOS_SIMULADOR } from "../../data/casosSimulador.js";

const POB_LABELS = {
  infantil: "Infantil",
  adulto_joven: "Adulto joven",
  adulto_mayor: "Adulto mayor",
};

const DIF_LABELS = {
  facil: { lb: "Fácil", c: "#10b981" },
  media: { lb: "Media", c: "#f59e0b" },
  dificil: { lb: "Difícil", c: "#dc2626" },
};

export default function SimuladorPage() {
  const [casoSel, setCasoSel] = useState(null);
  const [respuesta, setRespuesta] = useState("");
  const [revelado, setRevelado] = useState(false);
  const [filtroPob, setFiltroPob] = useState("");

  const casos = filtroPob
    ? CASOS_SIMULADOR.filter(c => c.poblacion === filtroPob)
    : CASOS_SIMULADOR;

  const empezar = (c) => {
    setCasoSel(c);
    setRespuesta("");
    setRevelado(false);
  };

  const cerrar = () => { setCasoSel(null); setRevelado(false); setRespuesta(""); };

  /* Vista LISTADO */
  if (!casoSel) {
    return (
      <>
        <TopBar title="Simulador de casos clínicos" />
        <main className="p-8 max-w-5xl mx-auto space-y-5">
          <div className="flex items-center gap-3 mb-2">
            <I name="psychology_alt" style={{ color: TEAL, fontSize: 28 }} />
            <div>
              <h2 className="ns-serif text-xl font-bold">Practica interpretación clínica</h2>
              <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
                {CASOS_SIMULADOR.length} casos sintéticos con perfiles cognitivos REALES (baremos
                del motor NeuroSoft). Lee, interpreta y compara con la respuesta experta.
              </p>
            </div>
          </div>

          {/* Filtros */}
          <div className="flex gap-2 flex-wrap">
            <button onClick={() => setFiltroPob("")}
              className="text-xs px-3 py-1.5 rounded"
              style={{ background: !filtroPob ? TEAL : "var(--ns-subtle)",
                       color: !filtroPob ? "white" : "var(--ns-muted)" }}>Todos</button>
            {["infantil", "adulto_joven", "adulto_mayor"].map(p => (
              <button key={p} onClick={() => setFiltroPob(p)}
                className="text-xs px-3 py-1.5 rounded"
                style={{ background: filtroPob === p ? TEAL : "var(--ns-subtle)",
                         color: filtroPob === p ? "white" : "var(--ns-muted)" }}>{POB_LABELS[p]}</button>
            ))}
          </div>

          {/* Lista de casos */}
          <div className="grid sm:grid-cols-2 gap-4">
            {casos.map(c => {
              const dif = DIF_LABELS[c.dificultad];
              return (
                <button key={c.id} onClick={() => empezar(c)}
                  className="text-left p-5 rounded border transition-all hover:shadow-md flex flex-col h-full"
                  style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider"
                      style={{ color: TEAL }}>
                      {POB_LABELS[c.poblacion]}
                    </span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded"
                      style={{ background: `${dif.c}15`, color: dif.c }}>
                      {dif.lb}
                    </span>
                  </div>
                  <h3 className="ns-serif font-bold text-base mb-2 leading-tight">{c.titulo}</h3>
                  <p className="text-xs leading-relaxed mb-3 flex-1" style={{ color: "var(--ns-muted)" }}>
                    {c.motivo_consulta.slice(0, 140)}…
                  </p>
                  <div className="flex items-center justify-between text-[10px]"
                    style={{ color: "var(--ns-muted)" }}>
                    <span><I name="biotech" className="text-xs" /> {c.perfil.escalares.length} pruebas</span>
                    <span><I name="arrow_forward" className="text-xs" /> Resolver</span>
                  </div>
                </button>
              );
            })}
          </div>
        </main>
      </>
    );
  }

  /* Vista CASO ACTIVO */
  return (
    <>
      <TopBar title={casoSel.titulo}>
        <Btn variant="ghost" onClick={cerrar} className="text-xs">
          <I name="arrow_back" className="mr-1" />Volver
        </Btn>
      </TopBar>
      <main className="p-8 max-w-5xl mx-auto space-y-5">
        {/* Sociodemográficos */}
        <Card className="p-5">
          <p className="ns-eyebrow mb-2" style={{ color: TEAL }}>Datos del paciente (caso sintético)</p>
          <div className="grid sm:grid-cols-3 gap-3 text-sm">
            {Object.entries(casoSel.sociodemograficos).map(([k, v]) => (
              <div key={k}>
                <p className="text-[10px] uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
                  {k.replace(/_/g, " ")}
                </p>
                <p className="font-medium" style={{ color: "var(--ns-text)" }}>{v}</p>
              </div>
            ))}
          </div>
        </Card>

        {/* Motivo de consulta */}
        <Card className="p-5">
          <p className="ns-eyebrow mb-2" style={{ color: TEAL }}>Motivo de consulta</p>
          <p className="ns-serif-italic text-sm leading-relaxed" style={{ color: "var(--ns-text)" }}>
            "{casoSel.motivo_consulta}"
          </p>
        </Card>

        {/* Antecedentes */}
        <Card className="p-5">
          <p className="ns-eyebrow mb-2" style={{ color: TEAL }}>Antecedentes relevantes</p>
          <ul className="space-y-1 text-sm" style={{ color: "var(--ns-text)" }}>
            {casoSel.antecedentes.map((a, i) => <li key={i}>· {a}</li>)}
          </ul>
        </Card>

        {/* Observación */}
        <Card className="p-5">
          <p className="ns-eyebrow mb-2" style={{ color: TEAL }}>Observación clínica</p>
          <p className="text-sm leading-relaxed" style={{ color: "var(--ns-text)" }}>
            {casoSel.observacion}
          </p>
        </Card>

        {/* Perfil cognitivo */}
        <Card className="p-5">
          <p className="ns-eyebrow mb-3" style={{ color: TEAL }}>
            Perfil cognitivo — {casoSel.perfil.protocolo}
          </p>
          <table className="w-full text-xs">
            <thead style={{ background: "var(--ns-subtle)" }}>
              <tr>
                <th className="text-left p-2">Prueba</th>
                <th className="text-left p-2">Dominio</th>
                <th className="text-right p-2">PD</th>
                <th className="text-right p-2">Escalar</th>
                <th className="text-left p-2">Interp.</th>
              </tr>
            </thead>
            <tbody>
              {casoSel.perfil.escalares.map((e, i) => (
                <tr key={i} style={{ borderBottom: "1px solid var(--ns-card-b)" }}>
                  <td className="p-2 font-bold ns-mono">{e.test}</td>
                  <td className="p-2" style={{ color: "var(--ns-muted)" }}>{e.dominio}</td>
                  <td className="p-2 text-right ns-mono">{e.pd}</td>
                  <td className="p-2 text-right ns-mono font-bold" style={{ color: TEAL }}>{e.escalar}</td>
                  <td className="p-2 text-[11px]" style={{ color: "var(--ns-muted)" }}>{e.interp}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {casoSel.perfil.indices && (
            <div className="mt-3 pt-3 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
              <p className="ns-eyebrow mb-2">Índices compuestos</p>
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
                {casoSel.perfil.indices.map(idx => (
                  <div key={idx.id} className="text-center p-2 rounded"
                    style={{ background: "var(--ns-subtle)" }}>
                    <p className="text-[10px] font-bold" style={{ color: NAVY }}>{idx.id}</p>
                    <p className="text-xl font-bold" style={{ color: TEAL }}>{idx.ci}</p>
                    <p className="text-[9px]" style={{ color: "var(--ns-muted)" }}>{idx.interp}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>

        {/* Tu interpretación */}
        <Card className="p-5">
          <p className="ns-eyebrow mb-2" style={{ color: NAVY }}>Tu interpretación clínica</p>
          <p className="text-xs mb-3" style={{ color: "var(--ns-muted)" }}>
            Escribe: (a) perfil dominante, (b) hipótesis diagnóstica,
            (c) batería complementaria que pedirías, (d) recomendaciones iniciales.
          </p>
          <Txta rows={10} value={respuesta} onChange={e => setRespuesta(e.target.value)}
            placeholder="(a) Perfil dominante:&#10;&#10;(b) Hipótesis diagnóstica (DSM-5 + CIE-10):&#10;&#10;(c) Batería complementaria:&#10;&#10;(d) Recomendaciones:" />
          {!revelado && (
            <div className="mt-3 flex justify-end">
              <Btn onClick={() => setRevelado(true)}
                style={{ background: TEAL, color: "white", borderColor: TEAL }}>
                <I name="visibility" className="mr-1.5" />Ver interpretación experta
              </Btn>
            </div>
          )}
        </Card>

        {/* Interpretación experta */}
        {revelado && (
          <Card className="p-5" style={{ background: "rgba(13,148,136,0.04)", borderLeft: `3px solid ${TEAL}` }}>
            <p className="ns-eyebrow mb-3" style={{ color: TEAL }}>Interpretación experta</p>

            <div className="mb-4">
              <p className="font-bold mb-1">Perfil dominante</p>
              <p className="text-sm leading-relaxed whitespace-pre-line" style={{ color: "var(--ns-text)" }}>
                {casoSel.interpretacion_experta.perfil_dominante}
              </p>
            </div>

            <div className="mb-4">
              <p className="font-bold mb-1">Hipótesis clínica</p>
              <p className="text-sm leading-relaxed" style={{ color: "var(--ns-text)" }}>
                {casoSel.interpretacion_experta.hipotesis}
              </p>
            </div>

            <div className="mb-4">
              <p className="font-bold mb-1">Diagnóstico propuesto</p>
              <p className="text-sm leading-relaxed whitespace-pre-line ns-serif-italic"
                style={{ color: "var(--ns-text)" }}>
                {casoSel.interpretacion_experta.diagnostico_propuesto}
              </p>
            </div>

            <div className="mb-4">
              <p className="font-bold mb-1">Batería complementaria sugerida</p>
              <ul className="space-y-1 text-sm" style={{ color: "var(--ns-text)" }}>
                {casoSel.interpretacion_experta.bateria_complementaria.map((b, i) => (
                  <li key={i}>· {b}</li>
                ))}
              </ul>
            </div>

            <div className="mb-3">
              <p className="font-bold mb-1">Recomendaciones clave</p>
              <ul className="space-y-1 text-sm" style={{ color: "var(--ns-text)" }}>
                {casoSel.interpretacion_experta.recomendaciones_clave.map((r, i) => (
                  <li key={i}>· {r}</li>
                ))}
              </ul>
            </div>

            {casoSel.referencias_tecnicas?.length > 0 && (
              <div className="border-t pt-3 mt-3" style={{ borderColor: "var(--ns-card-b)" }}>
                <p className="ns-eyebrow mb-1">Referencias técnicas</p>
                <ul className="space-y-0.5 text-[11px] ns-serif-italic" style={{ color: "var(--ns-muted)" }}>
                  {casoSel.referencias_tecnicas.map((r, i) => <li key={i}>· {r}</li>)}
                </ul>
              </div>
            )}
          </Card>
        )}
      </main>
    </>
  );
}
