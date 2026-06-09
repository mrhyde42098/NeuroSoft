/* ═══════════════════════════════════════════════════════════════════════
 * src/app/therapy/TareasTerapeuticasPanel.jsx — Tareas-casa entre sesiones
 * ───────────────────────────────────────────────────────────────────────
 * Componente que se monta dentro de SesionSOAPForm (o como panel suelto en
 * TherapyPage) para asignar y revisar tareas terapéuticas entre sesiones.
 *
 * Base evidencia: Kazantzis et al. (2016) meta-análisis g≈0.48 en outcome
 * cuando hay tarea inter-sesión revisada. Reúsa el patrón de adherencia de
 * rehab cognitiva.
 *
 * Endpoints:
 *   GET    /api/v1/therapy/tasks?patient_id=...
 *   POST   /api/v1/therapy/tasks
 *   PATCH  /api/v1/therapy/tasks/{id}
 *   DELETE /api/v1/therapy/tasks/{id}
 *   GET    /api/v1/therapy/tasks/{patient_id}/summary
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState, useCallback } from "react";
import { api, _parseError } from "../../api/client.js";
import { Btn, I, Sel, Txta } from "../../ui/primitives.jsx";
import { TEAL, NAVY, ACCENTS } from "../../ui/tokens.js";
import { useToast, useConfirm } from "../../contexts.jsx";

const PLUM = ACCENTS?.plum || "#6D28D9";

/* Catálogo de tipos de tarea — anclado al backend (Literal TASK_TIPOS) */
const TIPOS = [
  { id: "registro_pensamientos",  label: "Registro de pensamientos",  enfoque: "TCC",  hint: "Detección de distorsiones cognitivas — A-B-C." },
  { id: "registro_emocional",     label: "Registro emocional",        enfoque: "DBT",  hint: "Bitácora de estados emocionales y disparadores." },
  { id: "autorregistro_conducta", label: "Autorregistro de conducta", enfoque: "TCC",  hint: "Frecuencia / intensidad de un síntoma objetivo." },
  { id: "exposicion",             label: "Exposición",                enfoque: "TCC",  hint: "Subir un escalón de la jerarquía de ansiedad." },
  { id: "activacion_conductual",  label: "Activación conductual",     enfoque: "TCC",  hint: "Tareas placenteras / dominio para romper inercia depresiva." },
  { id: "habilidades_DBT",        label: "Habilidades DBT",           enfoque: "DBT",  hint: "Mindfulness, tolerancia al malestar, regulación." },
  { id: "psicoeducacion",         label: "Psicoeducación",            enfoque: "—",    hint: "Lectura / video con preguntas reflexivas." },
  { id: "libre",                  label: "Otra (libre)",              enfoque: "—",    hint: "Tarea personalizada redactada por el clínico." },
];

const FRECUENCIAS = [
  { id: "diaria",         label: "Diaria" },
  { id: "varias_semana",  label: "Varias veces por semana" },
  { id: "semanal",        label: "Semanal" },
  { id: "unica",          label: "Una sola vez" },
];

const ESTADO_META = {
  pendiente:    { label: "Pendiente",   c: "#94A3B8", bg: "#94A3B815" },
  en_progreso: { label: "En progreso", c: NAVY,      bg: `${NAVY}15` },
  completada:   { label: "Completada",  c: "#10b981", bg: "#10b98115" },
  parcial:      { label: "Parcial",     c: "#B45309", bg: "#B4530915" },
  omitida:      { label: "Omitida",     c: "#dc2626", bg: "#dc262615" },
};

export default function TareasTerapeuticasPanel({ patientId, planId, sessionId, profesionalId, embedded = false }) {
  const toast = useToast();
  const [tareas, setTareas] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [expandedId, setExpandedId] = useState(null);
  const [filterEstado, setFilterEstado] = useState("");

  const cargar = useCallback(async () => {
    setLoading(true);
    try {
      const qs = new URLSearchParams({ patient_id: patientId });
      if (filterEstado) qs.set("estado", filterEstado);
      const list = await api.get(`/api/v1/therapy/tasks?${qs.toString()}`);
      setTareas(list || []);
      const s = await api.get(`/api/v1/therapy/tasks/${patientId}/summary`);
      setSummary(s);
    } catch (e) {
      toast.error(_parseError(e));
    }
    setLoading(false);
  }, [patientId, filterEstado, toast]);

  useEffect(() => { if (patientId) cargar(); }, [patientId, cargar]);

  const Wrapper = embedded ? "div" : "div";

  return (
    <Wrapper className={embedded ? "" : "rounded-md border p-5"}
      style={!embedded ? { background: "var(--ns-card)", borderColor: "var(--ns-card-b)" } : {}}>
      {/* Encabezado editorial */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="ns-eyebrow" style={{ color: PLUM }}>Entre sesiones</p>
          <h3 className="ns-serif text-lg font-bold mt-0.5" style={{ color: "var(--ns-text)" }}>
            Tareas terapéuticas
          </h3>
          <p className="text-[11px] mt-1 max-w-md" style={{ color: "var(--ns-muted)" }}>
            La adherencia a tareas inter-sesión es uno de los predictores con mejor evidencia del outcome terapéutico.
          </p>
        </div>
        <button onClick={() => setShowForm(s => !s)}
          className="text-[11px] font-semibold px-3 py-1.5 rounded-md flex items-center gap-1"
          style={{ background: showForm ? "var(--ns-subtle)" : PLUM, color: showForm ? "var(--ns-text)" : "#fff" }}>
          <I name={showForm ? "close" : "add"} className="text-sm" />
          {showForm ? "Cerrar" : "Asignar tarea"}
        </button>
      </div>

      {/* Mini-resumen de adherencia */}
      {summary && summary.total > 0 && (
        <div className="grid grid-cols-4 gap-3 mb-4 p-3 rounded-md" style={{ background: "var(--ns-subtle)" }}>
          <Kpi label="Adherencia" value={`${summary.adherencia_global_pct}%`} color={summary.adherencia_global_pct >= 70 ? "#10b981" : summary.adherencia_global_pct >= 40 ? "#B45309" : "#dc2626"} />
          <Kpi label="Completadas" value={summary.completadas} color={NAVY} />
          <Kpi label="Pendientes"  value={summary.pendientes}  color="#94A3B8" />
          <Kpi label="Total"       value={summary.total}       color={PLUM} />
        </div>
      )}

      {/* Formulario inline para crear */}
      {showForm && (
        <NewTaskForm
          patientId={patientId}
          planId={planId}
          sessionId={sessionId}
          profesionalId={profesionalId}
          onCreated={() => { setShowForm(false); cargar(); toast.success("Tarea asignada."); }}
          onCancel={() => setShowForm(false)}
        />
      )}

      {/* Filtros */}
      {!showForm && tareas.length > 0 && (
        <div className="flex items-center gap-2 mb-3 text-[11px]">
          <span style={{ color: "var(--ns-muted)" }}>Filtrar:</span>
          {["", "pendiente", "en_progreso", "completada", "parcial", "omitida"].map(e => (
            <button key={e || "todas"} onClick={() => setFilterEstado(e)}
              className="px-2 py-0.5 rounded-full transition-all"
              style={{
                background: filterEstado === e ? PLUM : "transparent",
                color: filterEstado === e ? "#fff" : "var(--ns-muted)",
                border: `1px solid ${filterEstado === e ? PLUM : "var(--ns-card-b)"}`,
              }}>
              {e ? ESTADO_META[e].label : "Todas"}
            </button>
          ))}
        </div>
      )}

      {/* Lista de tareas */}
      {loading ? (
        <div className="text-center py-8" style={{ color: "var(--ns-muted)" }}>
          <div className="inline-block animate-spin w-5 h-5 border-2 border-current border-t-transparent rounded-full" />
        </div>
      ) : tareas.length === 0 ? (
        <div className="text-center py-8 rounded-md" style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
          <p className="text-xs ns-serif-italic">
            {filterEstado ? "Sin tareas en este estado." : "Aún no has asignado tareas a este paciente."}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {tareas.map(t => (
            <TaskRow key={t.id} task={t}
              expanded={expandedId === t.id}
              onToggle={() => setExpandedId(prev => prev === t.id ? null : t.id)}
              onChange={cargar} />
          ))}
        </div>
      )}
    </Wrapper>
  );
}

function Kpi({ label, value, color }) {
  return (
    <div>
      <p className="ns-serif text-xl font-bold tabular-nums leading-none" style={{ color }}>{value}</p>
      <p className="ns-eyebrow mt-1.5">{label}</p>
    </div>
  );
}

function NewTaskForm({ patientId, planId, sessionId, profesionalId, onCreated, onCancel }) {
  const toast = useToast();
  const [tipo, setTipo] = useState("libre");
  const [titulo, setTitulo] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [frecuencia, setFrecuencia] = useState("semanal");
  const [fechaLimite, setFechaLimite] = useState("");
  const [saving, setSaving] = useState(false);

  const tipoDef = TIPOS.find(t => t.id === tipo);

  const guardar = async () => {
    if (!titulo.trim()) {
      toast.warn("Dale un título a la tarea.");
      return;
    }
    setSaving(true);
    try {
      await api.post("/api/v1/therapy/tasks", {
        patient_id: patientId,
        plan_id: planId || null,
        session_id: sessionId || null,
        profesional_id: profesionalId || null,
        tipo,
        titulo: titulo.trim(),
        descripcion: descripcion.trim() || null,
        frecuencia,
        fecha_limite: fechaLimite || null,
      });
      onCreated?.();
    } catch (e) { toast.error(_parseError(e)); }
    setSaving(false);
  };

  return (
    <div className="rounded-md p-4 mb-4 border" style={{ borderColor: `${PLUM}40`, background: `${PLUM}05` }}>
      <p className="ns-eyebrow mb-3" style={{ color: PLUM }}>Nueva tarea</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
        <div>
          <p className="ns-eyebrow mb-1">Tipo</p>
          <Sel value={tipo} onChange={e => setTipo(e.target.value)}>
            {TIPOS.map(t => <option key={t.id} value={t.id}>{t.label} {t.enfoque !== "—" ? `· ${t.enfoque}` : ""}</option>)}
          </Sel>
          {tipoDef && (
            <p className="text-[11px] ns-serif-italic mt-1" style={{ color: "var(--ns-muted)" }}>
              {tipoDef.hint}
            </p>
          )}
        </div>
        <div>
          <p className="ns-eyebrow mb-1">Frecuencia</p>
          <Sel value={frecuencia} onChange={e => setFrecuencia(e.target.value)}>
            {FRECUENCIAS.map(f => <option key={f.id} value={f.id}>{f.label}</option>)}
          </Sel>
        </div>
        <div className="md:col-span-2">
          <p className="ns-eyebrow mb-1">Título</p>
          <input value={titulo} onChange={e => setTitulo(e.target.value)}
            maxLength={120}
            placeholder="Ej. Registro de pensamientos automáticos, 3 al día"
            className="w-full px-3 py-2 rounded-md text-sm"
            style={{ background: "var(--ns-input)", border: "1px solid var(--ns-card-b)", color: "var(--ns-text)" }} />
        </div>
        <div className="md:col-span-2">
          <p className="ns-eyebrow mb-1">Instrucciones detalladas <span className="ns-serif-italic opacity-60 font-normal">(opcional)</span></p>
          <Txta value={descripcion} onChange={e => setDescripcion(e.target.value)} rows={3}
            placeholder="Pasos, ejemplos, cómo se hace la tarea…"
            className="text-sm" />
        </div>
        <div>
          <p className="ns-eyebrow mb-1">Fecha límite <span className="ns-serif-italic opacity-60 font-normal">(opcional)</span></p>
          <input type="date" value={fechaLimite} onChange={e => setFechaLimite(e.target.value)}
            className="w-full px-3 py-2 rounded-md text-sm"
            style={{ background: "var(--ns-input)", border: "1px solid var(--ns-card-b)", color: "var(--ns-text)" }} />
        </div>
      </div>
      <div className="flex items-center justify-end gap-2">
        <Btn v="outline" onClick={onCancel} className="text-xs">Cancelar</Btn>
        <Btn onClick={guardar} disabled={saving} className="text-xs" style={{ background: PLUM }}>
          <I name="check" className="text-sm" />
          {saving ? "Guardando…" : "Asignar"}
        </Btn>
      </div>
    </div>
  );
}

function TaskRow({ task, expanded, onToggle, onChange }) {
  const toast = useToast();
  const confirm = useConfirm();
  const [saving, setSaving] = useState(false);
  const [nota, setNota] = useState(task.nota_clinico || "");
  const [respuesta, setRespuesta] = useState(task.respuesta || "");
  const [adherencia, setAdherencia] = useState(task.adherencia_pct ?? "");
  const [utilidad, setUtilidad] = useState(task.utilidad_pct ?? "");
  const [dificultad, setDificultad] = useState(task.dificultad_pct ?? "");

  const meta = ESTADO_META[task.estado] || ESTADO_META.pendiente;
  const tipoDef = TIPOS.find(t => t.id === task.tipo);

  const cambiarEstado = async (nuevoEstado) => {
    setSaving(true);
    try {
      await api.patch(`/api/v1/therapy/tasks/${task.id}`, {
        estado: nuevoEstado,
        completar: nuevoEstado === "completada",
      });
      onChange?.();
    } catch (e) { toast.error(_parseError(e)); }
    setSaving(false);
  };

  const guardarRevision = async () => {
    setSaving(true);
    try {
      await api.patch(`/api/v1/therapy/tasks/${task.id}`, {
        nota_clinico: nota,
        respuesta: respuesta || null,
        adherencia_pct: adherencia === "" ? null : parseInt(adherencia, 10),
        utilidad_pct: utilidad === "" ? null : parseInt(utilidad, 10),
        dificultad_pct: dificultad === "" ? null : parseInt(dificultad, 10),
        revisar: true,
      });
      toast.success("Revisión guardada.");
      onChange?.();
    } catch (e) { toast.error(_parseError(e)); }
    setSaving(false);
  };

  const archivar = async () => {
    if (!(await confirm({
      title: "Archivar tarea",
      message: "Esta tarea no se borrará, solo se ocultará del panel. ¿Continuar?",
      confirmText: "Archivar",
    }))) return;
    setSaving(true);
    try {
      await api.del(`/api/v1/therapy/tasks/${task.id}`);
      toast.success("Tarea archivada.");
      onChange?.();
    } catch (e) { toast.error(_parseError(e)); }
    setSaving(false);
  };

  return (
    <div className="rounded-md border transition-all"
      style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)", borderLeftWidth: 3, borderLeftColor: meta.c }}>
      {/* Cabecera clickable */}
      <button onClick={onToggle}
        className="w-full text-left p-3 flex items-center gap-3 hover:bg-black/[0.02]">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded-sm"
              style={{ background: meta.bg, color: meta.c }}>
              {meta.label}
            </span>
            {tipoDef && (
              <span className="text-[10px] ns-serif-italic" style={{ color: "var(--ns-muted)" }}>
                {tipoDef.label}
              </span>
            )}
            {task.revisada_en && (
              <span className="text-[10px] flex items-center gap-0.5" style={{ color: TEAL }}>
                <I name="check_circle" className="text-xs" /> Revisada
              </span>
            )}
          </div>
          <p className="text-sm font-semibold truncate" style={{ color: "var(--ns-text)" }}>
            {task.titulo}
          </p>
          <p className="text-[11px] mt-0.5" style={{ color: "var(--ns-muted)" }}>
            Asignada: {new Date(task.fecha_asignacion).toLocaleDateString("es-CO", { day: "numeric", month: "short" })}
            {task.fecha_limite && (
              <> · Límite: {new Date(task.fecha_limite).toLocaleDateString("es-CO", { day: "numeric", month: "short" })}</>
            )}
            {task.frecuencia && (
              <> · {FRECUENCIAS.find(f => f.id === task.frecuencia)?.label || task.frecuencia}</>
            )}
          </p>
        </div>
        <I name={expanded ? "expand_less" : "expand_more"}
          className="text-base" style={{ color: "var(--ns-muted)" }} />
      </button>

      {/* Detalle expandido */}
      {expanded && (
        <div className="px-3 pb-3 pt-1 border-t space-y-3" style={{ borderColor: "var(--ns-card-b)" }}>
          {task.descripcion && (
            <div>
              <p className="ns-eyebrow mb-1">Instrucciones</p>
              <p className="text-xs leading-relaxed" style={{ color: "var(--ns-text)" }}>{task.descripcion}</p>
            </div>
          )}

          {/* Cambio rápido de estado */}
          <div>
            <p className="ns-eyebrow mb-1.5">Estado</p>
            <div className="flex flex-wrap gap-1.5">
              {["pendiente", "en_progreso", "completada", "parcial", "omitida"].map(e => {
                const m = ESTADO_META[e];
                const activo = task.estado === e;
                return (
                  <button key={e} onClick={() => cambiarEstado(e)} disabled={saving}
                    className="text-[11px] font-semibold px-2 py-1 rounded-md transition-all"
                    style={{
                      background: activo ? m.c : "transparent",
                      color: activo ? "#fff" : m.c,
                      border: `1px solid ${m.c}40`,
                    }}>
                    {m.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Revisión clínica */}
          <div className="rounded-md p-3 border" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
            <p className="ns-eyebrow mb-2" style={{ color: PLUM }}>Revisión en sesión</p>
            <div>
              <p className="text-[11px] mb-1" style={{ color: "var(--ns-muted)" }}>Respuesta del paciente</p>
              <Txta value={respuesta} onChange={e => setRespuesta(e.target.value)} rows={2}
                placeholder="Lo que el paciente trajo / completó / reflexionó…"
                className="text-xs" />
            </div>
            <div className="grid grid-cols-3 gap-2 mt-2">
              <NumField label="Adherencia %" value={adherencia} onChange={setAdherencia} />
              <NumField label="Dificultad %" value={dificultad} onChange={setDificultad} />
              <NumField label="Utilidad %"   value={utilidad}   onChange={setUtilidad} />
            </div>
            <div className="mt-2">
              <p className="text-[11px] mb-1" style={{ color: "var(--ns-muted)" }}>Nota clínica</p>
              <Txta value={nota} onChange={e => setNota(e.target.value)} rows={2}
                placeholder="Observación clínica sobre la tarea / siguiente paso…"
                className="text-xs" />
            </div>
            <div className="flex items-center justify-between mt-3">
              <button onClick={archivar} disabled={saving}
                className="text-[11px] flex items-center gap-1" style={{ color: "#dc2626" }}>
                <I name="archive" className="text-sm" /> Archivar
              </button>
              <Btn onClick={guardarRevision} disabled={saving} className="text-xs" style={{ background: PLUM }}>
                <I name="save" className="text-sm" />
                {saving ? "Guardando…" : "Guardar revisión"}
              </Btn>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function NumField({ label, value, onChange }) {
  return (
    <div>
      <p className="text-[10px] mb-0.5" style={{ color: "var(--ns-muted)" }}>{label}</p>
      <input type="number" min="0" max="100" value={value}
        onChange={e => onChange(e.target.value)}
        className="w-full px-2 py-1 rounded text-xs"
        style={{ background: "var(--ns-input)", border: "1px solid var(--ns-card-b)", color: "var(--ns-text)" }} />
    </div>
  );
}
