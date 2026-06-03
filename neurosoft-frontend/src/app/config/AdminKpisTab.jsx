/* ═══════════════════════════════════════════════════════════════════════
 * src/app/config/AdminKpisTab.jsx — Dashboard KPIs administrativo
 * ───────────────────────────────────────────────────────────────────────
 * Sprint 11. Vista para coordinación clínica con métricas agregadas:
 *
 *   • KPIs globales (pacientes, evaluaciones, planes, citas)
 *   • Producción por profesional (ordenada por carga reciente)
 *   • Distribución diagnóstica top-20 CIE-10
 *   • Información del baremo activo (Sprint 9)
 *
 * Todos los datos provienen de endpoints autenticados del backend
 * (`/api/v1/admin/kpis/*` + `/api/v1/baremos/info`).
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api } from "../../api/client.js";
import { Card, I, Label, Sel } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const KPI_GROUPS = [
  {
    key: "pacientes",
    label: "Pacientes",
    icon: "group",
    color: "#0d9488",
    tiles: [
      { k: "total",      l: "Total",         primary: true },
      { k: "nuevos_30d", l: "Nuevos 30 días" },
      { k: "nuevos_7d",  l: "Nuevos 7 días" },
    ],
  },
  {
    key: "evaluaciones",
    label: "Evaluaciones",
    icon: "psychology",
    color: "#7c3aed",
    tiles: [
      { k: "total",       l: "Total",         primary: true },
      { k: "este_mes",    l: "Este mes" },
      { k: "ultimos_30d", l: "Últimos 30 días" },
      { k: "firmadas",    l: "Firmadas" },
    ],
  },
  {
    key: "rehabilitacion",
    label: "Rehabilitación",
    icon: "fitness_center",
    color: "#f59e0b",
    tiles: [
      { k: "planes_total",    l: "Planes total",   primary: true },
      { k: "planes_activos",  l: "Activos" },
      { k: "planes_firmados", l: "Firmados" },
      { k: "sesiones_30d",    l: "Sesiones 30 días" },
    ],
  },
  {
    key: "agenda",
    label: "Agenda",
    icon: "calendar_today",
    color: "#dc2626",
    tiles: [
      { k: "citas_total",   l: "Total",        primary: true },
      { k: "esta_semana",   l: "Esta semana" },
    ],
  },
];

export default function AdminKpisTab() {
  const [kpis, setKpis] = useState(null);
  const [profs, setProfs] = useState([]);
  const [diag, setDiag] = useState([]);
  const [baremo, setBaremo] = useState(null);
  const [sources, setSources] = useState([]);
  const [periodo, setPeriodo] = useState(30);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    Promise.all([
      api.get("/api/v1/admin/kpis").catch(() => null),
      api.get(`/api/v1/admin/kpis/professional?dias=${periodo}`).catch(() => []),
      api.get("/api/v1/admin/kpis/diagnoses?top=20").catch(() => []),
      api.get("/api/v1/baremos/info").catch(() => null),
      api.get("/api/v1/baremos/sources").catch(() => []),
    ]).then(([k, ps, ds, b, s]) => {
      setKpis(k); setProfs(ps || []); setDiag(ds || []);
      setBaremo(b); setSources(s || []);
      setLoading(false);
    });
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load();   }, [periodo]);

  if (loading) {
    return (
      <Card className="p-8 text-center">
        <div className="animate-spin w-8 h-8 mx-auto border-4 border-teal-200 border-t-teal-600 rounded-full"/>
        <p className="text-xs mt-3" style={{ color: "var(--ns-muted)" }}>Cargando KPIs administrativos…</p>
      </Card>
    );
  }

  const profMaxEvals = Math.max(1, ...profs.map((p) => p[`evaluaciones_${periodo}d`] || 0));
  const diagMaxN = Math.max(1, ...diag.map((d) => d.n));

  return (
    <Card className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <I name="dashboard" style={{ color: TEAL }}/>Dashboard administrativo
        </h3>
        <div className="flex items-center gap-2">
          <Label className="text-xs mb-0">Periodo:</Label>
          <Sel value={periodo} onChange={(e) => setPeriodo(parseInt(e.target.value, 10))} className="w-32 text-xs">
            <option value={7}>Últimos 7 días</option>
            <option value={30}>Últimos 30 días</option>
            <option value={90}>Últimos 90 días</option>
            <option value={365}>Últimos 12 meses</option>
          </Sel>
        </div>
      </div>

      {/* ─── KPIs globales en tarjetas ──────────────────────────── */}
      {kpis && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {KPI_GROUPS.map((g) => {
            const data = kpis[g.key] || {};
            return (
              <div key={g.key} className="p-4 rounded-2xl border" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }}>
                <div className="flex items-center gap-2 mb-3">
                  <I name={g.icon} className="text-lg" style={{ color: g.color }}/>
                  <p className="text-sm font-bold uppercase tracking-wider">{g.label}</p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {g.tiles.map((t) => (
                    <div key={t.k}>
                      <p className={`font-extrabold ${t.primary ? "text-3xl" : "text-xl"}`} style={{ color: t.primary ? g.color : "var(--ns-text)" }}>
                        {data[t.k] != null ? data[t.k] : "—"}
                      </p>
                      <p className="text-[10px] uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>{t.l}</p>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ─── Producción por profesional ─────────────────────────── */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-bold flex items-center gap-2">
            <I name="bar_chart" className="text-base" style={{ color: TEAL }}/>
            Producción por profesional (últimos {periodo} días)
          </h4>
          <span className="text-xs" style={{ color: "var(--ns-muted)" }}>{profs.length} profesionales</span>
        </div>
        {profs.length === 0 ? (
          <div className="text-center py-8 text-xs" style={{ color: "var(--ns-muted)" }}>
            <I name="info" className="text-base mr-1"/>Sin datos. Registre profesionales y vincúlelos a pacientes.
          </div>
        ) : (
          <div className="space-y-2">
            {profs.map((p) => {
              const evalsRecent = p[`evaluaciones_${periodo}d`] || 0;
              const pct = (evalsRecent / profMaxEvals) * 100;
              return (
                <div key={p.profesional_id} className="p-3 rounded-xl" style={{ background: "var(--ns-subtle)" }}>
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-bold truncate">{p.nombre}</p>
                      {p.titulo && <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>{p.titulo}</p>}
                    </div>
                    <div className="flex gap-4 text-right">
                      <div>
                        <p className="text-[10px] font-bold uppercase" style={{ color: "var(--ns-muted)" }}>Pacientes</p>
                        <p className="text-sm font-bold">{p.pacientes}</p>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold uppercase" style={{ color: "var(--ns-muted)" }}>Evals</p>
                        <p className="text-sm font-bold" style={{ color: TEAL }}>{evalsRecent}</p>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold uppercase" style={{ color: "var(--ns-muted)" }}>Planes</p>
                        <p className="text-sm font-bold">{p.planes_firmados}</p>
                      </div>
                    </div>
                  </div>
                  <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "var(--ns-card)" }}>
                    <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: TEAL }}/>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ─── Distribución diagnóstica ───────────────────────────── */}
      <div>
        <h4 className="text-sm font-bold flex items-center gap-2 mb-3">
          <I name="pie_chart" className="text-base" style={{ color: TEAL }}/>
          Distribución diagnóstica (CIE-10, top 20)
        </h4>
        {diag.length === 0 ? (
          <div className="text-center py-6 text-xs" style={{ color: "var(--ns-muted)" }}>
            Aún no hay códigos CIE-10 registrados.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {diag.map((d) => {
              const pct = (d.n / diagMaxN) * 100;
              return (
                <div key={d.cie10} className="flex items-center gap-3 p-2 rounded-lg" style={{ background: "var(--ns-subtle)" }}>
                  <span className="text-xs font-mono font-bold w-16 shrink-0" style={{ color: TEAL }}>{d.cie10}</span>
                  <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: "var(--ns-card)" }}>
                    <div className="h-full rounded-full" style={{ width: `${pct}%`, background: TEAL }}/>
                  </div>
                  <span className="text-xs font-bold w-8 text-right">{d.n}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ─── Baremos cargados (Sprint 9 — read-only) ─────────────── */}
      <div>
        <h4 className="text-sm font-bold flex items-center gap-2 mb-3">
          <I name="science" className="text-base" style={{ color: TEAL }}/>
          Baremos activos en el motor de scoring
        </h4>
        {baremo && (
          <div className="p-3 rounded-xl mb-3" style={{ background: "var(--ns-subtle)" }}>
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-bold">Versión: <code className="text-xs">{baremo.version}</code></p>
              <span className="text-xs" style={{ color: "var(--ns-muted)" }}>{baremo.total_pruebas} pruebas</span>
            </div>
            <div className="flex flex-wrap gap-2 text-[10px]">
              {Object.entries(baremo.pruebas_por_poblacion || {}).map(([pop, n]) => (
                <span key={pop} className="px-2 py-0.5 rounded-full" style={{ background: `${TEAL}15`, color: TEAL }}>
                  {pop}: <b>{n}</b>
                </span>
              ))}
            </div>
            <p className="text-[10px] font-mono mt-2" style={{ color: "var(--ns-muted)" }}>
              SHA-256: {baremo.checksum_sha256?.slice(0, 16)}…
            </p>
          </div>
        )}
        <div className="space-y-2">
          <p className="text-[10px] font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>Fuentes normativas declaradas</p>
          {sources.map((s) => (
            <details key={s.id} className="p-3 rounded-xl" style={{ background: "var(--ns-subtle)" }}>
              <summary className="cursor-pointer text-sm font-bold">{s.nombre}</summary>
              <p className="text-[11px] mt-2" style={{ color: "var(--ns-muted)" }}>
                <b>Autores:</b> {s.autores} ({s.anio})<br/>
                <b>Edad:</b> {s.edad_min}–{s.edad_max} años
              </p>
              {s.pruebas_cubiertas && (
                <p className="text-[10px] mt-2" style={{ color: "var(--ns-muted)" }}>
                  <b>Pruebas:</b> {s.pruebas_cubiertas.slice(0, 6).join(", ")}{s.pruebas_cubiertas.length > 6 ? "…" : ""}
                </p>
              )}
              <p className="text-[10px] italic mt-2" style={{ color: "var(--ns-muted)" }}>{s.cita}</p>
            </details>
          ))}
        </div>
      </div>
    </Card>
  );
}
