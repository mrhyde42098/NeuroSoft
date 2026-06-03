/* ═══════════════════════════════════════════════════════════════════════
 * src/app/dashboard/DashboardPage.jsx — Página de inicio (post-login)
 * ───────────────────────────────────────────────────────────────────────
 * Muestra:
 *   - 4 KPIs (pacientes, evaluaciones, este mes, este año)
 *   - Tendencia de evaluaciones (real, GET /api/v1/evaluations/trend?meses=6)
 *   - Distribución por sexo
 *   - Adherencia agregada de planes de rehabilitación (top-5 + promedio)
 *   - Acciones rápidas
 *   - Distribución por grupo poblacional
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api } from "../../api/client.js";
import { useAuth, useToast } from "../../contexts.jsx";
import { I, TopBar } from "../../ui/primitives.jsx";
import { TEAL, NAVY } from "../../ui/tokens.js";
import NotificationsWidget from "./NotificationsWidget.jsx";
import { SkeletonKpi } from "../../ui/Skeleton.jsx";

export default function DashboardPage({ setPage }) {
  const { user } = useAuth();
  const toast = useToast();
  const [stats, setStats] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [rehabSummary, setRehabSummary] = useState(null);

  useEffect(() => {
    api.get("/api/v1/patients/stats").then(setStats).catch(() => toast.error("Error cargando estadísticas"));
    /* Tendencia real (6 meses) servida por /api/v1/evaluations/trend.
     * Si el endpoint falla por cualquier motivo, dejamos la lista vacía
     * y el chart simplemente no se dibuja (mejor que mostrar mock). */
    api.get("/api/v1/evaluations/trend?meses=6")
      .then((rows) => setTrendData(rows || []))
      .catch(() => setTrendData([]));
    /* Resumen de rehabilitación: top 5 pacientes con plan activo + adherencia promedio */
    api.get("/api/v1/patients/panel?por_pagina=50").then(async (d) => {
      const pacs = (d.pacientes || []).slice(0, 20);
      /* §A3-fix: en vez de buscar el paciente por adheres.indexOf(a) — que
       * es frágil si alguien clona los objetos en un .map() intermedio —
       * preservamos el id del paciente desde el primer paso y indexamos
       * por id explícito. Sobrevive a cualquier refactor futuro. */
      const adheres = await Promise.all(pacs.map(async p => {
        const a = await api.get(`/api/v1/rehab/adherence/${p.id}`).catch(() => null);
        return a ? { ...a, _patient_id: p.id, _paciente: p.nombre_completo } : null;
      }));
      const conPlan = adheres.filter(a => a && a.has_plan);
      if (conPlan.length === 0) {
        setRehabSummary({ total: 0, promedio: 0, activos: [] });
        return;
      }
      const promedio = Math.round(conPlan.reduce((s, a) => s + a.adherencia_pct, 0) / conPlan.length);
      const activos = conPlan
        .map((a) => ({ ...a, paciente: a._paciente || "—" }))
        .sort((a, b) => b.adherencia_pct - a.adherencia_pct)
        .slice(0, 5);
      setRehabSummary({ total: conPlan.length, promedio, activos });
    }).catch(() => setRehabSummary({ total: 0, promedio: 0, activos: [] }));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const total = stats?.total_pacientes || 0;
  const pctM = total ? Math.round((stats.masculino / total) * 100) : 0;
  const pctF = total ? 100 - pctM : 0;
  const hora = new Date().getHours();
  const saludo = hora < 12 ? "Buenos días" : hora < 18 ? "Buenas tardes" : "Buenas noches";
  const ageGroups = [
    { l: "Niños (6-16)", v: stats?.ninos || 0,         c: "#6366f1" },
    { l: "Adulto Joven", v: stats?.adulto_joven || 0,  c: TEAL },
    { l: "Adulto Mayor", v: stats?.adulto_mayor || 0,  c: "#e67e22" },
  ];
  const maxTrend = Math.max(...trendData.map(t => t.val), 10);

  return (
    <>
      <TopBar title={`${saludo}, ${user?.nombre_completo?.split(" ")[0] || "Doctor"}`} />
      <main className="p-6 lg:p-8 space-y-7 max-w-7xl mx-auto" style={{ background: "var(--ns-bg)", minHeight: "100vh" }}>
        {/* Hero: bienvenida + descripción del software */}
        <div className="rounded-xl p-6 border" style={{ background: `linear-gradient(135deg, ${NAVY}08, ${TEAL}08)`, borderColor: `${TEAL}25` }}>
          <div className="flex flex-col md:flex-row md:items-center gap-4">
            <div className="flex-1">
              <p className="ns-eyebrow mb-1" style={{ color: TEAL }}>Plataforma de evaluación neuropsicológica</p>
              <h2 className="ns-serif text-2xl font-bold" style={{ color: "var(--ns-text)" }}>
                {saludo}, <span className="ns-serif-italic" style={{ color: TEAL }}>{user?.nombre_completo?.split(" ")[0] || "Doctor"}</span>
              </h2>
              <p className="text-sm mt-1 max-w-2xl" style={{ color: "var(--ns-muted)" }}>
                {new Date().toLocaleDateString("es-CO", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
              </p>
            </div>
            {/* Resumen de módulos disponibles */}
            <div className="flex flex-wrap gap-2 md:gap-3">
              {[
                { icon: "person", label: "Pacientes" },
                { icon: "clinical_notes", label: "Evaluaciones" },
                { icon: "checklist", label: "Screening" },
                { icon: "fitness_center", label: "Rehabilitación" },
                { icon: "psychology", label: "Terapia" },
              ].map((m) => (
                <div key={m.label} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-semibold"
                  style={{ background: "var(--ns-card)", color: "var(--ns-muted)", border: "1px solid var(--ns-card-b)" }}>
                  <I name={m.icon} className="text-sm" style={{ color: TEAL }} />{m.label}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Widget de notificaciones telerehab */}
        <NotificationsWidget />

        {/* §editorial: KPIs estilo periódico — números grandes serif + label tracking + barra acento */}
        <div>
          <p className="ns-eyebrow mb-3">Indicadores</p>
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            {!stats ? (
              Array.from({ length: 5 }).map((_, i) => <SkeletonKpi key={i} />)
            ) : (
              [
                { l: "Pacientes",    v: stats.total_pacientes      ?? 0, i: "group",            c: NAVY,      action: () => setPage("patients") },
                { l: "Evaluaciones", v: stats.total_evaluaciones   ?? 0, i: "clinical_notes",   c: TEAL,      action: null },
                { l: "Sin informe",  v: stats.evaluaciones_sin_informe ?? 0, i: "description", c: "#dc2626",  action: () => setPage("reports"), warn: (stats.evaluaciones_sin_informe ?? 0) > 0 },
                { l: "Este mes",     v: stats.atendidos_este_mes   ?? 0, i: "event_available",  c: "#6366f1", action: null },
                { l: "Este año",     v: stats.atendidos_este_anio  ?? 0, i: "calendar_month",   c: "#B45309", action: null },
              ].map((s, i) => (
                <div key={i}
                  onClick={s.action || undefined}
                  className={`p-5 rounded-md border transition-all ${s.action ? "cursor-pointer hover:shadow-sm" : ""}`}
                  style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)", borderLeftWidth: 3, borderLeftColor: s.c }}>
                  <div className="flex items-start justify-between mb-3">
                    <I name={s.i} className="text-lg opacity-60" style={{ color: s.c }} />
                    {s.action && <I name="arrow_outward" className="text-sm opacity-30" />}
                  </div>
                  <p className={`ns-serif text-4xl font-bold tabular-nums leading-none ${s.warn?"":"mb-0"}`} style={{ color: s.warn ? s.c : "var(--ns-text)" }}>{s.v}</p>
                  {s.warn && <p className="text-[10px] font-bold mt-0.5" style={{color: s.c}}>Pendientes</p>}
                  <p className="ns-eyebrow mt-2">{s.l}</p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* §editorial: Analytics: trend + sex pie */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="p-6 lg:col-span-2 rounded-md border"
            style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
            <div className="mb-4">
              <p className="ns-eyebrow" style={{ color: TEAL }}>Tendencia</p>
              <h3 className="ns-serif text-lg font-bold mt-1" style={{ color: "var(--ns-text)" }}>
                Evaluaciones aplicadas <span className="ns-serif-italic font-normal opacity-60">(últimos 6 meses)</span>
              </h3>
            </div>
            {!stats && <div className="ns-skeleton h-40 rounded-xl" style={{background:"var(--ns-subtle)"}}/>}
            {/* §H2-fix: con 1 sola entrada, la fórmula `540/(length-1)` daría Infinity y rompía el SVG.
              * Pedimos ≥ 2 puntos para dibujar la línea. */}
            {stats && trendData.length === 1 && (
              <div className="h-40 rounded-xl flex items-center justify-center text-xs"
                style={{background:"var(--ns-subtle)",color:"var(--ns-muted)"}}>
                <span>{trendData[0].mes}: <strong style={{color:"var(--ns-text)"}}>{trendData[0].val}</strong> evaluación{trendData[0].val!==1?"es":""} · necesita ≥2 meses para mostrar tendencia</span>
              </div>
            )}
            {stats && trendData.length >= 2 && (
              <svg viewBox="0 0 600 180" className="w-full h-40">
                <defs>
                  <linearGradient id="tg" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%"   stopColor={TEAL} stopOpacity="0.4" />
                    <stop offset="100%" stopColor={TEAL} stopOpacity="0" />
                  </linearGradient>
                </defs>
                {[0, 0.25, 0.5, 0.75, 1].map(f => (
                  <line key={f} x1="30" y1={20 + f * 140} x2="570" y2={20 + f * 140}
                    stroke="var(--ns-card-b)" strokeWidth="0.5" />
                ))}
                {[0, 0.25, 0.5, 0.75, 1].map(f => (
                  <text key={f} x="20" y={24 + f * 140} textAnchor="end" fontSize="9" fill="var(--ns-muted)">
                    {Math.round(maxTrend * (1 - f))}
                  </text>
                ))}
                <polygon
                  points={`30,160 ${trendData.map((t, i) =>
                    `${30 + i * (540 / (trendData.length - 1))},${20 + (1 - t.val / maxTrend) * 140}`
                  ).join(" ")} 570,160`}
                  fill="url(#tg)"
                />
                <polyline fill="none" stroke={TEAL} strokeWidth="2.5"
                  points={trendData.map((t, i) =>
                    `${30 + i * (540 / (trendData.length - 1))},${20 + (1 - t.val / maxTrend) * 140}`
                  ).join(" ")}
                />
                {trendData.map((t, i) => {
                  const x = 30 + i * (540 / (trendData.length - 1));
                  const y = 20 + (1 - t.val / maxTrend) * 140;
                  return (
                    <g key={i}>
                      <circle cx={x} cy={y} r="4" fill={TEAL} />
                      <text x={x} y={y - 10} fontSize="10" textAnchor="middle"
                        fontWeight="bold" fill="var(--ns-text)">{t.val}</text>
                      <text x={x} y="175" fontSize="9" textAnchor="middle" fill="var(--ns-muted)">{t.mes}</text>
                    </g>
                  );
                })}
              </svg>
            )}
          </div>
          <div className="p-6 rounded-md border"
            style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
            <div className="mb-4">
              <p className="ns-eyebrow" style={{ color: TEAL }}>Demografía</p>
              <h3 className="ns-serif text-lg font-bold mt-1" style={{ color: "var(--ns-text)" }}>
                Distribución por sexo
              </h3>
            </div>
            {!stats && <div className="ns-skeleton h-40 rounded-xl" style={{background:"var(--ns-subtle)"}}/>}
            {stats && (total > 0 ? (
              <>
                <div className="flex items-center justify-center my-3">
                  <svg width="140" height="140" viewBox="0 0 140 140">
                    <circle cx="70" cy="70" r="55" fill="none" stroke="var(--ns-subtle)" strokeWidth="18" />
                    <circle cx="70" cy="70" r="55" fill="none" stroke={NAVY} strokeWidth="18"
                      strokeDasharray={`${(pctM / 100) * 345.5} 345.5`}
                      transform="rotate(-90 70 70)" strokeLinecap="round" />
                    <text x="70" y="68" textAnchor="middle" fontSize="24"
                      fontWeight="800" fill="var(--ns-text)">{total}</text>
                    <text x="70" y="84" textAnchor="middle" fontSize="10" fill="var(--ns-muted)">Total</text>
                  </svg>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full" style={{ background: NAVY }} />
                    <span className="flex-1">Masculino</span>
                    <span className="font-bold">{stats?.masculino || 0} ({pctM}%)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full" style={{ background: TEAL }} />
                    <span className="flex-1">Femenino</span>
                    <span className="font-bold">{stats?.femenino || 0} ({pctF}%)</span>
                  </div>
                </div>
              </>
            ) : (
              <p className="text-center text-xs py-12" style={{ color: "var(--ns-muted)" }}>Sin datos</p>
            ))}
          </div>
        </div>

        {/* §editorial: Adherencia Rehab */}
        {rehabSummary && rehabSummary.total > 0 && (
          <div className="p-6 rounded-md border"
            style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
            <div className="flex items-center justify-between mb-5">
              <div>
                <p className="ns-eyebrow" style={{ color: TEAL }}>Rehabilitación</p>
                <h3 className="ns-serif text-lg font-bold mt-1" style={{ color: "var(--ns-text)" }}>
                  Adherencia a planes <span className="ns-serif-italic font-normal opacity-60">activos</span>
                </h3>
              </div>
              <button onClick={() => setPage("rehab")}
                className="text-xs font-semibold flex items-center gap-1 hover:underline"
                style={{ color: TEAL }}>
                Ver detalle<I name="arrow_forward" className="text-sm" />
              </button>
            </div>
            <div className="grid grid-cols-3 gap-4 mb-5">
              <div>
                <p className="ns-serif text-3xl font-bold tabular-nums" style={{ color: TEAL }}>{rehabSummary.promedio}%</p>
                <p className="ns-eyebrow mt-2">Promedio global</p>
              </div>
              <div>
                <p className="ns-serif text-3xl font-bold tabular-nums" style={{ color: "var(--ns-text)" }}>{rehabSummary.total}</p>
                <p className="ns-eyebrow mt-2">Pacientes activos</p>
              </div>
              <div>
                <p className="ns-serif text-3xl font-bold"
                  style={{ color: rehabSummary.promedio >= 70 ? "#10b981" : rehabSummary.promedio >= 40 ? "#B45309" : "#dc2626" }}>
                  {rehabSummary.promedio >= 70 ? "Alta" : rehabSummary.promedio >= 40 ? "Media" : "Baja"}
                </p>
                <p className="ns-eyebrow mt-2">Adherencia general</p>
              </div>
            </div>
            <div className="space-y-2">
              {rehabSummary.activos.map((a, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-xs font-semibold flex-1 truncate" style={{ color: "var(--ns-text)" }}>{a.paciente}</span>
                  <div className="w-32 h-1.5 rounded-full" style={{ background: "var(--ns-subtle)" }}>
                    <div className="h-1.5 rounded-full"
                      style={{
                        width: `${Math.min(100, a.adherencia_pct)}%`,
                        background: a.adherencia_pct >= 70 ? "#10b981" : a.adherencia_pct >= 40 ? "#B45309" : "#dc2626",
                      }} />
                  </div>
                  <span className="ns-serif text-sm font-bold tabular-nums w-10 text-right"
                    style={{ color: a.adherencia_pct >= 70 ? "#10b981" : a.adherencia_pct >= 40 ? "#B45309" : "#dc2626" }}>
                    {a.adherencia_pct}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Módulos principales — descripción breve de cada sección */}
        <div>
          <p className="ns-eyebrow mb-3">Módulos</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {[
              {
                l: "Pacientes",
                sub: "Registra y gestiona historias clínicas",
                i: "person",
                p: "patients",
                primary: true,
              },
              {
                l: "Evaluación neuropsicológica",
                sub: "Aplica baterías WISC-IV, WAIS-III y más de 50 pruebas",
                i: "clinical_notes",
                p: "evaluation",
                primary: true,
              },
              {
                l: "Screening",
                sub: "PHQ-9, GAD-7, MMSE, MoCA, SNAP-IV y otras escalas",
                i: "checklist",
                p: "screening",
                primary: false,
              },
              {
                l: "Rehabilitación cognitiva",
                sub: "Planes de ejercicios y seguimiento de adherencia",
                i: "fitness_center",
                p: "rehab",
                primary: false,
              },
              {
                l: "Terapia",
                sub: "Sesiones SOAP, enfoques CBT / ACT / EMDR y más",
                i: "psychology",
                p: "therapy",
                primary: false,
              },
              {
                l: "Agenda",
                sub: "Citas, recordatorios y gestión de horarios",
                i: "calendar_today",
                p: "agenda",
                primary: false,
              },
            ].map((a) => (
              <button key={a.l} onClick={() => setPage(a.p)}
                className="flex items-start gap-3 p-4 rounded-md border text-left transition-all hover:shadow-sm hover:-translate-y-px"
                style={{
                  background: a.primary ? `${TEAL}08` : "var(--ns-card)",
                  borderColor: a.primary ? `${TEAL}40` : "var(--ns-card-b)",
                }}>
                <div className="w-9 h-9 rounded-md flex items-center justify-center shrink-0 mt-0.5"
                  style={{ background: `${TEAL}15`, color: TEAL }}>
                  <I name={a.i} className="text-xl" />
                </div>
                <div>
                  <p className="text-sm font-bold leading-tight" style={{ color: "var(--ns-text)" }}>{a.l}</p>
                  <p className="text-[11px] mt-0.5 leading-snug" style={{ color: "var(--ns-muted)" }}>{a.sub}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* §editorial: Grupo poblacional */}
        {ageGroups.some(g => g.v > 0) && (
          <div className="p-6 rounded-md border"
            style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
            <div className="mb-5">
              <p className="ns-eyebrow" style={{ color: TEAL }}>Población atendida</p>
              <h3 className="ns-serif text-lg font-bold mt-1" style={{ color: "var(--ns-text)" }}>
                Distribución por grupo etario
              </h3>
            </div>
            <div className="grid grid-cols-3 gap-6">
              {ageGroups.map((g, i) => {
                const pct = total ? Math.round((g.v / total) * 100) : 0;
                return (
                  <div key={i} className="space-y-2">
                    <div className="flex items-end justify-between">
                      <div>
                        <p className="ns-serif text-2xl font-bold tabular-nums leading-none" style={{ color: "var(--ns-text)" }}>{g.v}</p>
                        <p className="text-[10px] font-semibold uppercase tracking-wider mt-1" style={{ color: g.c }}>{g.l}</p>
                      </div>
                      <span className="ns-serif-italic text-sm opacity-60">{pct}%</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full" style={{ background: "var(--ns-subtle)" }}>
                      <div className="h-1.5 rounded-full" style={{ width: `${pct}%`, background: g.c }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </main>
    </>
  );
}
