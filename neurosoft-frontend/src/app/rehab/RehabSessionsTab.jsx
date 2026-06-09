import React, { useEffect, useMemo, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { useConfirm, useToast } from "../../contexts.jsx";
import {
  Btn, Card, EmptyState, I, Input, Label, MsgBanner,
  Sel, Skeleton, TopBar, Txta,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { DOMINIO_COLORS, DOMINIO_LABELS, ACTIVITY_COMPONENTS } from "./rehabConstants.js";

export default function SessionsTab({ patientId }) {
  const [sessions, setSessions] = useState([]);
  const [evolution, setEvolution] = useState(null);
  const [ld, setLd] = useState(true);

  useEffect(() => {
    setLd(true);
    Promise.all([
      api.get(`/api/v1/rehab/sessions/by-patient/${patientId}`).catch(() => []),
      api.get(`/api/v1/rehab/evolution/${patientId}`).catch(() => null),
    ]).then(([sess, evo]) => {
      setSessions(sess || []);
      setEvolution(evo);
      setLd(false);
    });
  }, [patientId]);

  if (ld) return <Skeleton className="h-64" />;
  if (sessions.length === 0) {
    return (
      <EmptyState
        icon="monitoring"
        title="Sin sesiones registradas"
        description="Las actividades realizadas en consulta o tarea-casa aparecerán aquí."
      />
    );
  }

  /* Agrupar por slug para mostrar evolución */
  const bySlug = {};
  sessions.forEach((s) => {
    bySlug[s.activity_slug] = bySlug[s.activity_slug] || [];
    bySlug[s.activity_slug].push(s);
  });

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-3xl font-extrabold" style={{ color: TEAL }}>
              {sessions.length}
            </p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Sesiones totales
            </p>
          </div>
          <div>
            <p className="text-3xl font-extrabold">
              {Math.round(
                sessions.reduce((a, s) => a + (s.score || 0), 0) /
                  Math.max(sessions.length, 1)
              )}
            </p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Score promedio
            </p>
          </div>
          <div>
            <p className="text-3xl font-extrabold">
              {sessions.filter((s) => s.modo === "tarea_casa").length}
            </p>
            <p className="text-xs font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Tarea-casa
            </p>
          </div>
        </div>
      </Card>

      {/* ─── Gráfica longitudinal por dominio ─── */}
      {evolution && evolution.dominios && evolution.dominios.length > 0 && (
        <EvolutionChart evolution={evolution} />
      )}

      {/* ── continuación: tabla de sesiones ── */}
      <Card className="overflow-hidden">
        <table className="w-full text-sm">
          <thead style={{ background: "var(--ns-subtle)" }}>
            <tr>
              <th className="px-4 py-3 text-left font-bold text-xs uppercase">Fecha</th>
              <th className="px-4 py-3 text-left font-bold text-xs uppercase">Actividad</th>
              <th className="px-4 py-3 text-center font-bold text-xs uppercase">Score</th>
              <th className="px-4 py-3 text-center font-bold text-xs uppercase">Aciertos</th>
              <th className="px-4 py-3 text-center font-bold text-xs uppercase">Errores</th>
              <th className="px-4 py-3 text-center font-bold text-xs uppercase">Modo</th>
            </tr>
          </thead>
          <tbody>
            {sessions.slice(0, 50).map((s) => (
              <tr key={s.id} className="border-b" style={{ borderColor: "var(--ns-card-b)" }}>
                <td className="px-4 py-3 text-xs">
                  {new Date(s.ts_inicio).toLocaleString("es", { dateStyle: "short", timeStyle: "short" })}
                </td>
                <td className="px-4 py-3 font-bold">{s.activity_slug}</td>
                <td className="px-4 py-3 text-center font-extrabold" style={{ color: TEAL }}>
                  {s.score ?? "—"}
                </td>
                <td className="px-4 py-3 text-center text-emerald-600 font-bold">
                  {s.aciertos ?? "—"}
                </td>
                <td className="px-4 py-3 text-center text-red-500 font-bold">
                  {s.errores ?? "—"}
                </td>
                <td className="px-4 py-3 text-center">
                  <span
                    className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded"
                    style={
                      s.modo === "tarea_casa"
                        ? { background: "#fef3c7", color: "#92400e" }
                        : { background: "#ecfdf5", color: "#065f46" }
                    }
                  >
                    {s.modo}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
 * EvolutionChart — gráfica SVG de scores promedio por dominio/semana
 * ═══════════════════════════════════════════════════════════════ */
function EvolutionChart({ evolution }) {
  const W = 720;
  const H = 240;
  const PAD_L = 40;
  const PAD_R = 20;
  const PAD_T = 20;
  const PAD_B = 40;

  /* Recolectar todas las semanas (eje X) */
  const weekSet = new Set();
  evolution.dominios.forEach((d) => d.puntos.forEach((p) => weekSet.add(p.semana)));
  const weeks = [...weekSet].sort();
  const xStep = (W - PAD_L - PAD_R) / Math.max(weeks.length - 1, 1);
  const xOf = (sem) => PAD_L + weeks.indexOf(sem) * xStep;
  const yOf = (score) => PAD_T + (1 - Math.min(100, Math.max(0, score)) / 100) * (H - PAD_T - PAD_B);

  const formatWeek = (w) => {
    const m = w.match(/^(\d{4})-W(\d{2})$/);
    if (!m) return w;
    return `S${m[2]}`;
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold flex items-center gap-2">
          <I name="show_chart" style={{ color: TEAL }} />
          Evolución por dominio cognitivo
        </h3>
        <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
          {evolution.total_sesiones} sesión(es) · {evolution.rango.desde} → {evolution.rango.hasta}
        </span>
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
        {/* Grilla horizontal cada 25 puntos */}
        {[0, 25, 50, 75, 100].map((v) => (
          <g key={v}>
            <line
              x1={PAD_L}
              y1={yOf(v)}
              x2={W - PAD_R}
              y2={yOf(v)}
              stroke="var(--ns-card-b)"
              strokeWidth="0.5"
              strokeDasharray={v === 0 || v === 100 ? "" : "3 4"}
            />
            <text
              x={PAD_L - 8}
              y={yOf(v) + 3}
              textAnchor="end"
              fontSize="9"
              fill="var(--ns-muted)"
            >
              {v}
            </text>
          </g>
        ))}

        {/* Línea de "promedio clínico" referencial en 70 */}
        <line
          x1={PAD_L}
          y1={yOf(70)}
          x2={W - PAD_R}
          y2={yOf(70)}
          stroke={TEAL}
          strokeWidth="1"
          strokeDasharray="6 4"
          strokeOpacity="0.4"
        />
        <text
          x={W - PAD_R}
          y={yOf(70) - 4}
          textAnchor="end"
          fontSize="9"
          fontWeight="bold"
          fill={TEAL}
          opacity="0.6"
        >
          objetivo
        </text>

        {/* Series por dominio */}
        {evolution.dominios.map((d, di) => {
          const color = DOMINIO_COLORS[d.dominio] || TEAL;
          const points = d.puntos
            .filter((p) => weeks.includes(p.semana))
            .map((p) => ({ x: xOf(p.semana), y: yOf(p.score_avg), v: p.score_avg, n: p.n }));
          if (points.length === 0) return null;
          return (
            <g key={di}>
              <polyline
                fill="none"
                stroke={color}
                strokeWidth="2.5"
                strokeLinejoin="round"
                strokeLinecap="round"
                points={points.map((p) => `${p.x},${p.y}`).join(" ")}
              />
              {points.map((p, pi) => (
                <g key={pi}>
                  <circle cx={p.x} cy={p.y} r="4" fill="#fff" stroke={color} strokeWidth="2" />
                  <text
                    x={p.x}
                    y={p.y - 8}
                    textAnchor="middle"
                    fontSize="9"
                    fontWeight="bold"
                    fill={color}
                  >
                    {Math.round(p.v)}
                  </text>
                </g>
              ))}
            </g>
          );
        })}

        {/* Etiquetas X */}
        {weeks.map((w, _i) => (
          <text
            key={w}
            x={xOf(w)}
            y={H - 12}
            textAnchor="middle"
            fontSize="10"
            fill="var(--ns-muted)"
          >
            {formatWeek(w)}
          </text>
        ))}
      </svg>

      {/* Leyenda */}
      <div className="flex flex-wrap gap-3 mt-3">
        {evolution.dominios.map((d, i) => {
          const color = DOMINIO_COLORS[d.dominio] || TEAL;
          return (
            <div key={i} className="flex items-center gap-1.5 text-xs">
              <span className="w-3 h-3 rounded-full" style={{ background: color }} />
              <span className="font-bold">{DOMINIO_LABELS[d.dominio] || d.dominio}</span>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
