/* Dashboard — 3 zonas: hero accionable, indicadores, módulos */
import React, { useEffect, useState } from "react";
import { api } from "../../api/client.js";
import { useAuth, useToast } from "../../contexts.jsx";
import { TopBar } from "../../ui/primitives.jsx";
import StatTile from "../../ui/StatTile.jsx";
import ActionTile from "../../ui/ActionTile.jsx";
import SectionCard from "../../ui/SectionCard.jsx";
import NotificationsWidget from "./NotificationsWidget.jsx";

export default function DashboardPage({ setPage }) {
  const { user } = useAuth();
  const toast = useToast();
  const [stats, setStats] = useState(null);
  const [agendaStats, setAgendaStats] = useState(null);
  const [rehabSummary, setRehabSummary] = useState(null);

  useEffect(() => {
    api.get("/api/v1/patients/stats").then(setStats).catch(() => toast.error("Error cargando estadísticas"));
    api.get("/api/v1/agenda/stats").then(setAgendaStats).catch(() => {});
    api.get("/api/v1/patients/panel?por_pagina=50").then(async (d) => {
      const pacs = (d.pacientes || []).slice(0, 20);
      const adheres = await Promise.all(pacs.map(async (p) => {
        const a = await api.get(`/api/v1/rehab/adherence/${p.id}`).catch(() => null);
        return a ? { ...a, _paciente: p.nombre_completo } : null;
      }));
      const conPlan = adheres.filter((a) => a && a.has_plan);
      if (!conPlan.length) { setRehabSummary({ total: 0, promedio: 0, activos: [] }); return; }
      const promedio = Math.round(conPlan.reduce((s, a) => s + a.adherencia_pct, 0) / conPlan.length);
      setRehabSummary({
        total: conPlan.length,
        promedio,
        activos: conPlan.sort((a, b) => b.adherencia_pct - a.adherencia_pct).slice(0, 5).map((a) => ({ ...a, paciente: a._paciente })),
      });
    }).catch(() => setRehabSummary({ total: 0, promedio: 0, activos: [] }));
  }, [toast]);

  const hora = new Date().getHours();
  const saludo = hora < 12 ? "Buenos días" : hora < 18 ? "Buenas tardes" : "Buenas noches";
  const fecha = new Date().toLocaleDateString("es-CO", { weekday: "long", day: "numeric", month: "long", year: "numeric" });

  return (
    <>
      <TopBar title={`${saludo}, ${user?.nombre_completo?.split(" ")[0] || "Doctor"}`} />
      <main className="p-6 lg:p-8 space-y-6 max-w-7xl mx-auto" style={{ background: "var(--ns-bg)", minHeight: "100vh" }}>
        {/* Zona 1 — Hero accionable */}
        <section className="rounded-xl border p-6" style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
          <p className="text-[10px] font-bold uppercase tracking-widest mb-1" style={{ color: "var(--ns-muted)" }}>
            {fecha}
          </p>
          <h2 className="ns-serif text-2xl font-bold mb-4" style={{ color: "var(--ns-text)" }}>
            ¿Qué desea hacer hoy?
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <ActionTile icon="person_add" title="Ingresar paciente" subtitle="Registro e historia clínica" onClick={() => setPage("register")} />
            <ActionTile icon="clinical_notes" title="Realizar evaluación" subtitle="Aplicar batería neuropsicológica" onClick={() => setPage("evaluation")} />
            <ActionTile icon="fitness_center" title="Rehabilitación" subtitle="Plan y actividades cognitivas" onClick={() => setPage("rehab")} />
            <ActionTile icon="psychology" title="Terapia" subtitle="Sesiones y plan terapéutico" onClick={() => setPage("therapy")} />
          </div>
        </section>

        <NotificationsWidget />

        {/* Zona 2 — Indicadores */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatTile
            label="Pacientes"
            value={stats?.total_pacientes ?? "—"}
            icon="group"
            onClick={() => setPage("patients")}
            popoverContent={stats ? (
              <div className="text-xs space-y-1">
                <p><strong>Este mes:</strong> {stats.atendidos_este_mes ?? 0}</p>
                <p><strong>Este año:</strong> {stats.atendidos_este_anio ?? 0}</p>
                <p className="pt-1 opacity-70">Clic para ver panel completo</p>
              </div>
            ) : null}
          />
          <StatTile
            label="Sin informe"
            value={stats?.evaluaciones_sin_informe ?? "—"}
            icon="description"
            hint={(stats?.evaluaciones_sin_informe ?? 0) > 0 ? "Pendientes de PDF" : undefined}
            onClick={() => setPage("reports")}
          />
          <StatTile
            label="Citas hoy"
            value={agendaStats?.hoy ?? "—"}
            icon="calendar_today"
            onClick={() => setPage("agenda")}
            popoverContent={agendaStats ? (
              <div className="text-xs space-y-1">
                <p><strong>Esta semana:</strong> {agendaStats.esta_semana ?? 0}</p>
                <p><strong>Pendientes:</strong> {agendaStats.pendientes ?? 0}</p>
              </div>
            ) : null}
          />
        </div>

        {/* Rehab adherencia condicional */}
        {rehabSummary && rehabSummary.total > 0 && (
          <SectionCard eyebrow="Rehabilitación" title="Adherencia a planes activos" icon="fitness_center"
            headerRight={
              <button type="button" onClick={() => setPage("rehab")} className="text-xs font-semibold" style={{ color: "#0D9488" }}>
                Ver detalle
              </button>
            }>
            <p className="text-2xl font-bold mb-3" style={{ fontFamily: "Lora, serif", color: "#0D9488" }}>{rehabSummary.promedio}% promedio</p>
            <div className="space-y-2">
              {rehabSummary.activos.map((a, i) => (
                <div key={i} className="flex items-center gap-3 text-sm">
                  <span className="flex-1 truncate">{a.paciente}</span>
                  <span className="font-mono font-bold">{a.adherencia_pct}%</span>
                </div>
              ))}
            </div>
          </SectionCard>
        )}

        {/* Zona 3 — Módulos */}
        <SectionCard eyebrow="Módulos" title="Acceso rápido" icon="apps">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {[
              { icon: "person", title: "Pacientes", sub: "Panel y historias", p: "patients" },
              { icon: "psychology", title: "Evaluación", sub: "WISC, WAIS y más", p: "evaluation" },
              { icon: "checklist", title: "Screening", sub: "Escalas clínicas", p: "screening" },
              { icon: "fitness_center", title: "Rehabilitación", sub: "Planes cognitivos", p: "rehab" },
              { icon: "psychology_alt", title: "Terapia", sub: "Sesiones clínicas", p: "therapy" },
              { icon: "calendar_today", title: "Agenda", sub: "Citas y recordatorios", p: "agenda" },
              { icon: "description", title: "Informes", sub: "PDF y envío", p: "reports" },
              { icon: "bar_chart", title: "Estadísticas", sub: "Tendencia y demografía", p: "estadisticas" },
            ].map((m) => (
              <ActionTile key={m.p} icon={m.icon} title={m.title} subtitle={m.sub} onClick={() => setPage(m.p)} />
            ))}
          </div>
        </SectionCard>
      </main>
    </>
  );
}
