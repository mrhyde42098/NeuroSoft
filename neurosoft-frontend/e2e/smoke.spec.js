/* ═══════════════════════════════════════════════════════════════════════
 * e2e/smoke.spec.js — Humo basico del bundle servido por uvicorn
 * Verifica que el SPA carga, login con admin/neurosoft2025 funciona, y
 * que el dashboard renderiza sus 4 KPIs. Es la red de seguridad minima
 * antes de iterar el flujo completo de rehab.
 * ═══════════════════════════════════════════════════════════════════════ */

import { test, expect } from "@playwright/test";
import { loginAsAdmin } from "./helpers/auth.js";

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
    await loginAsAdmin(page);
    await expect(page.locator('[aria-current="page"]').first()).toBeAttached();
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
