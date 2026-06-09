/* ═══════════════════════════════════════════════════════════════════════
 * src/app/agenda/AgendaPage.jsx — Agenda de citas (vista Semana / Mes)
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useCallback, useEffect, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import {
  Btn, Card, I, Input, Label, MsgBanner, Sel, TopBar,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { safeLS } from "../../utils/safeLS.js";
import SectionCard from "../../ui/SectionCard.jsx";
import ConsentModal from "../patients/ConsentModal.jsx";
import { usePatientsPanel } from "../../hooks/usePatientsPanel.js";
import { useToast, useConfirm } from "../../contexts.jsx";
import AppointmentForm from "./AppointmentForm.jsx";

const DAYS = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
const MONTHS = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];

export default function AgendaPage({ setPage }) {
  const toast = useToast();
  const confirm = useConfirm();
  const { patients } = usePatientsPanel();
  const [stats, setStats] = useState(null);
  const [consentPatient, setConsentPatient] = useState(null);
  const [week, setWeek] = useState([]);
  const [monthCitas, setMonthCitas] = useState([]);
  const [ld, setLd] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [viewMode, setViewMode] = useState(safeLS.get("ns_agenda_view") || "semana");
  const [monthCursor, setMonthCursor] = useState(() => {
    const d = new Date();
    return { year: d.getFullYear(), month: d.getMonth() };
  });
  const [f, sF] = useState({
    patient_id: "",
    fecha: new Date().toISOString().split("T")[0],
    hora_inicio: "09:00", hora_fin: "10:00",
    tipo_cita: "evaluacion", motivo: "", recordar: true,
    eps: "", regimen: "", autorizacion_no: "", cups: "",
    modalidad: "presencial", discapacidad: "",
    contacto_telefono: "", contacto_correo: "",
  });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [notifPerm, setNotifPerm] = useState(
    typeof Notification !== "undefined" ? Notification.permission : "default"
  );
  const set = (k, val) => sF((o) => ({ ...o, [k]: val }));
  const selectedPatient = patients.find((p) => String(p.id) === String(f.patient_id));

  const openConsent = (patient = selectedPatient) => {
    if (!patient?.id) {
      toast.info("Seleccione o cree un paciente para imprimir o enviar el consentimiento.");
      return;
    }
    setConsentPatient(patient);
  };
  const reqNotif = async () => {
    if (typeof Notification === "undefined") return;
    const p = await Notification.requestPermission();
    setNotifPerm(p);
  };

  /* Programar recordatorios 15 min antes de cada cita hoy */
  useEffect(() => {
    if (notifPerm !== "granted" || !week.length) return;
    const today = new Date().toISOString().split("T")[0];
    const timers = [];
    week.forEach((day) => {
      if (day.fecha !== today) return;
      (day.citas || []).forEach((c) => {
        const [hh, mm] = (c.hora_inicio || "00:00").split(":").map(Number);
        const citaTime = new Date();
        citaTime.setHours(hh, mm - 15, 0, 0);
        const ms = citaTime.getTime() - Date.now();
        if (ms > 0 && ms < 86400000) {
          const t = setTimeout(() => {
            try {
              new Notification("Recordatorio de cita — NeuroSoft", {
                body: `${c.paciente_nombre || "Paciente"} a las ${c.hora_inicio}. Tipo: ${c.tipo_cita}. Motivo: ${c.motivo || "—"}`,
                icon: "/favicon.ico",
                /* `tag` debe ser estable: si volvía a `Math.random()`
                 * el navegador no podía deduplicar notificaciones de
                 * la misma cita disparadas en distintos renders. */
                tag: `cita_${c.id || `${day.fecha}_${c.hora_inicio}`}`,
                requireInteraction: true,
              });
            } catch (e) {
              /* §B7-fix: si el navegador revoca permisos en sesión, queda
               * traza mínima en consola para diagnosticar después. */
              try { console.debug("[Agenda] Notification falló:", e); } catch {}
            }
          }, ms);
          timers.push(t);
        }
      });
    });
    return () => timers.forEach(clearTimeout);
  }, [week, notifPerm]);

  const monthRange = useCallback(() => {
    const { year, month } = monthCursor;
    const pad = (n) => String(n).padStart(2, "0");
    const first = `${year}-${pad(month + 1)}-01`;
    const lastDay = new Date(year, month + 1, 0).getDate();
    const last = `${year}-${pad(month + 1)}-${pad(lastDay)}`;
    return { first, last };
  }, [monthCursor]);

  const load = useCallback(async () => {
    setLd(true);
    try {
      const statsP = api.get("/api/v1/agenda/stats").catch(() => ({
        hoy: 0, esta_semana: 0, pendientes: 0, atendidas_mes: 0,
      }));
      let citasP;
      if (viewMode === "mes") {
        const { first, last } = monthRange();
        citasP = api.get(`/api/v1/agenda/?fecha_desde=${first}&fecha_hasta=${last}&limit=200`).catch(() => []);
      } else {
        citasP = api.get("/api/v1/agenda/semana").catch(() => []);
      }
      const [s, data] = await Promise.all([statsP, citasP]);
      setStats(s);
      if (viewMode === "mes") {
        setMonthCitas(Array.isArray(data) ? data : []);
        setWeek([]);
      } else {
        setWeek(Array.isArray(data) ? data : []);
        setMonthCitas([]);
      }
    } catch {}
    setLd(false);
  }, [viewMode, monthRange]);
  useEffect(() => { load(); }, [load]);

  const create = async () => {
    setSaving(true);
    setMsg("");
    try {
      const body = { ...f };
      delete body.recordar;
      ["eps", "regimen", "autorizacion_no", "cups", "discapacidad", "contacto_telefono", "contacto_correo", "motivo"]
        .forEach((k) => { if (!body[k]) delete body[k]; });
      await api.post("/api/v1/agenda/", body);
      setMsg("ok");
      setShowForm(false);
      load();
    } catch (e) { setMsg(_parseError(e)); }
    setSaving(false);
  };

  const updateCitaEstado = async (cita, estado) => {
    if (!cita?.id) return;
    try {
      await api.patch(`/api/v1/agenda/${cita.id}`, { estado });
      toast.success(estado === "cancelada" ? "Cita cancelada." : "Cita actualizada.");
      load();
    } catch (e) { toast.error(_parseError(e)); }
  };

  const eliminarCita = async (cita) => {
    if (!cita?.id) return;
    if (!(await confirm({
      title: "Eliminar cita",
      message: `¿Eliminar la cita de ${cita.paciente_nombre || "paciente"} el ${cita.fecha || ""} a las ${cita.hora_inicio}?`,
      confirmText: "Eliminar",
      dangerous: true,
    }))) return;
    try {
      await api.del(`/api/v1/agenda/${cita.id}`);
      toast.success("Cita eliminada.");
      load();
    } catch (e) { toast.error(_parseError(e)); }
  };

  const tipC = {
    evaluacion: "bg-teal-100 text-teal-700",
    terapia: "bg-teal-100 text-teal-700",
    seguimiento: "bg-orange-100 text-orange-700",
    entrevista: "bg-purple-100 text-purple-700",
    devolucion: "bg-blue-100 text-blue-700",
    otro: "bg-gray-100 text-gray-700",
  };
  const estC = {
    programada: "bg-yellow-100 text-yellow-700",
    confirmada: "bg-teal-100 text-teal-700",
    atendida: "bg-teal-100 text-teal-700",
    cancelada: "bg-red-100 text-red-700",
  };

  return (
    <>
      <TopBar title="Agenda">
        {notifPerm !== "granted" && (
          <button onClick={reqNotif}
            className="px-3 py-1.5 rounded-full text-xs font-bold flex items-center gap-1.5"
            style={{ background: `${TEAL}15`, color: TEAL }}>
            <I name="notifications_active" className="text-sm" />Activar recordatorios
          </button>
        )}
        {notifPerm === "granted" && (
          <span className="text-xs flex items-center gap-1" style={{ color: TEAL }}>
            <I name="notifications_active" fill className="text-sm" />Recordatorios activos
          </span>
        )}
        <div className="flex rounded-full overflow-hidden border" style={{ borderColor: "var(--ns-card-b)" }}>
          {["semana", "mes"].map((v) => (
            <button key={v}
              onClick={() => { setViewMode(v); safeLS.set("ns_agenda_view", v); }}
              className="px-4 py-2 text-xs font-bold uppercase tracking-wider transition-all"
              style={viewMode === v
                ? { background: TEAL, color: "#fff" }
                : { background: "transparent", color: "var(--ns-muted)" }
              }>
              {v}
            </button>
          ))}
        </div>
        <Btn onClick={() => setShowForm(!showForm)}>
          <I name={showForm ? "close" : "add"} />{showForm ? "Cancelar" : "Nueva Cita"}
        </Btn>
      </TopBar>
      <main className="p-8 space-y-6">
        {stats && (
          <div className="grid grid-cols-4 gap-4">
            {[
              { l: "Hoy",            v: stats.hoy,           i: "today",            c: "#0D9488", b: "#dbe1ff30" },
              { l: "Esta Semana",    v: stats.esta_semana,   i: "date_range",       c: "#006a6a", b: "#9df1f130" },
              { l: "Pendientes",     v: stats.pendientes,    i: "pending_actions",  c: "#943700", b: "#ffdbcd20" },
              { l: "Atendidas (mes)",v: stats.atendidas_mes, i: "task_alt",         c: "#006a6a", b: "#9df1f120" },
            ].map((s, i) => (
              <div key={i} className="rounded-2xl p-5 flex items-center gap-4"
                style={{ background: s.b, border: `1px solid ${s.c}10` }}>
                <div className="w-11 h-11 rounded-xl flex items-center justify-center"
                  style={{ background: `${s.c}15`, color: s.c }}>
                  <I name={s.i} />
                </div>
                <div>
                  <p className="text-2xl font-extrabold">{s.v}</p>
                  <p className="text-xs font-bold uppercase tracking-wider" style={{ color: "#434655" }}>{s.l}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {showForm && (
          <AppointmentForm
            values={f}
            onChange={set}
            msg={msg}
            onDismissMsg={() => setMsg("")}
            setPage={setPage}
            onOpenConsent={() => openConsent()}
            onSubmit={create}
            saving={saving}
          />
        )}

        {ld ? (
          <div className="space-y-3 py-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-16 rounded-2xl ns-skeleton" style={{background:"var(--ns-subtle)"}}/>
            ))}
          </div>
        ) : viewMode === "mes" ? (
          (() => {
            const cur = new Date(monthCursor.year, monthCursor.month, 1);
            const firstWeekday = cur.getDay();
            const daysInMonth = new Date(monthCursor.year, monthCursor.month + 1, 0).getDate();
            const monthLabel = cur.toLocaleDateString("es", { month: "long", year: "numeric" });
            const byDate = {};
            (monthCitas || []).forEach((c) => {
              const key = String(c.fecha || "").slice(0, 10);
              if (!key) return;
              if (!byDate[key]) byDate[key] = [];
              byDate[key].push(c);
            });
            const cells = [];
            for (let i = 0; i < firstWeekday; i++) cells.push(null);
            for (let d = 1; d <= daysInMonth; d++) {
              const iso = `${monthCursor.year}-${String(monthCursor.month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
              cells.push({ day: d, iso, citas: byDate[iso] || [] });
            }
            const today = new Date().toISOString().split("T")[0];
            return (
              <Card className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <button onClick={() => setMonthCursor((c) => {
                    const m = c.month - 1;
                    return m < 0 ? { year: c.year - 1, month: 11 } : { year: c.year, month: m };
                  })} className="p-2 rounded-full hover:bg-gray-100" style={{ color: "var(--ns-muted)" }}>
                    <I name="chevron_left" />
                  </button>
                  <h3 className="text-lg font-bold capitalize">{monthLabel}</h3>
                  <button onClick={() => setMonthCursor((c) => {
                    const m = c.month + 1;
                    return m > 11 ? { year: c.year + 1, month: 0 } : { year: c.year, month: m };
                  })} className="p-2 rounded-full hover:bg-gray-100" style={{ color: "var(--ns-muted)" }}>
                    <I name="chevron_right" />
                  </button>
                </div>
                <div className="grid grid-cols-7 gap-2 mb-2">
                  {DAYS.map((d) => (
                    <div key={d} className="text-center text-[10px] font-extrabold uppercase tracking-wider py-1"
                      style={{ color: "var(--ns-muted)" }}>{d}</div>
                  ))}
                </div>
                <div className="grid grid-cols-7 gap-2">
                  {cells.map((c, i) => {
                    if (!c) return <div key={i} className="aspect-square rounded-xl" style={{ background: "transparent" }} />;
                    const isT = c.iso === today;
                    const n = c.citas.length;
                    return (
                      <div key={i} className="aspect-square rounded-xl p-2 flex flex-col"
                        style={{
                          background: isT ? `${TEAL}15` : "var(--ns-subtle)",
                          border: isT ? `2px solid ${TEAL}` : "1px solid transparent",
                        }}>
                        <p className="text-xs font-bold" style={{ color: isT ? TEAL : "var(--ns-text)" }}>{c.day}</p>
                        {n > 0 && (
                          <div className="mt-auto flex flex-col gap-0.5">
                            {c.citas.slice(0, 2).map((ct, ci) => (
                              <div key={ci} className="text-[9px] font-bold truncate px-1 py-0.5 rounded"
                                style={{
                                  background: ct.tipo_cita === "evaluacion" ? `${TEAL}20`
                                    : ct.tipo_cita === "terapia" ? "#67e8f920"
                                    : "#fed7aa50",
                                  color: ct.tipo_cita === "evaluacion" ? TEAL
                                    : ct.tipo_cita === "terapia" ? "#0e7490"
                                    : "#9a3412",
                                }}>
                                {ct.hora_inicio} {ct.paciente_nombre?.split(" ")[0] || ""}
                              </div>
                            ))}
                            {n > 2 && (
                              <p className="text-[9px] text-center font-bold" style={{ color: "var(--ns-muted)" }}>
                                +{n - 2} más
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
                <p className="text-[10px] text-center mt-4" style={{ color: "var(--ns-muted)" }}>
                  Vista mensual: citas cargadas para {monthLabel}.
                </p>
              </Card>
            );
          })()
        ) : week.length > 0 ? (
          <div className="grid grid-cols-7 gap-3">
            {week.map((day, di) => {
              const d = new Date(day.fecha + "T12:00:00");
              const isT = day.fecha === new Date().toISOString().split("T")[0];
              return (
                <div key={di} className={`rounded-2xl overflow-hidden ${isT ? "ring-2 ring-teal-600/30" : ""}`}>
                  <div className={`px-4 py-3 text-center ${isT ? "bg-teal-600 text-white" : "bg-white"}`}>
                    <p className={`text-[10px] font-bold uppercase ${isT ? "text-teal-100" : "text-gray-400"}`}>{DAYS[d.getDay()]}</p>
                    <p className="text-2xl font-extrabold">{d.getDate()}</p>
                    <p className={`text-[10px] ${isT ? "text-teal-200" : "text-gray-400"}`}>{MONTHS[d.getMonth()]}</p>
                  </div>
                  <div className="bg-white p-2 space-y-2 min-h-[200px]">
                    {day.citas && day.citas.length > 0 ? (
                      day.citas.map((c, ci) => (
                        <div key={ci} className="p-3 rounded-xl border border-gray-100 hover:shadow-md transition-all"
                          style={{
                            borderLeft: `3px solid ${
                              c.tipo_cita === "evaluacion" ? "#0D9488"
                              : c.tipo_cita === "terapia" ? "#006a6a"
                              : "#943700"
                            }`,
                          }}>
                          <p className="text-xs font-bold text-teal-600">
                            {c.hora_inicio}{c.hora_fin ? ` - ${c.hora_fin}` : ""}
                          </p>
                          <p className="text-xs font-bold truncate mt-1">{c.paciente_nombre || "Paciente"}</p>
                          <div className="flex items-center justify-between mt-2">
                            <span className={`text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded ${tipC[c.tipo_cita] || "bg-gray-100"}`}>{c.tipo_cita}</span>
                            <span className={`text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded ${estC[c.estado] || "bg-gray-100"}`}>{c.estado}</span>
                          </div>
                          {c.estado !== "cancelada" && c.estado !== "atendida" && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              <button type="button" onClick={() => updateCitaEstado(c, "atendida")}
                                className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: `${TEAL}20`, color: TEAL }}>
                                Atendida
                              </button>
                              <button type="button" onClick={() => updateCitaEstado(c, "cancelada")}
                                className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-red-50 text-red-600">
                                Cancelar
                              </button>
                              <button type="button" onClick={() => eliminarCita(c)}
                                className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ color: "var(--ns-muted)" }}>
                                Eliminar
                              </button>
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-gray-300 text-center pt-8">Sin citas</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <Card className="p-12 text-center">
            <I name="calendar_month" className="text-5xl text-gray-300 mb-4" />
            <p className="text-lg font-bold text-gray-500">Sin citas esta semana</p>
            <p className="text-sm text-gray-400">Usa "Nueva Cita" para agendar</p>
          </Card>
        )}
      </main>
      {consentPatient && (
        <ConsentModal
          patientId={consentPatient.id}
          patientName={
            consentPatient.nombre_completo
            || `${consentPatient.primer_nombre || ""} ${consentPatient.primer_apellido || ""}`.trim()
          }
          patientEmail={consentPatient.correo || f.contacto_correo || ""}
          onClose={() => setConsentPatient(null)}
        />
      )}
    </>
  );
}
