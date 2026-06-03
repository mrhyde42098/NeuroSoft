import { test, expect } from "@playwright/test";

const ADMIN = { user: "admin", pass: "neurosoft2025" };

async function loginAsAdmin(page) {
  await page.goto("/");
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

test.describe("Evaluacion - orden clinico sugerido", () => {
  test("la siguiente prueba sugerida cambia al completar la codificacion", async ({ page }) => {
    await loginAsAdmin(page);

    await page.locator("button").filter({ hasText: /Aplicar evaluaci/i }).first().click();
    await page.locator("select").nth(1).selectOption("adulto_mayor");

    const nextName = page.getByTestId("clinical-next-name");
    await expect(nextName).toContainText("Grober");

    await page.getByTestId("current-score-input").fill("12");
    await expect(nextName).toContainText("FCRO");
  });
});
