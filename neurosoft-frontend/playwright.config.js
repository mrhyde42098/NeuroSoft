/* ═══════════════════════════════════════════════════════════════════════
 * playwright.config.js — E2E tests configuration
 * ───────────────────────────────────────────────────────────────────────
 * Levanta el backend uvicorn en :8765 con una BD aislada (e2e_test.db) y
 * el bundle production de Vite servido desde dist/. Los tests viven en
 * ./e2e/*.spec.js.
 *
 * Variables de entorno inyectadas al backend:
 *   • NEUROSOFT_DB_PATH=data/e2e_test.db    → BD descartable
 *   • NEUROSOFT_ADMIN_PASSWORD=neurosoft2025 → credencial conocida
 *   • NEUROSOFT_ENV=development              → bypass producción
 *
 * NOTA: la suite asume que `dist/` ya está compilado (npm run build).
 * Si no existe, Playwright fallará con "frontend dist not found".
 * ═══════════════════════════════════════════════════════════════════════ */

import { defineConfig, devices } from "@playwright/test";

const PORT = 8765;
const BASE_URL = `http://127.0.0.1:${PORT}`;

export default defineConfig({
  testDir: "./e2e",
  testMatch: /.*\.spec\.js$/,
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],

  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  webServer: {
    command: [
      "..\\neurosoft-backend\\venv\\Scripts\\python -m uvicorn app.main:app",
      `--host 127.0.0.1 --port ${PORT}`,
    ].join(" "),
    cwd: "../neurosoft-backend",
    port: PORT,
    timeout: 60_000,
    reuseExistingServer: !process.env.CI,
    env: {
      NEUROSOFT_DB_PATH: "data/e2e_test.db",
      NEUROSOFT_ADMIN_PASSWORD: "neurosoft2025",
      NEUROSOFT_RESET_ADMIN_PASSWORD: "1",
      NEUROSOFT_RESET_BETA_PASSWORD: "1",
      NEUROSOFT_ENV: "development",
    },
  },
});
