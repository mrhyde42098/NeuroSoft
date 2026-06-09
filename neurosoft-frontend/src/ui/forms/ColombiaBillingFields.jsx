import React from "react";
import { Input, Sel } from "../primitives.jsx";
import {
  ASEGURADORES_COLOMBIA,
  REGIMENES,
  requiereAutorizacion,
} from "../../data/aseguradoresColombia.js";
import { useCupsPsicologia } from "../../hooks/useCupsPsicologia.js";
import FormField from "./FormField.jsx";

/**
 * Bloque régimen / EPS / CUPS / autorización (Colombia).
 * @param {"register"|"agenda"} variant - nombre del campo de autorización
 */
export default function ColombiaBillingFields({
  values,
  onChange,
  variant = "register",
  cups: cupsProp,
  gridClassName = "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4",
  filterEpsByRegimen = variant === "register",
  showParticularOption = variant === "register",
  showCups = true,
}) {
  const { cups: cupsHook } = useCupsPsicologia();
  const cups = cupsProp ?? cupsHook;
  const authKey = variant === "agenda" ? "autorizacion_no" : "autorizacion_eps";
  const authValue = values[authKey] ?? "";
  const regimen = values.regimen ?? "";
  const epsList = filterEpsByRegimen && regimen
    ? ASEGURADORES_COLOMBIA.filter((a) => a.regimen === regimen)
    : ASEGURADORES_COLOMBIA;

  return (
    <div className={gridClassName}>
      <FormField label="Régimen">
        <Sel value={regimen} onChange={(e) => onChange("regimen", e.target.value)}>
          <option value="">
            {variant === "agenda" ? "— Sin especificar —" : "— Seleccionar —"}
          </option>
          {REGIMENES.map((r) => (
            <option key={r.id} value={r.id}>
              {r.label}
            </option>
          ))}
        </Sel>
      </FormField>
      <FormField label="EPS / Asegurador">
        <Sel value={values.eps ?? ""} onChange={(e) => onChange("eps", e.target.value)}>
          <option value="">
            {variant === "agenda" ? "— Particular —" : "— Seleccionar —"}
          </option>
          {epsList.map((a) => (
            <option key={a.codigo} value={a.nombre}>
              {a.nombre}
            </option>
          ))}
          {showParticularOption ? (
            <option value="Particular">Particular / Sin afiliación</option>
          ) : null}
        </Sel>
      </FormField>
      {showCups ? (
        <FormField label="CUPS">
          <Sel value={values.cups ?? ""} onChange={(e) => onChange("cups", e.target.value)}>
            <option value="">— Seleccionar —</option>
            {cups.map((c) => (
              <option key={c.codigo} value={`${c.codigo} - ${c.nombre}`}>
                {c.codigo} — {c.nombre}
              </option>
            ))}
          </Sel>
        </FormField>
      ) : null}
      <FormField
        label={`Nº autorización${requiereAutorizacion(regimen) ? " *" : ""}`}
      >
        <Input
          value={authValue}
          onChange={(e) => onChange(authKey, e.target.value)}
          placeholder={variant === "agenda" ? "Requerido EPS" : "Si la EPS lo exige"}
        />
      </FormField>
    </div>
  );
}
