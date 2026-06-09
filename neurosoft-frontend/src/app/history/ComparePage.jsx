/* ═══════════════════════════════════════════════════════════════════════
 * src/app/history/ComparePage.jsx — Comparación Pre–Post de evaluaciones
 * ───────────────────────────────────────────────────────────────────────
 * Compara dos evaluaciones del mismo paciente (PRE vs POST) y produce:
 *   • Resumen Mejora/Estable/Deterioro/Sin dato
 *   • Gráfico horizontal de Z pre vs post (barras)
 *   • Tabla detallada por prueba con Δ Z
 *   • Radar de dominios cognitivos
 *   • Resumen por dominio (mejora/estable/deterioro)
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useMemo, useState } from "react";
import {
  Bar, BarChart, CartesianGrid, Legend, PolarAngleAxis, PolarGrid,
  PolarRadiusAxis, Radar, RadarChart, ReferenceLine,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { api, _parseError, exportCSV } from "../../api/client.js";
import {
  Btn, Card, I, Label, Sel, TopBar,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { analyzeRCI } from "../../utils/rci.js";
import { useToast } from "../../contexts.jsx";
import { safeLS } from "../../utils/safeLS.js";
import { usePatientsPanel } from "../../hooks/usePatientsPanel.js";
import { PatientSelect } from "../../ui/forms/PatientSelector.jsx";

const CAMBIO_STYLE = {
  mejora:    { bg: "#dcfce7", color: "#166534", label: "Mejora",     ico: "trending_up" },
  estable:   { bg: "#f3f4f6", color: "#6b7280", label: "Estable",    ico: "trending_flat" },
  deterioro: { bg: "#fee2e2", color: "#991b1b", label: "Deterioro",  ico: "trending_down" },
  sin_dato:  { bg: "#fef3c7", color: "#92400e", label: "Sin dato",   ico: "help" },
};

export default function ComparePage({ _setPage }) {
  const toast = useToast();
  const { patients, loading: patientsLoading } = usePatientsPanel();
  const [patId, setPatId] = useState(() => safeLS.get("ns_sel_patient") || "");
  const [evals, setEvals] = useState([]);
  const [preId, setPreId] = useState("");
  const [postId, setPostId] = useState("");
  const [data, setData] = useState(null);
  const [ld, setLd] = useState(false);
  const [err, setErr] = useState("");
  const [domFilter, setDomFilter] = useState("");

  useEffect(() => {
    if (!patId) { setEvals([]); return; }
    api.get(`/api/v1/evaluations/${patId}`).then((d) => {
      const arr = d.evaluaciones || d.evaluations || [];
      setEvals(arr);
      if (arr.length >= 2) {
        /* §H7-fix: NO asumir orden del backend. Ordenamos
         * explícitamente por fecha ASC: PRE = más antigua, POST = más
         * reciente. Si el backend cambia el orden, la comparativa
         * sigue siendo correcta. */
        const _ts = (x) => {
          const d = x.fecha || x.fecha_aplicacion || x.created_at;
          const t = d ? new Date(d).getTime() : 0;
          return Number.isFinite(t) ? t : 0;
        };
        const ordered = [...arr].sort((a, b) => _ts(a) - _ts(b));
        setPreId(ordered[0].evaluation_id || ordered[0].id);
        setPostId(ordered[ordered.length - 1].evaluation_id || ordered[ordered.length - 1].id);
      }
    }).catch(() => setEvals([]));
  }, [patId]);

  const runCompare = async () => {
    if (!patId || !preId || !postId) {
      setErr("Seleccione paciente, evaluación PRE y POST");
      return;
    }
    if (preId === postId) {
      setErr("PRE y POST no pueden ser la misma evaluación");
      return;
    }
    setLd(true);
    setErr("");
    setData(null);
    try {
      const d = await api.get(`/api/v1/evaluations/${patId}/compare?pre=${preId}&post=${postId}`);
      setData(d);
    } catch (e) { setErr(_parseError(e)); }
    setLd(false);
  };

  /* §M9-fix: memoizamos para evitar recomputar en cada render del IIFE
   * del resumen RCI. Para evaluaciones con 100+ subtests esto ahorra
   * milisegundos perceptibles en cada interacción. */
  const filteredTests = useMemo(
    () => (data?.tests?.filter(t => !domFilter || t.dominio_cognitivo === domFilter) || []),
    [data, domFilter],
  );
  const uniqDoms = useMemo(
    () => (data ? [...new Set(data.tests.map(t => t.dominio_cognitivo).filter(Boolean))] : []),
    [data],
  );
  const rciResults = useMemo(() => {
    if (!data) return [];
    return (data.tests || [])
      .map(t => {
        if (t.pre.z == null || t.post.z == null) return null;
        return { ...t, rci: analyzeRCI({ pre: t.pre.z, post: t.post.z, metricKind: "z" }) };
      })
      .filter(Boolean);
  }, [data]);

  return (
    <>
      <TopBar title="Comparación Pre–Post" />
      <main className="p-8 space-y-6">
        <Card className="p-6 space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <PatientSelect
              patients={patients}
              loading={patientsLoading}
              value={patId}
              onChange={(id) => {
                setPatId(id);
                safeLS.set("ns_sel_patient", id);
                setData(null);
                setPreId("");
                setPostId("");
              }}
              placeholder="— Seleccione —"
            />
            <div>
              <Label>Evaluación PRE</Label>
              <Sel value={preId} onChange={(e) => setPreId(e.target.value)} disabled={!evals.length}>
                <option value="">— Inicial —</option>
                {evals.map(e => {
                  const id = e.evaluation_id || e.id;
                  return <option key={id} value={id}>{e.fecha || ""} — {e.protocolo || "Eval"}</option>;
                })}
              </Sel>
            </div>
            <div>
              <Label>Evaluación POST</Label>
              <Sel value={postId} onChange={(e) => setPostId(e.target.value)} disabled={!evals.length}>
                <option value="">— Seguimiento —</option>
                {evals.map(e => {
                  const id = e.evaluation_id || e.id;
                  return <option key={id} value={id}>{e.fecha || ""} — {e.protocolo || "Eval"}</option>;
                })}
              </Sel>
            </div>
          </div>
          <div className="flex gap-3 items-center">
            <Btn onClick={runCompare} disabled={ld || !patId || !preId || !postId} className="text-sm">
              <I name="analytics" />{ld ? "Comparando..." : "Comparar"}
            </Btn>
            {err && (
              <span className="text-xs text-red-700 font-bold flex items-center gap-1">
                <I name="error" className="text-sm" />{err}
              </span>
            )}
            {evals.length < 2 && patId && (
              <span className="text-xs text-gray-500">
                Se necesitan al menos 2 evaluaciones guardadas.
              </span>
            )}
          </div>
        </Card>

        {data && (
          <>
            {/* Resumen clínico + RCI */}
            {(() => {
              /* §M9-fix: rciResults se memoiza arriba (useMemo). Aquí solo
               * derivamos los conteos del array memoizado. */
              const sigMejora    = rciResults.filter(r => r.rci?.significant && r.rci?.change === "mejora").length;
              const sigDeterioro = rciResults.filter(r => r.rci?.significant && r.rci?.change === "deterioro").length;
              const sugestivos   = rciResults.filter(r => r.rci?.suggestive).length;
              const estables     = rciResults.filter(r => r.rci && !r.rci.significant && !r.rci.suggestive).length;

              const exportData = () => {
                const rows = (data.tests || []).map(t => {
                  const r = (t.pre.z != null && t.post.z != null)
                    ? analyzeRCI({ pre: t.pre.z, post: t.post.z, metricKind: "z" }) : null;
                  return {
                    prueba: t.test_nombre, dominio: t.dominio_cognitivo || "",
                    pd_pre: t.pre.puntaje_bruto ?? "", pd_post: t.post.puntaje_bruto ?? "",
                    z_pre: t.pre.z?.toFixed(2) ?? "", z_post: t.post.z?.toFixed(2) ?? "",
                    delta_z: t.delta_z?.toFixed(2) ?? "",
                    rci: r?.rci ?? "", rci_nivel: r?.level ?? "", rci_p: r?.pValue ?? "",
                    cambio: t.cambio,
                  };
                });
                exportCSV(rows, `Comparativa_${data.patient?.nombre || "paciente"}_${Date.now()}.csv`);
              };

              return (
                <>
                  <div className="grid grid-cols-4 gap-4">
                    {[
                      ["mejora",    "#22c55e", "trending_up"],
                      ["estable",   "#6b7280", "trending_flat"],
                      ["deterioro", "#ef4444", "trending_down"],
                      ["sin_dato",  "#eab308", "help"],
                    ].map(([k, c, ic]) => (
                      <Card key={k} className="p-5 text-center">
                        <I name={ic} className="text-3xl mb-1" style={{ color: c }} />
                        <div className="text-2xl font-bold" style={{ color: c }}>{data.resumen[k]}</div>
                        <div className="text-xs uppercase font-bold" style={{ color: "var(--ns-muted)" }}>
                          {CAMBIO_STYLE[k].label}
                        </div>
                      </Card>
                    ))}
                  </div>

                  {/* Panel RCI */}
                  {rciResults.length > 0 && (
                    <Card className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="text-sm font-bold flex items-center gap-2">
                            <I name="science" fill style={{ color: TEAL }} />
                            Índice de Cambio Confiable (RCI · Jacobson &amp; Truax, 1991)
                          </h3>
                          <p className="text-[10px] mt-0.5" style={{ color: "var(--ns-muted)" }}>
                            Determina si cada cambio supera el error de medición del test. |RCI|≥1.96 = significativo (p&lt;.05)
                          </p>
                        </div>
                        <Btn v="outline" onClick={exportData} className="text-xs shrink-0">
                          <I name="download" className="text-sm" />CSV
                        </Btn>
                      </div>
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
                        {[
                          { v: sigMejora,    l: "Mejora significativa",    c: "#059669", i: "verified",       sub: "RCI ≥ +1.96" },
                          { v: sigDeterioro, l: "Deterioro significativo",  c: "#dc2626", i: "warning",        sub: "RCI ≤ -1.96" },
                          { v: sugestivos,   l: "Cambio sugestivo",         c: "#d97706", i: "info",           sub: "|RCI| 1.64–1.96" },
                          { v: estables,     l: "Dentro del error",         c: "#6b7280", i: "remove_circle",  sub: "|RCI| < 1.64" },
                        ].map(item => (
                          <div key={item.l} className="p-4 rounded-2xl border text-center"
                            style={{ borderColor: `${item.c}30`, background: `${item.c}08` }}>
                            <I name={item.i} fill className="text-2xl mb-1" style={{ color: item.c }} />
                            <div className="text-2xl font-extrabold" style={{ color: item.c }}>{item.v}</div>
                            <div className="text-[10px] font-bold mt-0.5" style={{ color: item.c }}>{item.l}</div>
                            <div className="text-[9px] mt-0.5" style={{ color: "var(--ns-muted)" }}>{item.sub}</div>
                          </div>
                        ))}
                      </div>
                      {/* Narrativa automática */}
                      {(sigMejora > 0 || sigDeterioro > 0) && (
                        <div className="p-4 rounded-xl text-xs leading-relaxed"
                          style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
                          <I name="summarize" className="text-sm mr-1" style={{ color: TEAL }} />
                          <span className="font-bold" style={{ color: "var(--ns-text)" }}>Interpretación clínica del cambio: </span>
                          {sigMejora > 0 && (
                            <span>
                              Se observa <strong style={{ color: "#059669" }}>mejora clínicamente significativa</strong> en{" "}
                              {sigMejora} prueba{sigMejora !== 1 ? "s" : ""} (RCI ≥ 1.96, p&lt;.05), superando el umbral
                              esperado por error de medición.{" "}
                            </span>
                          )}
                          {sigDeterioro > 0 && (
                            <span>
                              Se identifica <strong style={{ color: "#dc2626" }}>deterioro significativo</strong> en{" "}
                              {sigDeterioro} prueba{sigDeterioro !== 1 ? "s" : ""} (RCI ≤ -1.96), que requiere atención clínica.{" "}
                            </span>
                          )}
                          {sugestivos > 0 && (
                            <span>
                              Hay {sugestivos} cambio{sugestivos !== 1 ? "s" : ""} sugestivo{sugestivos !== 1 ? "s" : ""} (|RCI| 1.64–1.96)
                              que no alcanzan significancia estadística pero deben monitorizarse.{" "}
                            </span>
                          )}
                          Resultados basados en error de medición estándar para Z-scores (r=0.85).
                          Los valores RCI son orientativos y deben integrarse con el juicio clínico.
                        </div>
                      )}
                      {/* Leyenda */}
                      <div className="flex flex-wrap gap-4 mt-3 text-[10px]" style={{ color: "var(--ns-muted)" }}>
                        <span><strong>*</strong> = RCI significativo (p&lt;.05) · |RCI|≥1.96</span>
                        <span><strong>~</strong> = Cambio sugestivo (p&lt;.10) · |RCI| 1.64–1.96</span>
                        <span>SEM estimado con r=0.85 (conservador)</span>
                      </div>
                    </Card>
                  )}
                </>
              );
            })()}

            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-gray-500 uppercase">Perfil Z · PRE vs POST</h3>
                <span className="text-xs text-gray-400">{data.resumen.tests_comunes} pruebas comunes</span>
              </div>
              <CompareChart tests={filteredTests} />
            </Card>

            {/* Filtro dominio + tabla */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-gray-500 uppercase">Detalle por prueba</h3>
                <Sel value={domFilter} onChange={(e) => setDomFilter(e.target.value)} className="text-xs w-56">
                  <option value="">Todos los dominios</option>
                  {uniqDoms.map(d => <option key={d} value={d}>{d}</option>)}
                </Sel>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b-2" style={{ borderColor: "var(--ns-card-b)" }}>
                      <th className="text-left py-2 px-2 font-bold uppercase tracking-wide">Prueba</th>
                      <th className="text-left py-2 px-2 font-bold uppercase tracking-wide">Dominio</th>
                      <th className="text-right py-2 px-2 font-bold uppercase tracking-wide">PD Pre</th>
                      <th className="text-right py-2 px-2 font-bold uppercase tracking-wide">PD Post</th>
                      <th className="text-right py-2 px-2 font-bold uppercase tracking-wide">Z Pre</th>
                      <th className="text-right py-2 px-2 font-bold uppercase tracking-wide">Z Post</th>
                      <th className="text-right py-2 px-2 font-bold uppercase tracking-wide">ΔZ</th>
                      <th className="text-right py-2 px-2 font-bold uppercase tracking-wide" title="Reliable Change Index (Jacobson & Truax 1991). |RCI|≥1.96 = cambio significativo p<.05">RCI</th>
                      <th className="text-center py-2 px-2 font-bold uppercase tracking-wide">Cambio</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTests.map((t) => {
                      const s = CAMBIO_STYLE[t.cambio];
                      const rciRow = (t.pre.z != null && t.post.z != null)
                        ? analyzeRCI({ pre: t.pre.z, post: t.post.z, metricKind: "z" }) : null;
                      const rowBg = rciRow?.significant
                        ? rciRow.change === "mejora" ? "#dcfce720" : "#fee2e220"
                        : rciRow?.suggestive ? "#fef3c720" : "";
                      return (
                        <tr key={t.test_id} className="border-b hover:bg-gray-50"
                          style={{ borderColor: "var(--ns-card-b)", background: rowBg }}>
                          <td className="py-2 px-2 font-semibold">{t.test_nombre}</td>
                          <td className="py-2 px-2 text-gray-500">{t.dominio_cognitivo || "—"}</td>
                          <td className="py-2 px-2 text-right font-mono">
                            {t.pre.puntaje_bruto !== null ? t.pre.puntaje_bruto.toFixed(1) : "—"}
                          </td>
                          <td className="py-2 px-2 text-right font-mono">
                            {t.post.puntaje_bruto !== null ? t.post.puntaje_bruto.toFixed(1) : "—"}
                          </td>
                          <td className="py-2 px-2 text-right font-mono">
                            {t.pre.z !== null ? t.pre.z.toFixed(2) : "—"}
                          </td>
                          <td className="py-2 px-2 text-right font-mono">
                            {t.post.z !== null ? t.post.z.toFixed(2) : "—"}
                          </td>
                          <td className="py-2 px-2 text-right font-mono font-bold"
                            style={{
                              color: t.delta_z === null ? "#9ca3af"
                                : t.delta_z >= 0.5 ? "#16a34a"
                                : t.delta_z <= -0.5 ? "#dc2626"
                                : "#6b7280"
                            }}>
                            {t.delta_z !== null ? (t.delta_z >= 0 ? "+" : "") + t.delta_z.toFixed(2) : "—"}
                          </td>
                          {(() => {
                            /* RCI: usa Z score (z-metric tiene M=0, SD=1) — Jacobson & Truax 1991 */
                            const r = (t.pre.z != null && t.post.z != null)
                              ? analyzeRCI({ pre: t.pre.z, post: t.post.z, metricKind: "z" })
                              : null;
                            return (
                              <td className="py-2 px-2 text-right font-mono font-bold" style={{ color: r?.color || "#9ca3af" }}>
                                {r ? (
                                  <span title={`${r.level} (${r.pValue})`}>
                                    {r.rci >= 0 ? "+" : ""}{r.rci.toFixed(2)}
                                    {r.significant && <span className="ml-1 text-[9px]">*</span>}
                                    {r.suggestive && !r.significant && <span className="ml-1 text-[9px]">~</span>}
                                  </span>
                                ) : "—"}
                              </td>
                            );
                          })()}
                          <td className="py-2 px-2 text-center">
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold"
                              style={{ background: s.bg, color: s.color }}>
                              <I name={s.ico} className="text-xs" />{s.label}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                {filteredTests.length === 0 && (
                  <div className="py-6 text-center text-gray-400 text-xs">
                    Sin pruebas que coincidan con el filtro.
                  </div>
                )}
              </div>
            </Card>

            {data.dominios && data.dominios.length >= 3 && (
              <Card className="p-6">
                <h3 className="text-sm font-bold text-gray-500 uppercase mb-4">
                  Perfil cognitivo · Radar Pre vs Post
                </h3>
                <CompareRadar dominios={data.dominios} />
              </Card>
            )}

            {data.dominios && data.dominios.length > 0 && (
              <Card className="p-6">
                <h3 className="text-sm font-bold text-gray-500 uppercase mb-4">Resumen por dominio cognitivo</h3>
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
                  {data.dominios.map((d) => (
                    <div key={d.nombre} className="p-4 rounded-xl border"
                      style={{ borderColor: "var(--ns-card-b)" }}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold">{d.nombre}</span>
                        <span className="text-[10px] text-gray-400">{d.total} pruebas</span>
                      </div>
                      <div className="flex gap-1 h-2 rounded-full overflow-hidden" style={{ background: "var(--ns-subtle)" }}>{/* §dark-mode-fix */}
                        {d.mejora    > 0 && <div style={{ width: `${(d.mejora    / d.total) * 100}%`, background: "#22c55e" }} title={`${d.mejora} mejora`} />}
                        {d.estable   > 0 && <div style={{ width: `${(d.estable   / d.total) * 100}%`, background: "#9ca3af" }} title={`${d.estable} estable`} />}
                        {d.deterioro > 0 && <div style={{ width: `${(d.deterioro / d.total) * 100}%`, background: "#ef4444" }} title={`${d.deterioro} deterioro`} />}
                      </div>
                      <div className="flex gap-3 mt-2 text-[10px] text-gray-500">
                        <span>↑{d.mejora}</span><span>={d.estable}</span><span>↓{d.deterioro}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {(data.solo_pre?.length > 0 || data.solo_post?.length > 0) && (
              <Card className="p-5" style={{ background: "#fef3c720", borderLeft: "3px solid #d97706" }}>
                <h4 className="text-xs font-bold mb-2" style={{ color: "#b45309" }}>Pruebas no comparables</h4>
                {data.solo_pre.length > 0 && (
                  <p className="text-xs mb-1"><strong>Sólo PRE:</strong> {data.solo_pre.join(", ")}</p>
                )}
                {data.solo_post.length > 0 && (
                  <p className="text-xs"><strong>Sólo POST:</strong> {data.solo_post.join(", ")}</p>
                )}
              </Card>
            )}
          </>
        )}
      </main>
    </>
  );
}

/* ─── Helpers de color conscientes del tema ─────────────────────── */
const NS_TOOLTIP_STYLE = () => ({
  background: "var(--ns-card)",
  border: "1px solid var(--ns-card-b)",
  borderRadius: 12,
  fontSize: 11,
  color: "var(--ns-text)",
});
const NS_GRID_COLOR = "var(--ns-card-b)";
const NS_MUTED_FILL = "var(--ns-muted)";

/* ─── Subcomponente: Bar chart Pre vs Post ──────────────────────── */
function CompareChart({ tests }) {
  if (!tests || tests.length === 0) {
    return <div className="p-8 text-center text-xs" style={{ color: "var(--ns-muted)" }}>Sin datos para graficar</div>;
  }
  const rows = tests
    .filter(t => t.pre.z !== null && t.post.z !== null)
    .slice(0, 15)
    .map((t) => ({
      name: (t.test_nombre || t.test_id).slice(0, 24),
      pre:  +(t.pre.z.toFixed(2)),
      post: +(t.post.z.toFixed(2)),
      delta: +((t.post.z - t.pre.z).toFixed(2)),
    }));
  if (rows.length === 0) {
    return <div className="p-8 text-center text-xs" style={{ color: "var(--ns-muted)" }}>Sin puntajes Z comparables</div>;
  }
  return (
    <ResponsiveContainer width="100%" height={Math.max(260, rows.length * 42 + 50)}>
      <BarChart data={rows} layout="vertical" margin={{ top: 10, right: 24, bottom: 10, left: 50 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={NS_GRID_COLOR} />
        <XAxis type="number" domain={[-3.5, 1.5]} ticks={[-3, -2, -1, 0, 1]}
          tick={{ fontSize: 10, fill: NS_MUTED_FILL }} />
        <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: NS_MUTED_FILL }} width={140} />
        <ReferenceLine x={-2} stroke="#fca5a5" strokeDasharray="2 2"
          label={{ value: "-2 SD", fill: "#dc2626", fontSize: 9 }} />
        <ReferenceLine x={-1} stroke="#fbbf24" strokeDasharray="2 2" />
        <ReferenceLine x={0} stroke={NS_MUTED_FILL} />
        <Tooltip
          formatter={(v, n) => [v, n === "pre" ? "Z Pre" : n === "post" ? "Z Post" : "ΔZ"]}
          contentStyle={NS_TOOLTIP_STYLE()}
        />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Bar dataKey="pre"  fill="#94a3b8" name="Z Pre"  radius={[0, 4, 4, 0]} />
        <Bar dataKey="post" fill="#0D9488" name="Z Post" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

/* ─── Subcomponente: Radar de dominios ──────────────────────────── */
function CompareRadar({ dominios }) {
  if (!dominios || dominios.length === 0) return null;
  const data = dominios
    .map((d) => ({
      dominio: d.nombre,
      pre:  +((d.z_pre_promedio  ?? 0).toFixed(2)),
      post: +((d.z_post_promedio ?? 0).toFixed(2)),
    }))
    .filter((d) => Number.isFinite(d.pre) && Number.isFinite(d.post));
  if (data.length < 3) return null;
  return (
    <ResponsiveContainer width="100%" height={320}>
      <RadarChart data={data} outerRadius={110}>
        <PolarGrid stroke={NS_GRID_COLOR} />
        <PolarAngleAxis dataKey="dominio" tick={{ fontSize: 10, fill: NS_MUTED_FILL }} />
        <PolarRadiusAxis angle={90} domain={[-3, 1]} tick={{ fontSize: 9, fill: NS_MUTED_FILL }} />
        <Radar name="Pre"  dataKey="pre"  stroke="#94a3b8" fill="#94a3b8" fillOpacity={0.35} />
        <Radar name="Post" dataKey="post" stroke="#0D9488" fill="#0D9488" fillOpacity={0.45} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Tooltip contentStyle={NS_TOOLTIP_STYLE()} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
