/**
 * F8.1 — Sanity tests del refactor screening.js por constructo.
 * Ejecutar con: ``node tests/data/screening_constructo.test.cjs``
 * (no usamos vitest/jest — el proyecto frontend corre con Playwright e2e).
 *
 * Si la sintaxis cambia o los helpers no se exponen, este test falla
 * con un mensaje legible.
 */
"use strict";

const path = require("path");
const Module = require("module");

// Reemplaza require() de archivos .js para tratarlos como ESM y extraer named exports.
// Patrón mínimo: usa eval() sobre el código fuente para capturar ``export const``.
const fs = require("fs");
const screeningPath = path.join(__dirname, "..", "..", "src", "data", "screening.js");
const code = fs.readFileSync(screeningPath, "utf-8");

// 1) Elimina los prefijos ``export`` y deja los nombres originales. El archivo
// ya usa el estilo ``export const X = ...`` que coincide 1-a-1 con la asignación
// ``const X = ...``. Las funciones con ``export function`` se convierten en
// ``function`` plain. Esto preserva TODAS las referencias internas (los helpers
// llaman a SCREENING_INDEX, CONSTRUCTOS, etc. directamente).
const transformed = code
  .replace(/^export\s+const\s+/gm, "const ")
  .replace(/^export\s+function\s+/gm, "function ");

const harness = `
${transformed}
module.exports = {
  CONSTRUCTOS, POBLACIONES, SCREENING_INDEX, SCREENING_FORMS,
  getFormsPorConstructo, getConstructosDisponibles,
  getFormsPorPoblacion, getFormsPorEdad,
  sugerirPorConstructos, getScreeningMetadata,
};
`;

const m = { exports: {} };
new Function("module", "exports", harness)(m, m.exports);
const api = m.exports;

const asserts = [];
function check(name, fn) {
  try {
    fn();
    asserts.push({ name, ok: true });
  } catch (e) {
    asserts.push({ name, ok: false, err: e.message });
  }
}

check("CONSTRUCTOS exportado con 15 entradas", () => {
  if (!api.CONSTRUCTOS) throw new Error("CONSTRUCTOS no exportado");
  if (Object.keys(api.CONSTRUCTOS).length !== 15) {
    throw new Error("Esperaba 15 constructos, hay " + Object.keys(api.CONSTRUCTOS).length);
  }
});

check("SCREENING_INDEX cubre los 28 tests", () => {
  if (!api.SCREENING_INDEX) throw new Error("SCREENING_INDEX no exportado");
  if (!api.SCREENING_FORMS) throw new Error("SCREENING_FORMS no exportado");
  const idx = new Set(Object.keys(api.SCREENING_INDEX));
  const forms = new Set(Object.keys(api.SCREENING_FORMS));
  for (const id of forms) {
    if (!idx.has(id)) throw new Error("Falta index para " + id);
  }
  for (const id of idx) {
    if (!forms.has(id)) throw new Error("Index apunta a test inexistente: " + id);
  }
});

check("getFormsPorConstructo('depresion') incluye PHQ9, BDI2, GDS15, HADS", () => {
  const r = api.getFormsPorConstructo("depresion");
  for (const id of ["PHQ9", "BDI2", "GDS15", "HADS"]) {
    if (!r.includes(id)) throw new Error("Falta " + id);
  }
});

check("getFormsPorPoblacion('infantil') NO incluye tests de adulto mayor exclusivo", () => {
  const r = api.getFormsPorPoblacion("infantil");
  if (r.includes("GDS15")) throw new Error("GDS15 no debe ser infantil");
  if (r.includes("CDR")) throw new Error("CDR no debe ser infantil");
  if (!r.includes("MCHAT")) throw new Error("MCHAT debe ser infantil");
});

check("getFormsPorEdad(35) incluye universales (PHQ9) y específicos de adulto", () => {
  const r = api.getFormsPorEdad(35);
  for (const id of ["PHQ9", "BDI2", "GAD7", "ASRS"]) {
    if (!r.includes(id)) throw new Error("Falta " + id);
  }
  if (r.includes("MCHAT")) throw new Error("MCHAT no debe ser adulto");
});

check("getFormsPorEdad(8) NO incluye MMSE/MoCA/ACE3 (no son infantiles)", () => {
  const r = api.getFormsPorEdad(8);
  for (const id of ["MMSE", "MoCA", "ACE3", "ASRS"]) {
    if (r.includes(id)) throw new Error(id + " no debe ser infantil");
  }
});

check("sugerirPorConstructos(['depresion','ansiedad'], 35) ≥ 4 tests", () => {
  const r = api.sugerirPorConstructos(["depresion", "ansiedad"], 35);
  if (r.length < 4) throw new Error("Solo " + r.length + " tests");
});

check("getScreeningMetadata('PHQ9') tiene constructo Depresión", () => {
  const m = api.getScreeningMetadata("PHQ9");
  if (!m) throw new Error("PHQ9 sin metadata");
  if (m.constructo.label !== "Depresión") {
    throw new Error("Constructo PHQ9 debería ser Depresión, es " + m.constructo.label);
  }
});

check("getScreeningMetadata('INEXISTENTE') devuelve null", () => {
  if (api.getScreeningMetadata("INEXISTENTE") !== null) {
    throw new Error("Debe devolver null para test inexistente");
  }
});

check("POBLACIONES tiene 6 entradas", () => {
  if (Object.keys(api.POBLACIONES).length !== 6) {
    throw new Error("Esperaba 6 poblaciones");
  }
});

let failed = 0;
for (const a of asserts) {
  if (a.ok) {
    console.log("  PASS  " + a.name);
  } else {
    failed += 1;
    console.log("  FAIL  " + a.name + "  →  " + a.err);
  }
}

console.log();
console.log("Resultado: " + (asserts.length - failed) + "/" + asserts.length + " tests OK");
if (failed > 0) process.exit(1);
