/**
 * E2E API — flujo paciente → WISC scoring → PDF Pro
 * Complementa scoring-ground-truth.spec.js con persistencia + informe.
 */
import { test, expect } from "@playwright/test";

const ADMIN = { user: "admin", pass: "neurosoft2025" };

test.describe("Flujo WISC → PDF Pro (API)", () => {
  let token;

  test.beforeAll(async ({ request }) => {
    const r = await request.post("/api/v1/auth/login", {
      data: { username: ADMIN.user, password: ADMIN.pass },
    });
    expect(r.ok()).toBeTruthy();
    token = (await r.json()).access_token;
  });

  test("crear paciente, calificar WISC y generar PDF pro", async ({ request }) => {
    const headers = { Authorization: `Bearer ${token}` };
    const doc = `E2E${Date.now().toString().slice(-8)}`;

    const patientRes = await request.post("/api/v1/patients/", {
      headers,
      data: {
        tipo_documento: "CC",
        numero_documento: doc,
        primer_nombre: "E2E",
        primer_apellido: "WiscPdf",
        fecha_nacimiento: "2008-05-30",
        sexo: "M",
        escolaridad: "Secundaria Incompleta",
        lateralidad: "Diestro",
        fecha_atencion: "2026-03-20",
      },
    });
    expect(patientRes.ok(), await patientRes.text()).toBeTruthy();
    const patientId = (await patientRes.json()).id;

    const scoreRes = await request.post("/api/v1/scores/", {
      headers,
      data: {
        patient_id: patientId,
        protocolo: "WISC-IV",
        puntajes: {
          NiWiscDC: 53,
          NiWiscSem: 32,
          NiWiscVoc: 37,
        },
      },
    });
    expect(scoreRes.ok(), await scoreRes.text()).toBeTruthy();
    const scoring = await scoreRes.json();
    const evalId = scoring.evaluation_id;
    expect(evalId).toBeTruthy();

    const niWisc = scoring.resultados.find((r) => r.test_id === "NiWiscDC");
    expect(niWisc?.puntaje_escalar).toBe(11);

    const pdfRes = await request.post(
      `/api/v1/reports/pdf/${evalId}?template=pro`,
      { headers },
    );
    expect(pdfRes.ok(), await pdfRes.text()).toBeTruthy();
    const ct = pdfRes.headers()["content-type"] || "";
    expect(ct).toMatch(/pdf/i);
    const buf = await pdfRes.body();
    expect(buf.byteLength).toBeGreaterThan(5000);
  });

  test("estimulos WISC Matrices tienen laminas por item_id", async ({ request }) => {
    const headers = { Authorization: `Bearer ${token}` };
    const r = await request.get("/api/v1/estimulos/por_test/NiWiscMat", { headers });
    expect(r.ok(), await r.text()).toBeTruthy();
    const items = await r.json();
    if (items.length < 35) {
      test.skip(true, "Ejecute seed_pearson_ejemplo_laminas.py en el entorno de prueba");
    }
    expect(items.length).toBeGreaterThanOrEqual(35);
    const one = items.find((x) => String(x.item_id) === "1");
    expect(one?.contenido_base64).toMatch(/^data:image\//);
  });
});
