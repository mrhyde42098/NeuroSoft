/* ═══════════════════════════════════════════════════════════════════════
 * src/app/therapy/PlanTerapeuticoForm.jsx
 * ───────────────────────────────────────────────────────────────────────
 * Modal de creación de plan terapéutico. Selecciona enfoque (del catálogo),
 * diagnóstico CIE-10, motivo, duración estimada, y permite agregar
 * objetivos SMART al instante.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { Btn, I, Input, Sel, Txta } from "../../ui/primitives.jsx";
import { ACCENTS, NAVY } from "../../ui/tokens.js";
import { useToast } from "../../contexts.jsx";
import { ENFOQUES_TERAPEUTICOS } from "../../data/enfoquesTerapeuticos.js";

const PLUM = ACCENTS.plum;

export default function PlanTerapeuticoForm({ patientId, onSaved, onCancel }) {
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    patient_id: patientId,
    enfoque_principal: "",
    diagnostico_principal: "",
    diagnostico_secundario: "",
    motivo_consulta: "",
    duracion_estimada_sesiones: 12,
    objetivos: [],
  });
  const [nuevoObjetivo, setNuevoObjetivo] = useState({ descripcion: "", criterios_medibles: "" });

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));
  const enfoqueSeleccionado = ENFOQUES_TERAPEUTICOS.find(e => e.id === form.enfoque_principal);

  /* §B3-fix: cada objetivo recibe un _key estable al crearse para que React
   * pueda reconciliar correctamente cuando se borren los del medio (con key={i}
   * el item N+1 hereda el DOM/focus del N tras un splice). */
  const _genKey = () => `obj_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;

  const addObjetivo = () => {
    if (!nuevoObjetivo.descripcion.trim()) return;
    setForm(f => ({
      ...f,
      objetivos: [...f.objetivos, { ...nuevoObjetivo, orden: f.objetivos.length, _key: _genKey() }],
    }));
    setNuevoObjetivo({ descripcion: "", criterios_medibles: "" });
  };

  const removeObjetivo = (i) => {
    setForm(f => ({ ...f, objetivos: f.objetivos.filter((_, idx) => idx !== i) }));
  };

  const guardar = async () => {
    if (!form.enfoque_principal) {
      toast.warn("Selecciona un enfoque terapéutico.");
      return;
    }
    setSaving(true);
    try {
      const d = await api.post("/api/v1/therapy/plans", form);
      onSaved?.(d);
    } catch (e) { toast.error(_parseError(e)); }
    setSaving(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(15,23,42,0.55)", backdropFilter: "blur(2px)" }}
      onClick={onCancel}>
      <div onClick={e => e.stopPropagation()}
        className="w-full max-w-3xl max-h-[92vh] rounded-lg shadow-2xl flex flex-col overflow-hidden"
        style={{ background: "var(--ns-card)" }}>
        {/* Header */}
        <div className="px-6 py-4 border-b flex items-center justify-between"
          style={{ borderColor: "var(--ns-card-b)" }}>
          <div>
            <p className="ns-eyebrow" style={{ color: PLUM }}>Nuevo plan terapéutico</p>
            <h3 className="ns-serif text-xl font-bold mt-0.5">Define el marco del proceso</h3>
          </div>
          <button onClick={onCancel} aria-label="Cerrar"
            className="p-2 rounded-md hover:bg-gray-100" style={{ color: "var(--ns-muted)" }}>
            <I name="close" />
          </button>
        </div>

        <div className="flex-1 overflow-auto p-6 space-y-5">
          {/* Enfoque */}
          <div>
            <p className="ns-eyebrow mb-1.5">Enfoque terapéutico principal</p>
            <Sel value={form.enfoque_principal} onChange={e => set("enfoque_principal", e.target.value)}>
              <option value="">— Seleccionar —</option>
              {["individual", "pareja", "familia", "trauma", "duelo", "adicciones", "ninos_adolescentes"].map(cat => (
                <optgroup key={cat} label={cat.replace(/_/g, " ").toUpperCase()}>
                  {ENFOQUES_TERAPEUTICOS.filter(e => e.categoria === cat).map(e => (
                    <option key={e.id} value={e.id}>
                      {e.nombre} {e.sigla ? `(${e.sigla})` : ""} · Evidencia {e.evidencia}
                    </option>
                  ))}
                </optgroup>
              ))}
            </Sel>
            {enfoqueSeleccionado && (
              <div className="mt-2 p-3 rounded-md text-xs" style={{ background: `${PLUM}08`, border: `1px solid ${PLUM}20` }}>
                <p className="font-bold mb-1" style={{ color: PLUM }}>{enfoqueSeleccionado.nombre}</p>
                <p style={{ color: "var(--ns-muted)" }}>
                  Duración típica: <strong>{enfoqueSeleccionado.duracion_tipica}</strong> · Indicado para: {enfoqueSeleccionado.indicaciones.slice(0, 3).join(", ")}
                </p>
              </div>
            )}
          </div>

          {/* Diagnóstico */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="ns-eyebrow mb-1.5">Diagnóstico principal (CIE-10)</p>
              <Input value={form.diagnostico_principal} onChange={e => set("diagnostico_principal", e.target.value)}
                placeholder="Ej. F32.1" />
            </div>
            <div>
              <p className="ns-eyebrow mb-1.5">Diagnóstico secundario (opcional)</p>
              <Input value={form.diagnostico_secundario} onChange={e => set("diagnostico_secundario", e.target.value)}
                placeholder="Ej. F41.1" />
            </div>
          </div>

          {/* Motivo de consulta */}
          <div>
            <p className="ns-eyebrow mb-1.5">Motivo de consulta</p>
            <Txta value={form.motivo_consulta} onChange={e => set("motivo_consulta", e.target.value)}
              rows={3} placeholder="Resumen del motivo principal por el que el paciente busca terapia…"
              className="text-sm" />
          </div>

          {/* Duración estimada */}
          <div>
            <p className="ns-eyebrow mb-1.5">Duración estimada (sesiones)</p>
            <input type="number" min="1" max="200" value={form.duracion_estimada_sesiones}
              onChange={e => set("duracion_estimada_sesiones", parseInt(e.target.value, 10) || 12)}
              className="w-32 px-3 py-2 rounded-md text-sm"
              style={{ background: "var(--ns-input)", border: "1px solid var(--ns-card-b)", color: "var(--ns-text)" }} />
          </div>

          {/* Objetivos SMART */}
          <div className="ns-section-rule pl-5">
            <p className="ns-eyebrow mb-2">Objetivos terapéuticos (SMART)</p>
            <p className="text-xs mb-3" style={{ color: "var(--ns-muted)" }}>
              Específicos, Medibles, Alcanzables, Relevantes y Temporalmente acotados.
            </p>
            {form.objetivos.length > 0 && (
              <div className="space-y-2 mb-3">
                {form.objetivos.map((o, i) => (
                  <div key={o._key || `obj_idx_${i}`} className="flex items-start gap-2 p-3 rounded-md"
                    style={{ background: "var(--ns-subtle)" }}>
                    <span className="ns-mono text-xs font-bold shrink-0 mt-0.5" style={{ color: PLUM }}>{i + 1}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm">{o.descripcion}</p>
                      {o.criterios_medibles && (
                        <p className="text-[11px] mt-1 ns-serif-italic" style={{ color: "var(--ns-muted)" }}>
                          Cómo se mide: {o.criterios_medibles}
                        </p>
                      )}
                    </div>
                    <button onClick={() => removeObjetivo(i)} aria-label="Eliminar objetivo"
                      className="p-1 rounded hover:bg-red-50 text-red-500"><I name="close" className="text-sm" /></button>
                  </div>
                ))}
              </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              <Input value={nuevoObjetivo.descripcion}
                onChange={e => setNuevoObjetivo(o => ({ ...o, descripcion: e.target.value }))}
                placeholder="Describe el objetivo…" className="md:col-span-1" />
              <Input value={nuevoObjetivo.criterios_medibles}
                onChange={e => setNuevoObjetivo(o => ({ ...o, criterios_medibles: e.target.value }))}
                placeholder="Cómo se mide (criterio observable)…" className="md:col-span-1" />
              <Btn v="outline" onClick={addObjetivo}
                disabled={!nuevoObjetivo.descripcion.trim()}
                className="text-xs"><I name="add" className="text-sm" />Agregar</Btn>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t flex items-center justify-end gap-2"
          style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
          <Btn v="outline" onClick={onCancel} className="text-xs">Cancelar</Btn>
          <Btn onClick={guardar} disabled={saving || !form.enfoque_principal} className="text-xs" style={{ background: PLUM }}>
            <I name="save" className="text-sm" />{saving ? "Creando…" : "Crear plan"}
          </Btn>
        </div>
      </div>
    </div>
  );
}
