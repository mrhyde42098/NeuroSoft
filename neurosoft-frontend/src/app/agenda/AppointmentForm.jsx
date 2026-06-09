import React from "react";
import { Btn, I, Input, Label, MsgBanner, Sel } from "../../ui/primitives.jsx";
import SectionCard from "../../ui/SectionCard.jsx";
import PatientSelector from "../../ui/forms/PatientSelector.jsx";
import ColombiaBillingFields from "../../ui/forms/ColombiaBillingFields.jsx";
import { requiereAutorizacion } from "../../data/aseguradoresColombia.js";

export default function AppointmentForm({
  values,
  onChange,
  msg,
  onDismissMsg,
  setPage,
  onOpenConsent,
  onSubmit,
  saving,
}) {
  const set = (k, val) => onChange(k, val);

  return (
    <SectionCard eyebrow="Agenda" title="Nueva cita" icon="calendar_add_on">
      <MsgBanner msg={msg === "ok" ? "ok" : msg} onDismiss={msg && msg !== "ok" ? onDismissMsg : null} />
      <div className="grid grid-cols-6 gap-4">
        <div className="col-span-2">
          <PatientSelector
            value={values.patient_id}
            onChange={(id) => set("patient_id", id)}
            allowNew={!!setPage}
            onNewPatient={setPage ? () => setPage("register") : undefined}
            trailing={(
              <Btn v="outline" className="text-xs shrink-0" onClick={onOpenConsent} title="Imprimir o enviar consentimiento informado">
                <I name="draw" />
                Consentimiento
              </Btn>
            )}
          />
        </div>
        <div><Label>Fecha</Label><Input type="date" value={values.fecha} onChange={(e) => set("fecha", e.target.value)} /></div>
        <div><Label>Inicio</Label><Input type="time" value={values.hora_inicio} onChange={(e) => set("hora_inicio", e.target.value)} /></div>
        <div><Label>Fin</Label><Input type="time" value={values.hora_fin} onChange={(e) => set("hora_fin", e.target.value)} /></div>
        <div>
          <Label>Tipo</Label>
          <Sel value={values.tipo_cita} onChange={(e) => set("tipo_cita", e.target.value)}>
            <option value="evaluacion">Evaluación</option>
            <option value="terapia">Terapia</option>
            <option value="seguimiento">Seguimiento</option>
            <option value="devolucion">Devolución de resultados</option>
            <option value="entrevista">Entrevista</option>
            <option value="otro">Otro</option>
          </Sel>
        </div>
        <div>
          <Label>Modalidad</Label>
          <Sel value={values.modalidad} onChange={(e) => set("modalidad", e.target.value)}>
            <option value="presencial">Presencial</option>
            <option value="telepsicologia">Telepsicología</option>
            <option value="telefonica">Telefónica</option>
          </Sel>
        </div>
      </div>
      <ColombiaBillingFields values={values} onChange={set} variant="agenda" gridClassName="grid grid-cols-4 gap-4 mt-4" />
      <div className="grid grid-cols-3 gap-4 mt-4">
        <div><Label>Contacto teléfono</Label><Input value={values.contacto_telefono} onChange={(e) => set("contacto_telefono", e.target.value)} /></div>
        <div><Label>Contacto correo</Label><Input type="email" value={values.contacto_correo} onChange={(e) => set("contacto_correo", e.target.value)} /></div>
        <div><Label>Discapacidad (si aplica)</Label><Input value={values.discapacidad} onChange={(e) => set("discapacidad", e.target.value)} placeholder="Ninguna" /></div>
      </div>
      <div className="mt-4">
        <Label>Motivo</Label>
        <Input value={values.motivo} onChange={(e) => set("motivo", e.target.value)} placeholder="Ej: Evaluación WISC-IV" />
      </div>
      <p className="text-[11px] mt-3" style={{ color: "var(--ns-muted)" }}>
        Recordatorios: notificación del navegador 15 min antes (activar arriba). Para SMS/correo automático, configure SMTP en Configuración → Comunicaciones.
      </p>
      <div className="flex flex-wrap justify-end items-center gap-2 mt-4">
        {values.patient_id && (
          <Btn v="outline" className="!min-h-[44px] !py-2.5 !px-5 !text-sm" onClick={onOpenConsent}>
            <I name="draw" className="text-sm" />
            Consentimiento informado
          </Btn>
        )}
        <Btn
          className="!min-h-[44px] !py-2.5 !px-5 !text-sm"
          onClick={onSubmit}
          disabled={saving || !values.patient_id || (requiereAutorizacion(values.regimen) && !values.autorizacion_no)}
        >
          {saving ? "Guardando..." : "Agendar Cita"}
        </Btn>
      </div>
    </SectionCard>
  );
}
