/* Helpers compartidos E2E — login contra backend uvicorn (playwright baseURL). */
import { expect } from "@playwright/test";

export async function loginAsAdmin(page) {
  await page.goto("/");
  await page.evaluate(async () => {
    if ("serviceWorker" in navigator) {
      const regs = await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.map((r) => r.unregister()));
    }
  });

  const user = process.env.NS_USER || "admin";
  const pass = process.env.NS_PASS || "neurosoft2025";

  await page.fill('input[placeholder="usuario"]', user);
  await page.fill('input[type="password"]', pass);

  const loginResp = page.waitForResponse(
    (r) => r.url().includes("/api/v1/auth/login"),
    { timeout: 15_000 },
  );
  await page.locator('input[type="password"]').press("Enter");
  const resp = await loginResp;
  expect(resp.status()).toBe(200);

  await expect(page.locator("button >> text=Pacientes")).toBeVisible({ timeout: 15_000 });
}
