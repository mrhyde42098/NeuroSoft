/* ═══════════════════════════════════════════════════════════════════════
 * src/app/patients/CompanionsSection.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §M-7 — Sección de acompañantes del paciente.
 *
 * Reemplaza el campo de texto libre "acompañante" de la HC con una
 * sección que permite registrar múltiples acompañantes (familia, cuidadores,
 * tutores) con sus datos de contacto y permisos:
 *
 *   • Autoriza escalas (¿puede responder SNAP/GADS/CDI proxy?)
 *   • Autoriza contacto (¿se le envían recordatorios?)
 *   • Marca "principal" para identificar al acompañante de referencia.
 *
 * Embeddable en ClinicalHistoryPage / PatientDetailPage.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { useConfirm } from "../../contexts.jsx";
import { api, _parseError } from "../../api/client.js";
import { Btn, Card, I, Input, Label, Sel } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { useToast } from "../../contexts.jsx";

const RELACIONES = [
  { v: "madre",    l: "Madre" },
  { v: "padre",    l: "Padre" },
  { v: "conyuge",  l: "Cónyuge / pareja" },
  { v: "hermano",  l: "Hermano/a" },
  { v: "hijo",     l: "Hijo/a" },
  { v: "cuidador", l: "Cuidador/a" },
  { v: "tutor",    l: "Tutor legal" },
  { v: "otro",     l: "Otro" },
];

const EMPTY = {
  nombre_completo: "", relacion: "", documento: "", telefono: "", email: "",
  autoriza_escalas: false, autoriza_contacto: true, es_principal: false, notas: "",
};

export default function CompanionsSection({ patientId, embedded = false }) {
  const toast = useToast();
  const [companions, setCompanions] = useState([]);
  const [editing, setEditing] = useState(null); // null | "new" | id
  const [draft, setDraft] = useState(EMPTY);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const confirm = useConfirm();

  useEffect(() => {
    if (!patientId) { setCompanions([]); return; }
    setLoading(true);
    api.get(`/api/v1/companions?patient_id=${patientId}`)
      .then(d => { setCompanions(d || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, [patientId]);

  const startNew = () => {
    setDraft(EMPTY);
    setEditing("new");
  };

  const startEdit = (c) => {
    setDraft({ ...EMPTY, ...c });
    setEditing(c.id);
  };

  const cancel = () => { setEditing(null); setDraft(EMPTY); };

  const save = async () => {
    if (!draft.nombre_completo?.trim()) {
      toast.error("El nombre es obligatorio");
      return;
    }
    setSaving(true);
    try {
      const body = { ...draft, nombre_completo: draft.nombre_completo.trim() };
      let saved;
      if (editing === "new") {
        saved = await api.post(`/api/v1/companions?patient_id=${patientId}`, body);
        setCompanions(prev => [saved, ...prev]);
      } else {
        saved = await api.put(`/api/v1/companions/${editing}`, body);
        setCompanions(prev => prev.map(c => c.id === editing ? saved : c));
      }
      // Si el guardado fue marcado principal, descartar otros principales del state local
      if (saved.es_principal) {
        setCompanions(prev => prev.map(c => c.id === saved.id ? c : { ...c, es_principal: false }));
      }
      cancel();
      toast.success("Acompañante guardado");
    } catch (e) {
      toast.error(_parseError(e));
    }
    setSaving(false);
  };

  const remove = async (id) => {
    if (!(await confirm("¿Eliminar este acompañante?"))) return;
    try {
      await api.del(`/api/v1/companions/${id}`);
      setCompanions(prev => prev.filter(c => c.id !== id));
      toast.success("Acompañante eliminado");
    } catch (e) {
      toast.error(_parseError(e));
    }
  };

  const Wrapper = embedded ? "div" : Card;
  const wrapperProps = embedded ? {} : { className: "p-6" };

  return (
    <Wrapper {...wrapperProps}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-bold flex items-center gap-2">
            <I name="groups" style={{ color: TEAL }} />
            Acompañantes
          </h3>
          <p className="text-xs mt-0.5" style={{ color: "var(--ns-muted)" }}>
            Familiares o cuidadores responsables. El "principal" recibe los
            recordatorios y puede responder escalas proxy (CDI, SNAP-IV, GADS).
          </p>
        </div>
        {!editing && patientId && (
          <Btn onClick={startNew} className="text-xs">
            <I name="add" className="mr-1" />Añadir acompañante
          </Btn>
        )}
      </div>

      {!patientId && (
        <p className="text-xs text-center py-4" style={{ color: "var(--ns-muted)" }}>
          Selecciona un paciente para gestionar acompañantes.
        </p>
      )}

      {loading && (
        <div className="flex justify-center py-6">
          <div className="animate-spin w-6 h-6 border-4 border-teal-200 border-t-teal-600 rounded-full" />
        </div>
      )}

      {editing && (
        <div className="rounded-lg border p-4 mb-4 space-y-3"
          style={{ borderColor: TEAL, background: "rgba(13,148,136,0.04)" }}>
          <p className="ns-eyebrow" style={{ color: TEAL }}>
            {editing === "new" ? "Nuevo acompañante" : "Editar acompañante"}
          </p>
          <div className="grid sm:grid-cols-2 gap-3">
            <div className="sm:col-span-2">
              <Label>Nombre completo *</Label>
              <Input value={draft.nombre_completo}
                onChange={e => setDraft(d => ({ ...d, nombre_completo: e.target.value }))} />
            </div>
            <div>
              <Label>Relación con el paciente</Label>
              <Sel value={draft.relacion || ""}
                onChange={e => setDraft(d => ({ ...d, relacion: e.target.value }))}>
                <option value="">— Seleccionar —</option>
                {RELACIONES.map(r => <option key={r.v} value={r.v}>{r.l}</option>)}
              </Sel>
            </div>
            <div>
              <Label>Documento</Label>
              <Input value={draft.documento || ""}
                onChange={e => setDraft(d => ({ ...d, documento: e.target.value }))} />
            </div>
            <div>
              <Label>Teléfono</Label>
              <Input value={draft.telefono || ""}
                onChange={e => setDraft(d => ({ ...d, telefono: e.target.value }))}
                placeholder="3001234567" />
            </div>
            <div>
              <Label>Email</Label>
              <Input type="email" value={draft.email || ""}
                onChange={e => setDraft(d => ({ ...d, email: e.target.value }))}
                placeholder="contacto@email.com" />
            </div>
          </div>
          <div className="flex flex-wrap gap-3 pt-2">
            <label className="flex items-center gap-2 text-xs cursor-pointer">
              <input type="checkbox" checked={!!draft.es_principal}
                onChange={e => setDraft(d => ({ ...d, es_principal: e.target.checked }))} />
              <span className="font-bold">Principal</span>
              <span style={{ color: "var(--ns-muted)" }}>(recibe recordatorios)</span>
            </label>
            <label className="flex items-center gap-2 text-xs cursor-pointer">
              <input type="checkbox" checked={!!draft.autoriza_contacto}
                onChange={e => setDraft(d => ({ ...d, autoriza_contacto: e.target.checked }))} />
              <span>Autoriza contacto</span>
            </label>
            <label className="flex items-center gap-2 text-xs cursor-pointer">
              <input type="checkbox" checked={!!draft.autoriza_escalas}
                onChange={e => setDraft(d => ({ ...d, autoriza_escalas: e.target.checked }))} />
              <span>Autoriza responder escalas proxy</span>
            </label>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Btn variant="ghost" onClick={cancel} disabled={saving}>Cancelar</Btn>
            <Btn onClick={save} disabled={saving}
              style={{ background: TEAL, color: "white", borderColor: TEAL }}>
              <I name="save" className="mr-1" />
              {saving ? "Guardando…" : "Guardar"}
            </Btn>
          </div>
        </div>
      )}

      {!loading && companions.length === 0 && !editing && (
        <p className="text-xs text-center py-4 italic" style={{ color: "var(--ns-muted)" }}>
          Sin acompañantes registrados todavía.
        </p>
      )}

      <div className="space-y-2">
        {companions.map(c => (
          <div key={c.id}
            className="flex items-start gap-3 p-3 rounded border"
            style={{
              borderColor: c.es_principal ? TEAL : "var(--ns-card-b)",
              background: c.es_principal ? "rgba(13,148,136,0.05)" : "var(--ns-card)",
            }}>
            <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
              style={{
                background: c.es_principal ? TEAL : "var(--ns-subtle)",
                color: c.es_principal ? "white" : "var(--ns-muted)",
              }}>
              <I name={c.relacion === "madre" || c.relacion === "padre" ? "family_restroom"
                : c.relacion === "cuidador" ? "support_agent"
                : c.relacion === "tutor" ? "verified_user"
                : "person"} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <p className="font-bold text-sm">{c.nombre_completo}</p>
                {c.es_principal && (
                  <span className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded"
                    style={{ background: TEAL, color: "white" }}>Principal</span>
                )}
                {c.relacion && (
                  <span className="text-[10px] capitalize" style={{ color: "var(--ns-muted)" }}>
                    {RELACIONES.find(r => r.v === c.relacion)?.l || c.relacion}
                  </span>
                )}
              </div>
              <div className="text-xs mt-1 flex flex-wrap gap-3" style={{ color: "var(--ns-muted)" }}>
                {c.telefono && <span><I name="call" className="text-xs" />{c.telefono}</span>}
                {c.email && <span><I name="mail" className="text-xs" />{c.email}</span>}
                {c.documento && <span><I name="badge" className="text-xs" />{c.documento}</span>}
              </div>
              <div className="flex gap-3 mt-1.5">
                {c.autoriza_contacto && (
                  <span className="text-[10px] flex items-center gap-0.5" style={{ color: TEAL }}>
                    <I name="check" className="text-xs" />Contacto OK
                  </span>
                )}
                {c.autoriza_escalas && (
                  <span className="text-[10px] flex items-center gap-0.5" style={{ color: TEAL }}>
                    <I name="check" className="text-xs" />Escalas proxy
                  </span>
                )}
              </div>
            </div>
            <div className="flex gap-1">
              <button onClick={() => startEdit(c)}
                className="p-1.5 rounded hover:bg-gray-100" title="Editar">
                <I name="edit" className="text-sm" style={{ color: "var(--ns-muted)" }} />
              </button>
              <button onClick={() => remove(c.id)}
                className="p-1.5 rounded hover:bg-red-50" title="Eliminar">
                <I name="delete" className="text-sm" style={{ color: "#9F1239" }} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </Wrapper>
  );
}
