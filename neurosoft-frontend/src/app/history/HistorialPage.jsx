/* ═══════════════════════════════════════════════════════════════════════
 * src/app/history/HistorialPage.jsx — Historial + Comparativo Pre-Post
 * ───────────────────────────────────────────────────────────────────────
 * Lista evaluaciones del paciente, permite ver detalle de cada una y
 * (cuando hay ≥ 2) muestra una gráfica longitudinal de los índices
 * compuestos en el tiempo.
 *
 * Soporta también informes inconclusos (flag/timeline) que se ven
 * embebidos al seleccionar paciente.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, _parseError, exportCSV } from "../../api/client.js";
import { useToast } from "../../contexts.jsx";
import {
  Btn, Card, I, Label, Sel, TopBar,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { lc } from "../../utils/colores.js";
import { SkeletonCard } from "../../ui/Skeleton.jsx";
import { safeLS } from "../../utils/safeLS.js";
import { usePatientsPanel } from "../../hooks/usePatientsPanel.js";
import { PatientSelect } from "../../ui/forms/PatientSelector.jsx";

export default function HistorialPage({ setPage }) {
  const toast = useToast();
  const initPat = safeLS.get("ns_sel_patient") || "";
  const [patId, setPatId] = useState(initPat);
  const [evals, setEvals] = useState([]);
  const [detail, setDetail] = useState(null);
  const [ld, setLd] = useState(false);
  const { patients, loading: patientsLoading } = usePatientsPanel();
  const [showLongitudinal, setShowLongitudinal] = useState(false);
  const [allDetails, setAllDetails] = useState([]);
  const [inconclusos, setInconclusos] = useState([]);
  const [incStats, setIncStats] = useState(null);

  useEffect(() => {
    api.get("/api/v1/inconclusos/stats").then(setIncStats).catch(() => toast.error("Error cargando inconclusos"));
    return () => safeLS.remove("ns_sel_patient");
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { if (initPat) loadH(initPat);   }, []);

  const loadH = async (pid) => {
    if (!pid) return;
    setLd(true);
    setDetail(null);
    setAllDetails([]);
    setInconclusos([]);
    try {
      const d = await api.get(`/api/v1/evaluations/${pid}`);
      const evList = d.evaluaciones || d.evaluations || [];
      setEvals(evList);
      if (evList.length > 1) {
        const details = await Promise.all(
          evList.map(ev => api.get(`/api/v1/evaluations/detail/${ev.evaluation_id || ev.id}`).catch(() => null))
        );
        setAllDetails(details.filter(Boolean));
      }
      try {
        const inc = await api.get(`/api/v1/inconclusos/?patient_id=${pid}`);
        setInconclusos(inc || []);
      } catch {}
    } catch { setEvals([]); }
    setLd(false);
  };

  const resolverInc = async (id, estado) => {
    try {
      await api.patch(`/api/v1/inconclusos/${id}`, {
        estado,
        notas_resolucion: estado === "resuelto" ? "Resuelto desde historial" : "Cerrado sin resolver",
      });
      loadH(patId);
      api.get("/api/v1/inconclusos/stats").then(setIncStats).catch(() => toast.error("Error recargando inconclusos"));
    } catch (e) { toast.error("Error: " + _parseError(e)); }
  };

  const loadD = async (id) => {
    try {
      const d = await api.get(`/api/v1/evaluations/detail/${id}`);
      d.id = d.evaluation_id || d.id || id;
      setDetail(d);
    } catch { setDetail(null); }
  };

  /* Comparativo longitudinal: extraer índices compuestos por evaluación */
  const longitudinalData = (() => {
    if (allDetails.length < 2) return null;
    const allIndices = new Set();
    allDetails.forEach(d => (d.resultados || []).forEach(r => {
      if (r.test_id && (r.test_id.includes("Ind") || r.test_id.includes("Tot"))) {
        allIndices.add(r.test_nombre.split("—")[0]?.trim() || r.test_id);
      }
    }));
    const series = [...allIndices].map(name => ({
      name,
      points: allDetails.map(d => {
        const match = (d.resultados || []).find(r => r.test_nombre.includes(name));
        return { fecha: d.fecha || "", val: match ? Math.round(match.puntaje_escalar || 0) : null };
      }),
    }));
    return series.filter(s => s.points.some(p => p.val != null));
  })();

  const exportHistorial = () => {
    if (!detail) return;
    const rows = (detail.resultados || []).map(r => ({
      fecha: detail.fecha,
      prueba: r.test_nombre,
      PD: r.puntaje_bruto,
      PE: r.puntaje_escalar,
      Z: r.z_equivalente,
      interpretacion: r.interpretacion,
    }));
    exportCSV(rows, `Historial_${detail.protocolo}_${Date.now()}.csv`);
  };

  return (
    <>
      <TopBar title="Historial de Evaluaciones">
        {incStats && incStats.abiertos > 0 && (
          <span className="text-[11px] font-bold px-3 py-1.5 rounded-full flex items-center gap-1.5"
            style={{
              background: incStats.vencidos > 0 ? "#fee2e2" : "#fef3c7",
              color: incStats.vencidos > 0 ? "#dc2626" : "#b45309",
            }}>
            <I name="flag" fill className="text-sm" />
            {incStats.abiertos} inconclusos{incStats.vencidos > 0 ? ` · ${incStats.vencidos} vencidos` : ""}
          </span>
        )}
        {evals.length > 1 && (
          <button onClick={() => setShowLongitudinal(!showLongitudinal)}
            className="px-4 py-2 rounded-full text-xs font-bold flex items-center gap-1.5 transition-all"
            style={
              showLongitudinal
                ? { background: TEAL, color: "#fff", boxShadow: "0 6px 16px -4px rgba(13,148,136,0.4)" }
                : { background: `${TEAL}15`, color: TEAL, border: `1px solid ${TEAL}40` }
            }
            title={`Comparar las ${evals.length} evaluaciones del paciente`}>
            <I name="compare_arrows" fill={showLongitudinal} className="text-sm" />
            {showLongitudinal ? "Ocultar" : "Comparar Pre–Post"}
            <span className="text-[10px] font-extrabold ml-1 px-1.5 py-0.5 rounded"
              style={{ background: showLongitudinal ? "rgba(255,255,255,0.2)" : TEAL, color: "#fff" }}>
              {evals.length}
            </span>
          </button>
        )}
      </TopBar>

      <main className="p-8 space-y-6">
        <Card className="p-6">
          <div className="flex items-center gap-6">
            <div className="flex-1">
              <PatientSelect
                patients={patients}
                loading={patientsLoading}
                label="Seleccionar Paciente"
                value={patId}
                onChange={(id) => { setPatId(id); loadH(id); }}
                placeholder="— Seleccione —"
              />
            </div>
            {patId && (
              <div className="pt-6">
                <Btn v="outline" onClick={() => loadH(patId)}>
                  <I name="refresh" className="text-sm" />Actualizar
                </Btn>
              </div>
            )}
          </div>
        </Card>

        {/* Informes inconclusos del paciente */}
        {patId && inconclusos.length > 0 && (
          <Card className="p-6" style={{ borderLeft: "4px solid #d97706" }}>
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2" style={{ color: "#b45309" }}>
              <I name="flag" fill />
              Informes Inconclusos ({inconclusos.filter(i => i.estado === "abierto").length} abiertos · {inconclusos.filter(i => i.estado !== "abierto").length} archivados)
            </h3>
            <div className="space-y-2">
              {inconclusos.map(i => {
                const ven = i.dias_restantes != null && i.dias_restantes < 0;
                const color = i.estado !== "abierto" ? "#9ca3af"
                  : ven ? "#dc2626"
                  : i.dias_restantes <= 3 ? "#d97706"
                  : "#6366f1";
                return (
                  <div key={i.id} className="p-3 rounded-xl"
                    style={{
                      background: i.estado !== "abierto" ? "#f3f4f6" : `${color}10`,
                      opacity: i.estado !== "abierto" ? 0.6 : 1,
                    }}>
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full"
                            style={{ background: color + "20", color }}>
                            {i.estado.toUpperCase()}
                          </span>
                          <span className="text-xs font-extrabold">{i.motivo_titulo}</span>
                          {ven && i.estado === "abierto" && (
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-700">VENCIDO</span>
                          )}
                        </div>
                        {i.descripcion && (
                          <p className="text-xs leading-snug mb-1" style={{ color: "var(--ns-muted)" }}>{i.descripcion}</p>
                        )}
                        {i.accion_sugerida && (
                          <p className="text-[10px] leading-snug" style={{ color: "var(--ns-muted)" }}>
                            <strong>Acción:</strong> {i.accion_sugerida}
                          </p>
                        )}
                        <p className="text-[10px] mt-1" style={{ color: "var(--ns-muted)" }}>
                          Creado: {i.fecha_creacion} · Límite: {i.fecha_limite || "—"}
                          {i.dias_restantes != null && i.estado === "abierto"
                            ? ` · ${i.dias_restantes >= 0
                                ? i.dias_restantes + " días restantes"
                                : "Vencido hace " + Math.abs(i.dias_restantes) + " días"}`
                            : ""}
                          {i.resuelto_en ? ` · Resuelto: ${i.resuelto_en}` : ""}
                        </p>
                      </div>
                      {i.estado === "abierto" && (
                        <div className="flex gap-1 shrink-0">
                          <button onClick={() => resolverInc(i.id, "resuelto")}
                            className="text-[10px] font-bold px-2 py-1 rounded"
                            style={{ background: "#059669", color: "#fff" }}
                            title="Marcar como resuelto">
                            <I name="check" className="text-xs" />Resolver
                          </button>
                          <button onClick={() => resolverInc(i.id, "cerrado")}
                            className="text-[10px] font-bold px-2 py-1 rounded bg-gray-300 text-gray-700"
                            title="Cerrar sin resolver">
                            <I name="archive" className="text-xs" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        )}

        {/* Comparativo longitudinal */}
        {showLongitudinal && longitudinalData && longitudinalData.length > 0 && (
          <Card className="p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <I name="timeline" style={{ color: TEAL }} />
              Comparativo Longitudinal — Evolución de Índices
            </h3>
            <p className="text-xs mb-4" style={{ color: "var(--ns-muted)" }}>
              Comparación de puntuaciones compuestas entre las {allDetails.length} evaluaciones del paciente.
              Línea de referencia en PE=100 (promedio).
            </p>
            {(() => {
              const n = allDetails.length;
              const w = 700, h = 240;
              const step = (w - 80) / Math.max(n - 1, 1);
              const colors = [TEAL, "#6366f1", "#f59e0b", "#ec4899", "#10b981", "#e11d48"];
              return (
                <svg viewBox={`0 0 ${w} ${h + 50}`} className="w-full">
                  {[40, 70, 85, 100, 115, 130, 160].map(v => {
                    const y = h - ((v - 40) / 120) * h + 10;
                    return (
                      <g key={v}>
                        <line x1="40" y1={y} x2={w - 20} y2={y}
                          stroke="var(--ns-card-b)" strokeWidth="0.5"
                          strokeDasharray={v === 100 ? "" : "2 3"} />
                        <text x="35" y={y + 3} textAnchor="end" fontSize="9" fill="var(--ns-muted)">{v}</text>
                      </g>
                    );
                  })}
                  <line x1="40" y1={h - (60 / 120) * h + 10}
                    x2={w - 20} y2={h - (60 / 120) * h + 10}
                    stroke={TEAL} strokeWidth="1" strokeDasharray="4 4" strokeOpacity="0.5" />
                  {longitudinalData.map((s, si) => {
                    const pts = s.points.map((p, i) => ({
                      x: 40 + i * step,
                      y: p.val != null ? h - ((p.val - 40) / 120) * h + 10 : null,
                      val: p.val,
                    }));
                    const valid = pts.filter(p => p.y != null);
                    if (valid.length === 0) return null;
                    return (
                      <g key={si}>
                        <polyline fill="none" stroke={colors[si % colors.length]}
                          strokeWidth="2" strokeLinejoin="round"
                          points={valid.map(p => `${p.x},${p.y}`).join(" ")} />
                        {pts.map((p, i) => p.y != null ? (
                          <g key={i}>
                            <circle cx={p.x} cy={p.y} r="4"
                              fill={colors[si % colors.length]} stroke="#fff" strokeWidth="1.5" />
                            <text x={p.x} y={p.y - 8} textAnchor="middle"
                              fontSize="9" fontWeight="bold" fill={colors[si % colors.length]}>
                              {p.val}
                            </text>
                          </g>
                        ) : null)}
                      </g>
                    );
                  })}
                  {allDetails.map((d, i) => (
                    <text key={i} x={40 + i * step} y={h + 35}
                      textAnchor="middle" fontSize="9" fill="var(--ns-muted)">
                      {d.fecha || `Eval ${i + 1}`}
                    </text>
                  ))}
                </svg>
              );
            })()}
            <div className="flex flex-wrap gap-2 mt-4">
              {longitudinalData.map((s, i) => {
                const colors = [TEAL, "#6366f1", "#f59e0b", "#ec4899", "#10b981", "#e11d48"];
                return (
                  <div key={i} className="flex items-center gap-1.5 text-xs">
                    <span className="w-3 h-3 rounded-full" style={{ background: colors[i % colors.length] }} />
                    <span className="font-bold">{s.name}</span>
                  </div>
                );
              })}
            </div>
          </Card>
        )}

        {!patId ? (
          <div className="flex flex-col items-center py-20" style={{ color: "var(--ns-muted)" }}>
            <I name="history" className="text-6xl mb-4 opacity-30" />
            <p className="font-bold text-lg">Selecciona un paciente</p>
          </div>
        ) : ld ? (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        ) : (
          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-12 lg:col-span-5 space-y-3">
              <h3 className="text-lg font-bold px-1">Evaluaciones ({evals.length})</h3>
              {evals.length === 0 ? (
                <Card className="p-8 text-center text-gray-400">
                  <I name="assignment" className="text-4xl mb-3" />
                  <p className="font-bold">Sin evaluaciones</p>
                </Card>
              ) : (
                evals.map((ev, i) => {
                  const eid = ev.evaluation_id || ev.id;
                  return (
                    <button key={eid || i} onClick={() => loadD(eid)}
                      className={`w-full text-left ${detail?.id === eid ? "ring-2 ring-teal-600/30" : ""}`}>
                      <Card className={`p-5 hover:shadow-lg transition-all ${detail?.id === eid ? "bg-teal-50/50" : ""}`}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-bold text-teal-600">{ev.protocolo || "Evaluación"}</span>
                          <span className="text-[10px] text-gray-400">{ev.fecha || ""}</span>
                        </div>
                        <p className="text-xs text-gray-500">
                          {ev.pruebas_realizadas || 0} pruebas • {ev.edad_display || ""}
                        </p>
                      </Card>
                    </button>
                  );
                })
              )}
            </div>
            <div className="col-span-12 lg:col-span-7">
              {!detail ? (
                <Card className="p-12 text-center text-gray-400 min-h-[400px] flex flex-col items-center justify-center">
                  <I name="touch_app" className="text-5xl mb-4 opacity-30" />
                  <p className="font-bold text-lg">Selecciona una evaluación</p>
                </Card>
              ) : (
                <div className="space-y-4 sticky top-24">
                  <Card className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold">{detail.protocolo || "Evaluación"}</h3>
                      <div className="flex gap-2">
                        <Btn v="outline" className="text-xs" onClick={exportHistorial}>
                          <I name="download" className="text-sm" />CSV
                        </Btn>
                        <Btn v="outline" className="text-xs" onClick={() => setPage("reports")}>
                          <I name="picture_as_pdf" className="text-sm" />PDF
                        </Btn>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400 text-xs font-bold uppercase">Fecha</span>
                        <p className="font-bold">{detail.fecha || "—"}</p>
                      </div>
                      <div>
                        <span className="text-gray-400 text-xs font-bold uppercase">Pruebas</span>
                        <p className="font-bold">{detail.pruebas_realizadas || 0}</p>
                      </div>
                      <div>
                        <span className="text-gray-400 text-xs font-bold uppercase">Población</span>
                        <p className="font-bold capitalize">{(detail.poblacion || "").replace("_", " ")}</p>
                      </div>
                    </div>
                  </Card>
                  {detail.resultados && detail.resultados.length > 0 && (
                    <Card className="overflow-hidden">
                      <table className="w-full text-sm">
                        <thead style={{ background: "var(--ns-subtle)" }}>{/* §dark-mode-fix */}
                          <tr>
                            <th className="px-5 py-3 text-left font-bold text-xs uppercase">Prueba</th>
                            <th className="px-3 py-3 text-center font-bold text-xs uppercase">PD</th>
                            <th className="px-3 py-3 text-center font-bold text-xs uppercase">Escalar</th>
                            <th className="px-3 py-3 text-left font-bold text-xs uppercase">Nivel</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(detail.resultados || []).map((r, i) => (
                            <tr key={i} className={i % 2 ? "bg-gray-50/30" : ""}>
                              <td className="px-5 py-3 font-semibold">{r.test_nombre || r.test_id}</td>
                              <td className="px-3 py-3 text-center">
                                {r.puntaje_bruto != null ? Math.round(r.puntaje_bruto) : "—"}
                              </td>
                              <td className="px-3 py-3 text-center font-bold"
                                style={{ color: lc(r.interpretacion) }}>
                                {r.puntaje_escalar != null ? Math.round(r.puntaje_escalar) : "—"}
                              </td>
                              <td className="px-3 py-3">
                                <span className="px-2 py-0.5 text-[10px] font-bold rounded"
                                  style={{
                                    background: `${lc(r.interpretacion)}15`,
                                    color: lc(r.interpretacion),
                                  }}>
                                  {(r.interpretacion || "").toUpperCase()}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </Card>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </>
  );
}
