# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: scoring-ground-truth.spec.js >> Scoring ground-truth — Caso 2 (María Elena, Neuronorma AM) >> escalares Neuronorma con ajuste de escolaridad coinciden
- Location: e2e\scoring-ground-truth.spec.js:135:3

# Error details

```
Error: scoring falló: 405

expect(received).toBeTruthy()

Received: false
```

# Test source

```ts
  1   | /* ═══════════════════════════════════════════════════════════════════════
  2   |  * e2e/scoring-ground-truth.spec.js
  3   |  * ───────────────────────────────────────────────────────────────────────
  4   |  * §test-e2e-scoring (2026-05-19): valida que el motor de scoring del backend
  5   |  * devuelve exactamente los escalares verificados contra informes clínicos
  6   |  * reales (Casos 1 y 2 del CLAUDE.md backend).
  7   |  *
  8   |  * Si alguno de estos tests falla → BUG CLÍNICO CRÍTICO. Detener release.
  9   |  *
  10  |  * Casos cubiertos:
  11  |  *   Caso 1 — Andrés Felipe Romero Castaño (16a 11m, M, Secundaria Incompleta):
  12  |  *     NiWiscDC PD=53 → escalar 11
  13  |  *     NiWiscSem PD=32 → escalar 11
  14  |  *     NiWiscVoc PD=37 → escalar 6
  15  |  *     NiWiscLN  PD=25 → escalar 16
  16  |  *     NiWiscCl  PD=46 → escalar 4
  17  |  *     NiWiscAri PD=21 → escalar 6
  18  |  *     NiWISCTot suma=83 → CI=87
  19  |  *
  20  |  *   Caso 2 — María Elena Cardona Restrepo (80a 5m, F, Primaria Incompleta):
  21  |  *     ViTMTA PD=239 → escalar 6 (con ajuste escolaridad +2)
  22  |  *     ViStP  PD=8   → escalar 3
  23  |  *     ViRDD  PD=4   → escalar 13
  24  |  *     ViGroberRLT  PD=3 → escalar 3
  25  |  *     ViGroberML_Tot PD=2 → escalar 6
  26  |  *     ViGroberMC_Tot PD=7 → escalar 4
  27  |  *     ViAni PD=8 → escalar 8
  28  |  *     ViYesavage PD=2 → escalar 2
  29  |  * ═══════════════════════════════════════════════════════════════════════ */
  30  | 
  31  | import { test, expect } from "@playwright/test";
  32  | 
  33  | const ADMIN = { user: "admin", pass: "neurosoft2025" };
  34  | let authToken = null;
  35  | 
  36  | test.beforeAll(async ({ request }) => {
  37  |   const r = await request.post("/api/v1/auth/login", {
  38  |     data: { username: ADMIN.user, password: ADMIN.pass },
  39  |   });
  40  |   expect(r.ok()).toBeTruthy();
  41  |   const body = await r.json();
  42  |   authToken = body.access_token;
  43  |   expect(authToken).toBeTruthy();
  44  | });
  45  | 
  46  | /**
  47  |  * Llama al endpoint de scoring directamente con un perfil de paciente
  48  |  * y un mapa { test_id: PD }. Devuelve { resultados: [{test_id, puntaje_escalar, ...}] }.
  49  |  */
  50  | async function scoreEvaluacion(request, { fecha_nacimiento, fecha_evaluacion, sexo, escolaridad, puntajes }) {
  51  |   const r = await request.post("/api/v1/scores/calculate", {
  52  |     headers: { Authorization: `Bearer ${authToken}` },
  53  |     data: {
  54  |       fecha_nacimiento,
  55  |       fecha_evaluacion,
  56  |       sexo,
  57  |       escolaridad,
  58  |       puntajes,
  59  |     },
  60  |   });
> 61  |   expect(r.ok(), `scoring falló: ${r.status()}`).toBeTruthy();
      |                                                  ^ Error: scoring falló: 405
  62  |   return r.json();
  63  | }
  64  | 
  65  | function findResult(resultados, testId) {
  66  |   const r = resultados.find(x => x.test_id === testId);
  67  |   expect(r, `No se encontró resultado para ${testId}`).toBeTruthy();
  68  |   return r;
  69  | }
  70  | 
  71  | test.describe("Scoring ground-truth — Caso 1 (Andrés, WISC-IV)", () => {
  72  |   const ctx = {
  73  |     fecha_nacimiento: "2008-05-30",
  74  |     fecha_evaluacion: "2025-05-15",
  75  |     sexo: "M",
  76  |     escolaridad: "Secundaria Incompleta",
  77  |     puntajes: {
  78  |       NiWiscDC: 53,
  79  |       NiWiscSem: 32,
  80  |       NiWiscVoc: 37,
  81  |       NiWiscLN: 25,
  82  |       NiWiscCl: 46,
  83  |       NiWiscAri: 21,
  84  |     },
  85  |   };
  86  | 
  87  |   const expected = {
  88  |     NiWiscDC: 11,
  89  |     NiWiscSem: 11,
  90  |     NiWiscVoc: 6,
  91  |     NiWiscLN: 16,
  92  |     NiWiscCl: 4,
  93  |     NiWiscAri: 6,
  94  |   };
  95  | 
  96  |   test("escalares coinciden con el informe clínico real", async ({ request }) => {
  97  |     const res = await scoreEvaluacion(request, ctx);
  98  |     for (const [tid, esperado] of Object.entries(expected)) {
  99  |       const r = findResult(res.resultados, tid);
  100 |       expect(r.puntaje_escalar, `${tid}: esperado ${esperado}, recibido ${r.puntaje_escalar}`)
  101 |         .toBe(esperado);
  102 |     }
  103 |   });
  104 | });
  105 | 
  106 | test.describe("Scoring ground-truth — Caso 2 (María Elena, Neuronorma AM)", () => {
  107 |   const ctx = {
  108 |     fecha_nacimiento: "1945-01-01",
  109 |     fecha_evaluacion: "2025-06-03",
  110 |     sexo: "F",
  111 |     escolaridad: "Primaria Incompleta",
  112 |     puntajes: {
  113 |       ViTMTA: 239,
  114 |       ViStP: 8,
  115 |       ViRDD: 4,
  116 |       ViGroberRLT: 3,
  117 |       ViGroberML_Tot: 2,
  118 |       ViGroberMC_Tot: 7,
  119 |       ViAni: 8,
  120 |       ViYesavage: 2,
  121 |     },
  122 |   };
  123 | 
  124 |   const expected = {
  125 |     ViTMTA: 6,
  126 |     ViStP: 3,
  127 |     ViRDD: 13,
  128 |     ViGroberRLT: 3,
  129 |     ViGroberML_Tot: 6,
  130 |     ViGroberMC_Tot: 4,
  131 |     ViAni: 8,
  132 |     ViYesavage: 2,
  133 |   };
  134 | 
  135 |   test("escalares Neuronorma con ajuste de escolaridad coinciden", async ({ request }) => {
  136 |     const res = await scoreEvaluacion(request, ctx);
  137 |     for (const [tid, esperado] of Object.entries(expected)) {
  138 |       const r = findResult(res.resultados, tid);
  139 |       expect(r.puntaje_escalar, `${tid}: esperado ${esperado}, recibido ${r.puntaje_escalar}`)
  140 |         .toBe(esperado);
  141 |     }
  142 |   });
  143 | });
  144 | 
  145 | test.describe("Endpoint /baremos/pruebas — catálogo público", () => {
  146 |   test("hay al menos 168 pruebas con baremos cargadas", async ({ request }) => {
  147 |     const r = await request.get("/api/v1/baremos/pruebas", {
  148 |       headers: { Authorization: `Bearer ${authToken}` },
  149 |     });
  150 |     expect(r.ok()).toBeTruthy();
  151 |     const data = await r.json();
  152 |     expect(data.total).toBeGreaterThanOrEqual(168);
  153 |     expect(data.por_poblacion.infantil).toBeGreaterThan(0);
  154 |     expect(data.por_poblacion.adulto_joven).toBeGreaterThan(0);
  155 |     expect(data.por_poblacion.adulto_mayor).toBeGreaterThan(0);
  156 |   });
  157 | });
  158 | 
```