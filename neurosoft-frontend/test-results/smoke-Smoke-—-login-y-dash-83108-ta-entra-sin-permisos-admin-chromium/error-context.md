# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: smoke.spec.js >> Smoke — login y dashboard >> usuario beta entra sin permisos admin
- Location: e2e\smoke.spec.js:51:3

# Error details

```
Error: expect(received).toBeTruthy()

Received: false
```

# Test source

```ts
  1  | /* ═══════════════════════════════════════════════════════════════════════
  2  |  * e2e/smoke.spec.js — Humo basico del bundle servido por uvicorn
  3  |  * Verifica que el SPA carga, login con admin/neurosoft2025 funciona, y
  4  |  * que el dashboard renderiza sus 4 KPIs. Es la red de seguridad minima
  5  |  * antes de iterar el flujo completo de rehab.
  6  |  * ═══════════════════════════════════════════════════════════════════════ */
  7  | 
  8  | import { test, expect } from "@playwright/test";
  9  | 
  10 | test.describe("Smoke — login y dashboard", () => {
  11 |   test("backend esta vivo (health endpoint)", async ({ request }) => {
  12 |     const r = await request.get("/health");
  13 |     expect(r.ok()).toBeTruthy();
  14 |   });
  15 | 
  16 |   test("la pagina de login se renderiza", async ({ page }) => {
  17 |     await page.goto("/");
  18 |     await expect(page.locator('input[placeholder="usuario"]')).toBeVisible();
  19 |     await expect(page.locator('input[type="password"]')).toBeVisible();
  20 |   });
  21 | 
  22 |   test("login admin/neurosoft2025 lleva al dashboard", async ({ page }) => {
  23 |     await page.goto("/");
  24 |     /* Desregistrar el service worker antes del flujo: cachea el bundle
  25 |      * y puede interceptar la POST de login en la primera carga. */
  26 |     await page.evaluate(async () => {
  27 |       if ("serviceWorker" in navigator) {
  28 |         const regs = await navigator.serviceWorker.getRegistrations();
  29 |         await Promise.all(regs.map((r) => r.unregister()));
  30 |       }
  31 |     });
  32 | 
  33 |     await page.fill('input[placeholder="usuario"]', "admin");
  34 |     await page.fill('input[type="password"]', "neurosoft2025");
  35 | 
  36 |     const loginResp = page.waitForResponse(
  37 |       (r) => r.url().includes("/api/v1/auth/login"),
  38 |       { timeout: 15_000 },
  39 |     );
  40 |     /* `Enter` en el password dispara el submit del form sin depender del
  41 |      * estado disabled del boton submit (que se vuelve true durante el
  42 |      * fetch). */
  43 |     await page.locator('input[type="password"]').press("Enter");
  44 |     const resp = await loginResp;
  45 |     expect(resp.status()).toBe(200);
  46 | 
  47 |     /* Tras login el sidebar muestra los items principales. */
  48 |     await expect(page.locator("button >> text=Pacientes")).toBeVisible({ timeout: 15_000 });
  49 |   });
  50 | 
  51 |   test("usuario beta entra sin permisos admin", async ({ request }) => {
  52 |     const login = await request.post("/api/v1/auth/login", {
  53 |       data: { username: "beta", password: "BetaTester2026!" },
  54 |     });
> 55 |     expect(login.ok()).toBeTruthy();
     |                        ^ Error: expect(received).toBeTruthy()
  56 |     const body = await login.json();
  57 |     expect(body.role).toBe("profesional");
  58 | 
  59 |     const headers = { Authorization: `Bearer ${body.access_token}` };
  60 |     const panel = await request.get("/api/v1/patients/panel", { headers });
  61 |     expect(panel.ok()).toBeTruthy();
  62 | 
  63 |     const adminKpis = await request.get("/api/v1/admin/kpis", { headers });
  64 |     expect(adminKpis.status()).toBe(403);
  65 |   });
  66 | });
  67 | 
```