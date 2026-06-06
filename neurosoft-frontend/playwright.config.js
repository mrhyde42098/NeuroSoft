/* ═══════════════════════════════════════════════════════════════════════
 * playwright.config.js — E2E tests configuration
 * ═══════════════════════════════════════════════════════════════════════ */

import { defineConfig, devices } from "@playwright/test";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = 8765;
const BASE_URL = `http://127.0.0.1:${PORT}`;
const BACKEND_DIR = path.resolve(__dirname, "../neurosoft-backend");
const E2E_DB = "data/e2e_test.db";

function resolvePython() {
  const candidates =
    process.platform === "win32"
      ? [path.join(BACKEND_DIR, "venv/Scripts/python.exe")]
      : [path.join(BACKEND_DIR, "venv/bin/python"), path.join(BACKEND_DIR, "venv/bin/python3")];
  for (const p of candidates) {
    if (existsSync(p)) return `"${p}"`;
  }
  return process.platform === "win32" ? "python" : "python3";
}

const PY = resolvePython();

export default defineConfig({
  globalSetup: "./e2e/global-setup.js",
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
      name: "smoke",
      testMatch: "**/smoke.spec.js",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "a11y",
      testMatch: "**/a11y.spec.js",
      dependencies: ["smoke"],
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  webServer: {
    command: `${PY} -m uvicorn app.main:app --host 127.0.0.1 --port ${PORT}`,
    cwd: BACKEND_DIR,
    port: PORT,
    timeout: 120_000,
    reuseExistingServer: !process.env.CI,
    env: {
      NEUROSOFT_DB_PATH: E2E_DB,
      NEUROSOFT_ADMIN_PASSWORD: "neurosoft2025",
      NEUROSOFT_RESET_ADMIN_PASSWORD: "1",
      NEUROSOFT_RESET_BETA_PASSWORD: "1",
      NEUROSOFT_E2E: "1",
      NEUROSOFT_ENV: "development",
    },
  },
});
