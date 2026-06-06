/**
 * S3.3: Tests de accesibilidad (A11y) — Skip link, aria-current.
 */
import { test, expect } from "@playwright/test";
import { loginAsAdmin } from "./helpers/auth.js";

test.describe("Accesibilidad básica (S3.3)", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test("Skip link existe y es accesible por teclado", async ({ page }) => {
    const skip = page.getByRole("link", { name: /saltar al contenido principal/i });
    await expect(skip).toBeAttached();
    await page.keyboard.press("Tab");
    const href = await skip.getAttribute("href");
    expect(href).toBe("#ns-main-content");
  });

  test("Elemento <main> tiene id y aria-label", async ({ page }) => {
    const main = page.locator("#ns-main-content");
    await expect(main).toBeAttached();
    const aria = await main.getAttribute("aria-label");
    expect(aria).toMatch(/contenido principal/i);
  });

  test('Sidebar usa aria-current="page" en el item activo', async ({ page }) => {
    const current = page.locator('[aria-current="page"]').first();
    await expect(current).toBeAttached();
    const text = await current.textContent();
    expect(text).toBeTruthy();
  });

  test('Cambiar a "Pacientes" actualiza aria-current', async ({ page }) => {
    await page.getByRole("button", { name: /pacientes/i }).first().click();
    await expect(page.locator('[aria-current="page"]').first()).toHaveText(/pacientes/i, {
      timeout: 5_000,
    });
  });
});
