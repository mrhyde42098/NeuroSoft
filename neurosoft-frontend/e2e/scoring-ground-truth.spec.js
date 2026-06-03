/* ═══════════════════════════════════════════════════════════════════════
 * e2e/scoring-ground-truth.spec.js
 * ───────────────────────────────────────────────────────────────────────
 * §test-e2e-scoring (2026-05-19): valida que el motor de scoring del backend
 * devuelve exactamente los escalares verificados contra informes clínicos
 * reales (Casos 1 y 2 del CLAUDE.md backend).
 *
 * Si alguno de estos tests falla → BUG CLÍNICO CRÍTICO. Detener release.
 *
 * Casos cubiertos:
 *   Caso 1 — Andrés Felipe Romero Castaño (16a 11m, M, Secundaria Incompleta):
 *     NiWiscDC PD=53 → escalar 11
 *     NiWiscSem PD=32 → escalar 11
 *     NiWiscVoc PD=37 → escalar 6
 *     NiWiscLN  PD=25 → escalar 16
 *     NiWiscCl  PD=46 → escalar 4
 *     NiWiscAri PD=21 → escalar 6
 *     NiWISCTot suma=83 → CI=87
 *
 *   Caso 2 — María Elena Cardona Restrepo (80a 5m, F, Primaria Incompleta):
 *     ViTMTA PD=239 → escalar 6 (con ajuste escolaridad +2)
 *     ViStP  PD=8   → escalar 3
 *     ViRDD  PD=4   → escalar 13
 *     ViGroberRLT  PD=3 → escalar 3
 *     ViGroberML_Tot PD=2 → escalar 6
 *     ViGroberMC_Tot PD=7 → escalar 4
 *     ViAni PD=8 → escalar 8
 *     ViYesavage PD=2 → escalar 2
 * ═══════════════════════════════════════════════════════════════════════ */

import { test, expect } from "@playwright/test";

const ADMIN = { user: "admin", pass: "neurosoft2025" };
let authToken = null;

test.beforeAll(async ({ request }) => {
  const r = await request.post("/api/v1/auth/login", {
    data: { username: ADMIN.user, password: ADMIN.pass },
  });
  expect(r.ok()).toBeTruthy();
  const body = await r.json();
  authToken = body.access_token;
  expect(authToken).toBeTruthy();
});

/**
 * Llama al endpoint de scoring directamente con un perfil de paciente
 * y un mapa { test_id: PD }. Devuelve { resultados: [{test_id, puntaje_escalar, ...}] }.
 */
async function scoreEvaluacion(request, { fecha_nacimiento, fecha_evaluacion, sexo, escolaridad, puntajes }) {
  const r = await request.post("/api/v1/scores/calculate", {
    headers: { Authorization: `Bearer ${authToken}` },
    data: {
      fecha_nacimiento,
      fecha_evaluacion,
      sexo,
      escolaridad,
      puntajes,
    },
  });
  expect(r.ok(), `scoring falló: ${r.status()}`).toBeTruthy();
  return r.json();
}

function findResult(resultados, testId) {
  const r = resultados.find(x => x.test_id === testId);
  expect(r, `No se encontró resultado para ${testId}`).toBeTruthy();
  return r;
}

test.describe("Scoring ground-truth — Caso 1 (Andrés, WISC-IV)", () => {
  const ctx = {
    fecha_nacimiento: "2008-05-30",
    fecha_evaluacion: "2025-05-15",
    sexo: "M",
    escolaridad: "Secundaria Incompleta",
    puntajes: {
      NiWiscDC: 53,
      NiWiscSem: 32,
      NiWiscVoc: 37,
      NiWiscLN: 25,
      NiWiscCl: 46,
      NiWiscAri: 21,
    },
  };

  const expected = {
    NiWiscDC: 11,
    NiWiscSem: 11,
    NiWiscVoc: 6,
    NiWiscLN: 16,
    NiWiscCl: 4,
    NiWiscAri: 6,
  };

  test("escalares coinciden con el informe clínico real", async ({ request }) => {
    const res = await scoreEvaluacion(request, ctx);
    for (const [tid, esperado] of Object.entries(expected)) {
      const r = findResult(res.resultados, tid);
      expect(r.puntaje_escalar, `${tid}: esperado ${esperado}, recibido ${r.puntaje_escalar}`)
        .toBe(esperado);
    }
  });
});

test.describe("Scoring ground-truth — Caso 2 (María Elena, Neuronorma AM)", () => {
  const ctx = {
    fecha_nacimiento: "1945-01-01",
    fecha_evaluacion: "2025-06-03",
    sexo: "F",
    escolaridad: "Primaria Incompleta",
    puntajes: {
      ViTMTA: 239,
      ViStP: 8,
      ViRDD: 4,
      ViGroberRLT: 3,
      ViGroberML_Tot: 2,
      ViGroberMC_Tot: 7,
      ViAni: 8,
      ViYesavage: 2,
    },
  };

  const expected = {
    ViTMTA: 6,
    ViStP: 3,
    ViRDD: 13,
    ViGroberRLT: 3,
    ViGroberML_Tot: 6,
    ViGroberMC_Tot: 4,
    ViAni: 8,
    ViYesavage: 2,
  };

  test("escalares Neuronorma con ajuste de escolaridad coinciden", async ({ request }) => {
    const res = await scoreEvaluacion(request, ctx);
    for (const [tid, esperado] of Object.entries(expected)) {
      const r = findResult(res.resultados, tid);
      expect(r.puntaje_escalar, `${tid}: esperado ${esperado}, recibido ${r.puntaje_escalar}`)
        .toBe(esperado);
    }
  });
});

test.describe("Endpoint /baremos/pruebas — catálogo público", () => {
  test("hay al menos 168 pruebas con baremos cargadas", async ({ request }) => {
    const r = await request.get("/api/v1/baremos/pruebas", {
      headers: { Authorization: `Bearer ${authToken}` },
    });
    expect(r.ok()).toBeTruthy();
    const data = await r.json();
    expect(data.total).toBeGreaterThanOrEqual(168);
    expect(data.por_poblacion.infantil).toBeGreaterThan(0);
    expect(data.por_poblacion.adulto_joven).toBeGreaterThan(0);
    expect(data.por_poblacion.adulto_mayor).toBeGreaterThan(0);
  });
});
