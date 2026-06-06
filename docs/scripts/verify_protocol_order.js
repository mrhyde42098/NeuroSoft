/**
 * Verifica orden clínico de protocolos en EvalApplyPage:
 * - Batería cognitiva primero (Grober/CVLT/DC…)
 * - Escalas al final (puntaje diferido / sala de espera)
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const evalSrc = fs.readFileSync(
  path.join(root, "neurosoft-frontend/src/app/evaluation/EvalApplyPage.jsx"),
  "utf8"
);
const m = evalSrc.match(/const protos=(\{[\s\S]*?\});/);
if (!m) {
  console.error("No se encontró protos en EvalApplyPage.jsx");
  process.exit(1);
}
// eslint-disable-next-line no-eval
const protos = eval(`(${m[1]})`);

const prepare = (tests) => tests.map((t, i) => ({ ...t, orden_aplicacion: i + 1 }));

const EXPECTED_FIRST = {
  wisc_iv: "NiWiscDC",
  adulto_mayor: "GBTotal",
  ninos_comp: "NiEniE1 + NiEniE2 + NiEniE3 + NiEniE4 = NiEniLT",
  adulto_joven: "AdCVLT",
  wais_iii: "AdWAISFI",
  validez: "REY15",
};

const SCALES_LAST = {
  adulto_mayor: ["EscKertesz", "EscQueja", "EscYesavage", "EscLawton", "MMSE"],
  adulto_joven: ["EscSTAI", "AdBeck", "EscASRS"],
};

let ok = true;
for (const [pid, firstExpected] of Object.entries(EXPECTED_FIRST)) {
  const raw = protos[pid]?.tests || [];
  const ordered = prepare(raw);
  const first = ordered[0]?.test_id;
  if (first !== firstExpected) {
    ok = false;
    console.log(`FAIL ${pid}: primer test ${first} (esperado ${firstExpected})`);
  } else {
    console.log(`OK ${pid}: batería inicia en ${first}`);
  }
  const scales = SCALES_LAST[pid];
  if (scales) {
    const ids = ordered.map((t) => t.test_id);
    const lastN = ids.slice(-scales.length);
    if (JSON.stringify(lastN) !== JSON.stringify(scales)) {
      ok = false;
      console.log(`FAIL ${pid}: escalas al final esperadas ${scales.join(" → ")}, got ${lastN.join(" → ")}`);
    } else {
      console.log(`OK ${pid}: escalas al cierre (${scales.length})`);
    }
    const deferred = ordered.filter((t) => t.es_escala_diferida);
    if (deferred.length !== scales.length) {
      ok = false;
      console.log(`FAIL ${pid}: faltan es_escala_diferida en escalas`);
    }
  }
  if (pid === "adulto_mayor") {
    const groberIdx = ordered.findIndex((t) => t.test_id === "GBTotal");
    const fcroIdx = ordered.findIndex((t) => t.test_id === "NiFCROCop");
    if (groberIdx < 0 || fcroIdx < 0 || groberIdx >= fcroIdx) {
      ok = false;
      console.log(`FAIL adulto_mayor: Grober debe ir antes que FCRO copia`);
    }
  }
}
process.exit(ok ? 0 : 1);
