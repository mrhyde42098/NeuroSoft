/* Catálogo EPS / aseguradores Colombia — [VERIFICAR] códigos ante BDUA/ADRES antes de RIPS */

export const REGIMENES = [
  { id: "contributivo", label: "Contributivo" },
  { id: "subsidiado", label: "Subsidiado" },
  { id: "especial", label: "Especial / Excepción" },
  { id: "particular", label: "Particular" },
  { id: "poliza", label: "Póliza / Prepagada" },
  { id: "arl", label: "ARL" },
  { id: "soat", label: "SOAT" },
];

export const ASEGURADORES_COLOMBIA = [
  { codigo: "EPS001", nombre: "Nueva EPS", regimen: "contributivo" },
  { codigo: "EPS002", nombre: "EPS Sura", regimen: "contributivo" },
  { codigo: "EPS003", nombre: "EPS Sanitas", regimen: "contributivo" },
  { codigo: "EPS004", nombre: "Salud Total", regimen: "contributivo" },
  { codigo: "EPS005", nombre: "Compensar", regimen: "contributivo" },
  { codigo: "EPS006", nombre: "Famisanar", regimen: "contributivo" },
  { codigo: "EPS007", nombre: "Coosalud", regimen: "contributivo" },
  { codigo: "EPS008", nombre: "Mutual SER", regimen: "contributivo" },
  { codigo: "EPS009", nombre: "Servicio Occidental de Salud (SOS)", regimen: "contributivo" },
  { codigo: "EPS010", nombre: "Aliansalud", regimen: "contributivo" },
  { codigo: "EPS011", nombre: "Comfenalco Valle", regimen: "contributivo" },
  { codigo: "EPS012", nombre: "Cajacopi", regimen: "subsidiado" },
  { codigo: "EPS013", nombre: "Capital Salud", regimen: "subsidiado" },
  { codigo: "EPS014", nombre: "Savia Salud", regimen: "subsidiado" },
  { codigo: "EPS015", nombre: "Asmet Salud", regimen: "subsidiado" },
  { codigo: "EPS016", nombre: "Emssanar", regimen: "subsidiado" },
  { codigo: "EPS017", nombre: "Capresoca", regimen: "subsidiado" },
  { codigo: "EPS018", nombre: "Pijaos Salud", regimen: "subsidiado" },
  { codigo: "EPS019", nombre: "Comfachocó", regimen: "subsidiado" },
  { codigo: "EPS020", nombre: "Comfaoriente", regimen: "subsidiado" },
  { codigo: "EPS021", nombre: "Comfaguajira", regimen: "subsidiado" },
  { codigo: "EPS022", nombre: "Comfamiliar Huila", regimen: "subsidiado" },
  { codigo: "EPS023", nombre: "Dusakawi", regimen: "especial" },
  { codigo: "EPS024", nombre: "AIC — Asociación Indígena del Cauca", regimen: "especial" },
  { codigo: "EPS025", nombre: "Anas Wayuu", regimen: "especial" },
  { codigo: "EPS026", nombre: "Mallamas", regimen: "especial" },
  { codigo: "EPS027", nombre: "Fomag (Magisterio)", regimen: "especial" },
  { codigo: "EPS028", nombre: "Sanidad Militar", regimen: "especial" },
  { codigo: "EPS029", nombre: "Sanidad Policía", regimen: "especial" },
  { codigo: "EPS030", nombre: "Ecopetrol", regimen: "especial" },
  { codigo: "PREP001", nombre: "Colsanitas", regimen: "poliza" },
  { codigo: "PREP002", nombre: "Coomeva Medicina Prepagada", regimen: "poliza" },
  { codigo: "PREP003", nombre: "Medplus", regimen: "poliza" },
  { codigo: "PREP004", nombre: "Colmédica", regimen: "poliza" },
  { codigo: "ARL001", nombre: "ARL Sura", regimen: "arl" },
  { codigo: "ARL002", nombre: "Positiva ARL", regimen: "arl" },
  { codigo: "ARL003", nombre: "Colmena ARL", regimen: "arl" },
  { codigo: "ARL004", nombre: "Bolívar ARL", regimen: "arl" },
  { codigo: "ARL005", nombre: "Axa Colpatria ARL", regimen: "arl" },
  { codigo: "PART", nombre: "Particular (sin EPS)", regimen: "particular" },
  { codigo: "SOAT", nombre: "SOAT", regimen: "soat" },
];

export function aseguradorOptions(regimenFilter) {
  const list = regimenFilter
    ? ASEGURADORES_COLOMBIA.filter((a) => a.regimen === regimenFilter)
    : ASEGURADORES_COLOMBIA;
  return list.map((a) => ({ value: a.nombre, label: a.nombre }));
}

export function requiereAutorizacion(regimen) {
  return ["contributivo", "subsidiado", "especial", "arl", "soat"].includes(regimen);
}
