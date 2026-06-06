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
    api.get("/api/v1/notifications/adherence/summary?dias=30").then((d) => {
      const activos = (d.pacientes || []).slice(0, 5).map((p) => ({
        adherencia_pct: p.adherencia_pct,
        paciente: p.paciente_nombre,
        has_plan: true,
      }));
      setRehabSummary({
        total: d.total_pacientes ?? activos.length,
        promedio: d.promedio_adherencia ?? 0,
        activos,
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

        {/* Zona 3 — Accesos complementarios (no duplican hero ni sidebar) */}
        <SectionCard eyebrow="Recursos" title="Herramientas y seguimiento" icon="hub">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {[
              { icon: "bar_chart", title: "Estadísticas", sub: "Tendencia, agenda y rehab", p: "estadisticas" },
              { icon: "compare", title: "Comparar evaluaciones", sub: "Evolución entre sesiones", p: "compare" },
              { icon: "menu_book", title: "Aprender", sub: "Glosario y protocolos", p: "aprender" },
              { icon: "library_books", title: "Referencias", sub: "Bibliografía clínica", p: "referencias" },
              { icon: "receipt_long", title: "RIPS / facturación", sub: "Exportación EPS", p: "rips" },
              { icon: "share", title: "Compartir", sub: "Enlaces seguros al paciente", p: "shares" },
              { icon: "settings", title: "Configuración", sub: "Informes, IA y respaldo", p: "config" },
              { icon: "help", title: "Ayuda", sub: "Guías de uso", p: "help" },
            ].map((m) => (
              <ActionTile key={m.p} icon={m.icon} title={m.title} subtitle={m.sub} onClick={() => setPage(m.p)} />
            ))}
          </div>
        </SectionCard>
      </main>
    </>
  );
}
