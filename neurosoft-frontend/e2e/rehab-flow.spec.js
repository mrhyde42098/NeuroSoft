/* ═══════════════════════════════════════════════════════════════════════
 * e2e/rehab-flow.spec.js — Flujo Evaluar → Rehabilitar → Tarea-casa
 * ───────────────────────────────────────────────────────────────────────
 * Documentado en e2e/README.md. Esta primera version prepara la
 * estructura: login del clinico, llegar a Pacientes, abrir RehabPage.
 * Los pasos finales (compartir link publico + Stroop del paciente) se
 * iteran en sesiones siguientes a medida que ajustamos selectores.
 *
 * Si un paso falla por selector cambiado, marcar `test.fixme(...)` con
 * una nota y avanzar — la suite SIGUE siendo util como red de regresion.
 * ═══════════════════════════════════════════════════════════════════════ */

import { test, expect } from "@playwright/test";

const ADMIN = { user: "admin", pass: "neurosoft2025" };

async function loginAsAdmin(page) {
  await page.goto("/");
  /* Desregistrar SW: ver smoke.spec.js para detalles. */
  await page.evaluate(async () => {
    if ("serviceWorker" in navigator) {
      const regs = await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.map((r) => r.unregister()));
    }
  });
  await page.fill('input[placeholder="usuario"]', ADMIN.user);
  await page.fill('input[type="password"]', ADMIN.pass);
  const loginResp = page.waitForResponse(
    (r) => r.url().includes("/api/v1/auth/login"),
    { timeout: 15_000 },
  );
  await page.locator('input[type="password"]').press("Enter");
  await loginResp;
  await expect(page.locator("button >> text=Pacientes")).toBeVisible({ timeout: 15_000 });
}

test.describe("Rehab — flujo end-to-end (iterativo)", () => {
  test("clinico puede llegar a la pagina de Rehabilitacion", async ({ page }) => {
    await loginAsAdmin(page);

    /* Sidebar → "Plan & Actividades" (item de la seccion Rehabilitación). */
    await page.locator("button >> text=Plan & Actividades").click();

    /* La pagina muestra al menos un encabezado. Aceptamos varios titulos
     * porque la UI puede cambiar entre "Plan", "Rehabilitacion", etc. */
    const heading = page.locator(
      'h1:has-text("Rehabilita"), h2:has-text("Rehabilita"), header:has-text("Rehabilita"), h1:has-text("Plan"), h2:has-text("Plan")'
    );
    await expect(heading.first()).toBeVisible({ timeout: 10_000 });
  });

  test.fixme("crear plan, firmar y compartir link publico", async ({ page }) => {
    /* Pendiente: requiere paciente seed + UI selectors estables.
     * Ver e2e/README.md para el escenario completo. */
  });

  test.fixme("paciente abre link publico y completa Stroop", async ({ browser }) => {
    /* Pendiente: depende del test anterior (propaga el link compartido). */
  });
});
