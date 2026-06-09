import { safeLS } from "../utils/safeLS.js";

/** Persiste el paciente activo y campos clave para herencia entre módulos. */
export function persistActivePatient(patient) {
  if (!patient?.id) return;
  safeLS.set("ns_sel_patient", patient.id);
  if (patient.numero_documento) safeLS.set("ns_sel_patient_doc", patient.numero_documento);
  if (patient.codigo_rips) safeLS.set("ns_sel_patient_cie", patient.codigo_rips);
  if (patient.tipo_documento) safeLS.set("ns_sel_patient_tdoc", patient.tipo_documento);
}

export function readActivePatientMeta() {
  return {
    id: safeLS.get("ns_sel_patient") || "",
    doc: safeLS.get("ns_sel_patient_doc") || "",
    cie: safeLS.get("ns_sel_patient_cie") || "",
    tipoDoc: safeLS.get("ns_sel_patient_tdoc") || "CC",
  };
}

/** Campos de acompañante precargados desde el registro del paciente. */
export function companionFromPatient(patient) {
  if (!patient) return { nombre: "", relacion: "", telefono: "" };
  return {
    nombre: patient.acompanante || "",
    relacion: patient.acompanante_relacion || "",
    telefono: patient.acompanante_telefono || patient.telefono_acompanante || "",
  };
}
