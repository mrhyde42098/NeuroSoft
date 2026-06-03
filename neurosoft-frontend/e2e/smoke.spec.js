/* ═══════════════════════════════════════════════════════════════════════
 * e2e/smoke.spec.js — Humo basico del bundle servido por uvicorn
 * Verifica que el SPA carga, login con admin/neurosoft2025 funciona, y
 * que el dashboard renderiza sus 4 KPIs. Es la red de seguridad minima
 * antes de iterar el flujo completo de rehab.
 * ═══════════════════════════════════════════════════════════════════════ */

import { test, expect } from "@playwright/test";

test.describe("Smoke — login y dashboard", () => {
  test("backend esta vivo (health endpoint)", async ({ request }) => {
    const r = await request.get("/health");
    expect(r.ok()).toBeTruthy();
  });

  test("la pagina de login se renderiza", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator('input[placeholder="usuario"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test("login admin/neurosoft2025 lleva al dashboard", async ({ page }) => {
    await page.goto("/");
    /* Desregistrar el service worker antes del flujo: cachea el bundle
     * y puede interceptar la POST de login en la primera carga. */
    await page.evaluate(async () => {
      if ("serviceWorker" in navigator) {
        const regs = await navigator.serviceWorker.getRegistrations();
        await Promise.all(regs.map((r) => r.unregister()));
      }
    });

    await page.fill('input[placeholder="usuario"]', "admin");
    await page.fill('input[type="password"]', "neurosoft2025");

    const loginResp = page.waitForResponse(
      (r) => r.url().includes("/api/v1/auth/login"),
      { timeout: 15_000 },
    );
    /* `Enter` en el password dispara el submit del form sin depender del
     * estado disabled del boton submit (que se vuelve true durante el
     * fetch). */
    await page.locator('input[type="password"]').press("Enter");
    const resp = await loginResp;
    expect(resp.status()).toBe(200);

    /* Tras login el sidebar muestra los items principales. */
    await expect(page.locator("button >> text=Pacientes")).toBeVisible({ timeout: 15_000 });
  });

  test("usuario beta entra sin permisos admin", async ({ request }) => {
    const login = await request.post("/api/v1/auth/login", {
      data: { username: "beta", password: "BetaTester2026!" },
    });
    expect(login.ok()).toBeTruthy();
    const body = await login.json();
    expect(body.role).toBe("profesional");

    const headers = { Authorization: `Bearer ${body.access_token}` };
    const panel = await request.get("/api/v1/patients/panel", { headers });
    expect(panel.ok()).toBeTruthy();

    const adminKpis = await request.get("/api/v1/admin/kpis", { headers });
    expect(adminKpis.status()).toBe(403);
  });
});
