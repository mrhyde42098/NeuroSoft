/** Nombre legible de paciente — convención única en toda la app. */
export function displayPatientName(p) {
  if (!p) return "";
  if (p.nombre_completo) return p.nombre_completo;
  return `${p.primer_nombre || ""} ${p.primer_apellido || ""}`.trim();
}
