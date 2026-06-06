/* Estadísticas clínicas y operativas — selector por categoría */
import React, { useEffect, useMemo, useState } from "react";
import { api } from "../../api/client.js";
import { useToast } from "../../contexts.jsx";
import { I, TopBar } from "../../ui/primitives.jsx";
import SectionCard from "../../ui/SectionCard.jsx";
import { TEAL, NAVY } from "../../ui/tokens.js";
import { SkeletonKpi } from "../../ui/Skeleton.jsx";

const CATEGORIES = [
  { id: "resumen", label: "Resumen", icon: "dashboard", desc: "Indicadores principales de la práctica" },
  { id: "tendencia", label: "Tendencia", icon: "trending_up", desc: "Volumen de evaluaciones en el tiempo" },
  { id: "demografia", label: "Demografía", icon: "wc", desc: "Sexo, edad y perfil de pacientes" },
  { id: "operativo", label: "Operativo", icon: "calendar_month", desc: "Agenda, informes e inconclusos" },
  { id: "rehab", label: "Rehabilitación", icon: "fitness_center", desc: "Adherencia a planes cognitivos" },
  { id: "clinico", label: "Clínico", icon: "psychology", desc: "Actividad evaluativa y productividad" },
];

function KpiCard({ label, value, sub, color = TEAL, icon }) {
  return (
    <div className="rounded-2xl p-5 border" style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
      <div className="flex items-start justify-between gap-2">
        <p className="text-[10px] font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>{label}</p>
        {icon && <I name={icon} className="text-lg" style={{ color }} />}
      </div>
      <p className="text-3xl font-extrabold mt-2 tabular-nums ns-serif" style={{ color }}>{value ?? "—"}</p>
      {sub && <p className="text-xs mt-1" style={{ color: "var(--ns-muted)" }}>{sub}</p>}
    </div>
  );
}

function BarRow({ label, value, max, color }) {
  const pct = max ? Math.round((value / max) * 100) : 0;
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span style={{ color: "var(--ns-text)" }}>{label}</span>
        <span className="font-bold tabular-nums" style={{ color }}>{value}</span>
      </div>
      <div className="h-2 rounded-full overflow-hidden" style={{ background: "var(--ns-subtle)" }}>
        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

export default function EstadisticasPage() {
  const toast = useToast();
  const [cat, setCat] = useState("resumen");
  const [stats, setStats] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [agenda, setAgenda] = useState(null);
  const [inconclusos, setInconclusos] = useState(null);
  const [adherence, setAdherence] = useState(null);
  const [ld, setLd] = useState(true);

  useEffect(() => {
    setLd(true);
    Promise.all([
      api.get("/api/v1/patients/stats").catch(() => null),
      api.get("/api/v1/evaluations/trend?meses=12").catch(() => []),
      api.get("/api/v1/agenda/stats").catch(() => null),
      api.get("/api/v1/inconclusos/stats").catch(() => null),
      api.get("/api/v1/notifications/adherence/summary?dias=30").catch(() => null),
    ]).then(([s, t, a, inc, adh]) => {
      setStats(s);
      setTrendData(t || []);
      setAgenda(a);
      setInconclusos(inc);
      setAdherence(adh);
      if (!s) toast.error("No se pudieron cargar todas las estadísticas");
    }).finally(() => setLd(false));
  }, [toast]);

  const total = stats?.total_pacientes || 0;
  const pctM = total ? Math.round((stats.masculino / total) * 100) : 0;
  const maxTrend = Math.max(...trendData.map((t) => t.val), 1);
  const ageGroups = useMemo(() => [
    { l: "Infantil / adolescente (<18)", v: stats?.infantil || 0, c: "#6366f1" },
    { l: "Adulto joven (18-49)", v: stats?.adulto_joven || 0, c: TEAL },
    { l: "Adulto mayor (≥50)", v: stats?.adulto_mayor || 0, c: "#e67e22" },
  ], [stats]);

  const activeCat = CATEGORIES.find((c) => c.id === cat);

  return (
    <>
      <TopBar title="Estadísticas" subtitle="Indicadores clínicos y operativos de su consulta" />
      <main className="p-6 lg:p-8 space-y-6 max-w-7xl mx-auto" style={{ background: "var(--ns-bg)", minHeight: "100vh" }}>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => setCat(c.id)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-full text-xs font-bold border transition-all"
              style={cat === c.id
                ? { background: TEAL, color: "#fff", borderColor: TEAL }
                : { background: "var(--ns-card)", color: "var(--ns-muted)", borderColor: "var(--ns-card-b)" }}
              title={c.desc}
            >
              <I name={c.icon} className="text-sm" />
              {c.label}
            </button>
          ))}
        </div>

        {activeCat && (
          <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
            <I name={activeCat.icon} className="text-base align-middle mr-1" style={{ color: TEAL }} />
            {activeCat.desc}
          </p>
        )}

        {ld && <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">{Array.from({ length: 4 }).map((_, i) => <SkeletonKpi key={i} />)}</div>}

        {!ld && cat === "resumen" && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <KpiCard label="Pacientes activos" value={stats?.total_pacientes} sub={`${stats?.atendidos_este_mes ?? 0} atendidos este mes`} icon="group" />
            <KpiCard label="Evaluaciones totales" value={stats?.total_evaluaciones} sub={`${stats?.evaluaciones_sin_informe ?? 0} sin informe PDF`} color="#6366f1" icon="psychology" />
            <KpiCard label="Citas hoy" value={agenda?.hoy} sub={`${agenda?.pendientes ?? 0} pendientes en agenda`} color="#0ea5e9" icon="calendar_today" />
            <KpiCard label="Informes inconclusos" value={inconclusos?.abiertos ?? inconclusos?.total} sub={inconclusos?.vencidos ? `${inconclusos.vencidos} vencidos` : "Flujo de cierre"} color="#f59e0b" icon="pending_actions" />
          </div>
        )}

        {!ld && cat === "tendencia" && (
          <SectionCard eyebrow="Serie temporal" title="Evaluaciones aplicadas" subtitle="Últimos 12 meses" icon="show_chart">
            {trendData.length < 2 ? (
              <p className="text-sm py-8 text-center" style={{ color: "var(--ns-muted)" }}>
                Se necesitan al menos dos meses con evaluaciones para visualizar la tendencia.
              </p>
            ) : (
              <>
                <svg viewBox="0 0 600 200" className="w-full h-48">
                  <defs>
                    <linearGradient id="tg-est2" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor={TEAL} stopOpacity="0.35" />
                      <stop offset="100%" stopColor={TEAL} stopOpacity="0" />
                    </linearGradient>
                  </defs>
                  <polygon
                    points={`40,170 ${trendData.map((t, i) =>
                      `${40 + i * (520 / Math.max(trendData.length - 1, 1))},${24 + (1 - t.val / maxTrend) * 140}`
                    ).join(" ")} 560,170`}
                    fill="url(#tg-est2)"
                  />
                  <polyline fill="none" stroke={TEAL} strokeWidth="2.5"
                    points={trendData.map((t, i) =>
                      `${40 + i * (520 / Math.max(trendData.length - 1, 1))},${24 + (1 - t.val / maxTrend) * 140}`
                    ).join(" ")}
                  />
                </svg>
                <div className="flex flex-wrap gap-2 mt-2 justify-center">
                  {trendData.map((t) => (
                    <span key={t.ym} className="text-[10px] px-2 py-1 rounded-full font-bold"
                      style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
                      {t.mes}: {t.val}
                    </span>
                  ))}
                </div>
              </>
            )}
          </SectionCard>
        )}

        {!ld && cat === "demografia" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <SectionCard eyebrow="Sexo" title="Distribución por sexo" icon="wc">
              {total > 0 ? (
                <>
                  <div className="flex justify-center my-4">
                    <svg width="140" height="140" viewBox="0 0 140 140">
                      <circle cx="70" cy="70" r="55" fill="none" stroke="var(--ns-subtle)" strokeWidth="18" />
                      <circle cx="70" cy="70" r="55" fill="none" stroke={NAVY} strokeWidth="18"
                        strokeDasharray={`${(pctM / 100) * 345.5} 345.5`} transform="rotate(-90 70 70)" />
                      <text x="70" y="75" textAnchor="middle" fontSize="22" fontWeight="800" fill="var(--ns-text)">{total}</text>
                    </svg>
                  </div>
                  <div className="space-y-2 text-sm">
                    <BarRow label="Masculino" value={stats.masculino} max={total} color={NAVY} />
                    <BarRow label="Femenino" value={stats.femenino} max={total} color="#ec4899" />
                  </div>
                </>
              ) : <p className="text-sm text-center py-6" style={{ color: "var(--ns-muted)" }}>Sin pacientes registrados.</p>}
            </SectionCard>
            <SectionCard eyebrow="Edad" title="Grupos etarios" icon="groups">
              <div className="space-y-4 mt-2">
                {ageGroups.map((g) => (
                  <BarRow key={g.l} label={g.l} value={g.v} max={total || 1} color={g.c} />
                ))}
              </div>
              <p className="text-[10px] mt-4" style={{ color: "var(--ns-muted)" }}>
                Los grupos se calculan desde la fecha de nacimiento registrada en cada ficha.
              </p>
            </SectionCard>
          </div>
        )}

        {!ld && cat === "operativo" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <SectionCard eyebrow="Agenda" title="Citas y seguimiento" icon="event">
              <div className="grid grid-cols-2 gap-3 mt-2">
                <KpiCard label="Hoy" value={agenda?.hoy} color={TEAL} />
                <KpiCard label="Esta semana" value={agenda?.esta_semana} color="#0ea5e9" />
                <KpiCard label="Pendientes" value={agenda?.pendientes} color="#f59e0b" />
                <KpiCard label="Atendidas (mes)" value={agenda?.atendidas_mes} color="#10b981" />
              </div>
            </SectionCard>
            <SectionCard eyebrow="Calidad documental" title="Informes e inconclusos" icon="description">
              <div className="space-y-3 mt-2">
                <BarRow label="Evaluaciones sin informe" value={stats?.evaluaciones_sin_informe ?? 0} max={stats?.total_evaluaciones || 1} color="#dc2626" />
                <BarRow label="Inconclusos abiertos" value={inconclusos?.abiertos ?? 0} max={inconclusos?.total || 1} color="#f59e0b" />
                <BarRow label="Inconclusos resueltos" value={inconclusos?.resueltos ?? 0} max={inconclusos?.total || 1} color={TEAL} />
                <BarRow label="Atendidos este año" value={stats?.atendidos_este_anio ?? 0} max={stats?.total_pacientes || 1} color="#6366f1" />
              </div>
            </SectionCard>
          </div>
        )}

        {!ld && cat === "rehab" && (
          <SectionCard eyebrow="Rehab cognitiva" title="Adherencia a planes (30 días)" icon="fitness_center">
            {adherence?.total_pacientes > 0 ? (
              <>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-2">
                  <KpiCard label="Pacientes con plan" value={adherence.total_pacientes} color={TEAL} />
                  <KpiCard label="Adherencia media" value={`${adherence.promedio_adherencia}%`} color="#10b981" />
                  <KpiCard label="Periodo" value={`${adherence.periodo_dias} días`} color="#0ea5e9" />
                </div>
                <div className="mt-4 space-y-2">
                  {(adherence.pacientes || []).slice(0, 8).map((p) => (
                    <div key={p.plan_id} className="flex items-center gap-3 text-sm">
                      <span className="flex-1 truncate">{p.paciente_nombre}</span>
                      <span className="text-xs tabular-nums" style={{ color: "var(--ns-muted)" }}>{p.sesiones}/{Math.round(p.esperadas)} ses.</span>
                      <span className="font-bold tabular-nums">{p.adherencia_pct}%</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="text-sm py-6 text-center" style={{ color: "var(--ns-muted)" }}>
                Sin planes de rehabilitación activos o datos de adherencia en el período.
              </p>
            )}
          </SectionCard>
        )}

        {!ld && cat === "clinico" && (
          <div className="space-y-5">
            <SectionCard eyebrow="Productividad" title="Actividad evaluativa" icon="clinical_notes">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <KpiCard label="Evaluaciones totales" value={stats?.total_evaluaciones} icon="psychology" />
                <KpiCard label="Atendidos este mes" value={stats?.atendidos_este_mes} color="#6366f1" icon="today" />
                <KpiCard label="Atendidos este año" value={stats?.atendidos_este_anio} color={TEAL} icon="date_range" />
              </div>
            </SectionCard>
            <SectionCard eyebrow="Próximamente" title="Métricas clínicas avanzadas" icon="insights" collapsible defaultOpen={false}>
              <ul className="text-xs space-y-2 list-disc pl-5" style={{ color: "var(--ns-muted)" }}>
                <li>Frecuencia de dominios débiles agregados (memoria, atención, FE) desde resultados_json</li>
                <li>Mix de protocolos (WISC-IV, WAIS-III, adulto mayor) por período</li>
                <li>Distribución de diagnósticos CIE-10 desde historias clínicas</li>
                <li>Outcomes terapéuticos: progreso de objetivos y escalas de outcome</li>
                <li>Tasa de consentimientos firmados y envío de informes por correo</li>
              </ul>
              <p className="text-[11px] mt-3 p-3 rounded-lg" style={{ background: `${TEAL}10`, color: "var(--ns-text)" }}>
                Los datos ya existen en la base de NeuroSoft; estas vistas se irán activando conforme se consoliden los endpoints de agregación clínica.
              </p>
            </SectionCard>
          </div>
        )}
      </main>
    </>
  );
}
