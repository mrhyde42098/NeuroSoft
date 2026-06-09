import React from "react";
import { Btn, I, Sel } from "../primitives.jsx";
import { usePatientsPanel } from "../../hooks/usePatientsPanel.js";
import { displayPatientName } from "../../utils/displayPatientName.js";
import FormField from "./FormField.jsx";

/** Selector sin fetch — cuando la página ya tiene la lista (usePatientsPanel). */
export function PatientSelect({
  patients = [],
  loading = false,
  value,
  onChange,
  allowNew = false,
  onNewPatient,
  trailing = null,
  label = "Paciente",
  required = false,
  className = "",
  selectClassName = "flex-1",
  placeholder = "Seleccionar...",
  bare = false,
}) {
  const select = (
    <div className="flex gap-2 flex-wrap">
      <Sel
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={loading}
        className={selectClassName}
      >
        <option value="">{loading ? "Cargando..." : placeholder}</option>
        {patients.map((p) => (
          <option key={p.id} value={p.id}>
            {displayPatientName(p)}
          </option>
        ))}
      </Sel>
      {allowNew && onNewPatient ? (
        <Btn
          v="outline"
          className="text-xs shrink-0"
          onClick={onNewPatient}
          title="Abrir registro de paciente"
        >
          <I name="person_add" />
          Nuevo paciente
        </Btn>
      ) : null}
      {trailing}
    </div>
  );

  if (bare) return select;

  return (
    <FormField label={label} required={required} className={className}>
      {select}
    </FormField>
  );
}

/** Selector con fetch integrado (usePatientsPanel). */
export default function PatientSelector(props) {
  const { patients, loading } = usePatientsPanel();
  return <PatientSelect patients={patients} loading={loading} {...props} />;
}
