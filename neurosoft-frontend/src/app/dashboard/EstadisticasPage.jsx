/* Estadísticas clínicas — tendencia, demografía, población (movido desde Dashboard) */
import React, { useEffect, useState } from "react";
import { api } from "../../api/client.js";
import { useToast } from "../../contexts.jsx";
import { TopBar } from "../../ui/primitives.jsx";
import SectionCard from "../../ui/SectionCard.jsx";
import { TEAL, NAVY } from "../../ui/tokens.js";
import { SkeletonKpi } from "../../ui/Skeleton.jsx";

export default function EstadisticasPage() {
  const toast = useToast();
  const [stats, setStats] = useState(null);
  const [trendData, setTrendData] = useState([]);

  useEffect(() => {
    api.get("/api/v1/patients/stats").then(setStats).catch(() => toast.error("Error cargando estadísticas"));
    api.get("/api/v1/evaluations/trend?meses=6").then((rows) => setTrendData(rows || [])).catch(() => setTrendData([]));
  }, [toast]);

  const total = stats?.total_pacientes || 0;
  const pctM = total ? Math.round((stats.masculino / total) * 100) : 0;
  const pctF = total ? 100 - pctM : 0;
  const maxTrend = Math.max(...trendData.map((t) => t.val), 10);
  const ageGroups = [
    { l: "Niños (6-16)", v: stats?.ninos || 0, c: "#6366f1" },
    { l: "Adulto Joven", v: stats?.adulto_joven || 0, c: TEAL },
    { l: "Adulto Mayor", v: stats?.adulto_mayor || 0, c: "#e67e22" },
  ];

  return (
    <>
      <TopBar title="Estadísticas" subtitle="Tendencia, demografía y población atendida" />
      <main className="p-6 lg:p-8 space-y-6 max-w-7xl mx-auto" style={{ background: "var(--ns-bg)", minHeight: "100vh" }}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <SectionCard
            className="lg:col-span-2"
            eyebrow="Tendencia"
            title="Evaluaciones aplicadas"
            subtitle="Últimos 6 meses"
            icon="trending_up"
          >
            {!stats && <div className="ns-skeleton h-40 rounded-xl" />}
            {stats && trendData.length < 2 && (
              <p className="text-sm py-8 text-center" style={{ color: "var(--ns-muted)" }}>
                {trendData.length === 1
                  ? `${trendData[0].mes}: ${trendData[0].val} evaluación(es). Se necesitan ≥2 meses para la tendencia.`
                  : "Sin datos de tendencia aún."}
              </p>
            )}
            {stats && trendData.length >= 2 && (
              <svg viewBox="0 0 600 180" className="w-full h-40">
                <defs>
                  <linearGradient id="tg-est" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor={TEAL} stopOpacity="0.4" />
                    <stop offset="100%" stopColor={TEAL} stopOpacity="0" />
                  </linearGradient>
                </defs>
                <polygon
                  points={`30,160 ${trendData.map((t, i) =>
                    `${30 + i * (540 / (trendData.length - 1))},${20 + (1 - t.val / maxTrend) * 140}`
                  ).join(" ")} 570,160`}
                  fill="url(#tg-est)"
                />
                <polyline fill="none" stroke={TEAL} strokeWidth="2.5"
                  points={trendData.map((t, i) =>
                    `${30 + i * (540 / (trendData.length - 1))},${20 + (1 - t.val / maxTrend) * 140}`
                  ).join(" ")}
                />
              </svg>
            )}
          </SectionCard>

          <SectionCard eyebrow="Demografía" title="Distribución por sexo" icon="wc">
            {!stats && <SkeletonKpi />}
            {stats && total > 0 && (
              <>
                <div className="flex justify-center my-3">
                  <svg width="120" height="120" viewBox="0 0 140 140">
                    <circle cx="70" cy="70" r="55" fill="none" stroke="var(--ns-subtle)" strokeWidth="18" />
                    <circle cx="70" cy="70" r="55" fill="none" stroke={NAVY} strokeWidth="18"
                      strokeDasharray={`${(pctM / 100) * 345.5} 345.5`} transform="rotate(-90 70 70)" />
                    <text x="70" y="75" textAnchor="middle" fontSize="22" fontWeight="800" fill="var(--ns-text)">{total}</text>
                  </svg>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span>Masculino</span><span className="font-semibold">{stats.masculino} ({pctM}%)</span></div>
                  <div className="flex justify-between"><span>Femenino</span><span className="font-semibold">{stats.femenino} ({pctF}%)</span></div>
                </div>
              </>
            )}
          </SectionCard>
        </div>

        {ageGroups.some((g) => g.v > 0) && (
          <SectionCard eyebrow="Población" title="Distribución por grupo etario" icon="groups">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              {ageGroups.map((g) => {
                const pct = total ? Math.round((g.v / total) * 100) : 0;
                return (
                  <div key={g.l}>
                    <p className="text-2xl font-bold tabular-nums" style={{ fontFamily: "Lora, serif" }}>{g.v}</p>
                    <p className="text-xs font-semibold uppercase tracking-wide mt-1" style={{ color: g.c }}>{g.l}</p>
                    <div className="w-full h-1.5 rounded-full mt-2" style={{ background: "var(--ns-subtle)" }}>
                      <div className="h-1.5 rounded-full" style={{ width: `${pct}%`, background: g.c }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </SectionCard>
        )}
      </main>
    </>
  );
}
