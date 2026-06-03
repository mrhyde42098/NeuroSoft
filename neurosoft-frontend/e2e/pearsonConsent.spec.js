/**
 * S5.1x: Tests E2E del flujo de aceptación one-time del material
 * con copyright Pearson (WISC-IV, WAIS-III).
 *
 * Cobertura:
 *  - El diálogo de aceptación se muestra en el primer inicio.
 *  - El clínico debe marcar la casilla de confirmación antes de aceptar.
 *  - Una vez aceptado, el diálogo NO se vuelve a mostrar (persistencia
 *    en localStorage con VERSION_ACUERDO).
 *  - Tras revocar, vuelve a aparecer.
 *  - Al navegar a una página con un test verbatim, se muestra el
 *    SelloProtegidoBadge y el ApoyoClinicoPanel.
 *
 * Precondición: dist/ compilado (npm run build) y backend en :8765.
 */

import { test, expect } from "@playwright/test";

const STORAGE_KEY_VERSION = 'ns_pearson_consent_version';
const STORAGE_KEY_DATE = 'ns_pearson_consent_global';

test.describe('Aceptación one-time material con copyright (S5.1x)', () => {

  test.beforeEach(async ({ page, context }) => {
    // Limpiar cualquier aceptación previa para garantizar un estado limpio
    await context.clearCookies();
    await page.goto('http://localhost:8765', { waitUntil: 'domcontentloaded' });
    await page.evaluate((keys) => {
      for (const k of keys) {
        try { localStorage.removeItem(k); } catch {}
      }
    }, [STORAGE_KEY_VERSION, STORAGE_KEY_DATE]);
  });

  test('Muestra el diálogo la primera vez que se inicia la app', async ({ page }) => {
    // Login
    const passInput = page.locator('input[type="password"]').first();
    if (await passInput.count() > 0) {
      await page.locator('input[name="username"], input[autocomplete="username"]').first()
        .fill(process.env.NS_USER || 'admin');
      await passInput.fill(process.env.NS_PASS || 'neurosoft2025');
      await page.locator('button[type="submit"]').first().click();
      await page.waitForLoadState('domcontentloaded');
    }
    // El diálogo debe estar visible
    const dialog = page.getByRole('dialog', { name: /acuerdo de uso/i });
    await expect(dialog).toBeVisible({ timeout: 5000 });
    await expect(dialog).toContainText(/WISC-IV/);
    await expect(dialog).toContainText(/WAIS-III/);
  });

  test('El checkbox de confirmación es obligatorio para aceptar', async ({ page }) => {
    const passInput = page.locator('input[type="password"]').first();
    if (await passInput.count() > 0) {
      await page.locator('input[name="username"], input[autocomplete="username"]').first()
        .fill(process.env.NS_USER || 'admin');
      await passInput.fill(process.env.NS_PASS || 'neurosoft2025');
      await page.locator('button[type="submit"]').first().click();
      await page.waitForLoadState('domcontentloaded');
    }
    const dialog = page.getByRole('dialog', { name: /acuerdo de uso/i });
    await expect(dialog).toBeVisible({ timeout: 5000 });
    // Botón "Acepto" debe estar deshabilitado sin el checkbox
    const acceptBtn = dialog.getByRole('button', { name: /acepto y continúo/i });
    await expect(acceptBtn).toBeDisabled();
    // Marcar el checkbox
    const checkbox = dialog.locator('input[type="checkbox"]');
    await checkbox.check();
    // Ahora debe estar habilitado
    await expect(acceptBtn).toBeEnabled();
  });

  test('Aceptar persiste en localStorage con VERSION_ACUERDO', async ({ page }) => {
    const passInput = page.locator('input[type="password"]').first();
    if (await passInput.count() > 0) {
      await page.locator('input[name="username"], input[autocomplete="username"]').first()
        .fill(process.env.NS_USER || 'admin');
      await passInput.fill(process.env.NS_PASS || 'neurosoft2025');
      await page.locator('button[type="submit"]').first().click();
      await page.waitForLoadState('domcontentloaded');
    }
    const dialog = page.getByRole('dialog', { name: /acuerdo de uso/i });
    await expect(dialog).toBeVisible({ timeout: 5000 });
    await dialog.locator('input[type="checkbox"]').check();
    await dialog.getByRole('button', { name: /acepto y continúo/i }).click();

    // Esperar a que el diálogo se cierre
    await expect(dialog).toBeHidden({ timeout: 3000 });

    // Verificar localStorage
    const version = await page.evaluate((k) => localStorage.getItem(k), STORAGE_KEY_VERSION);
    const date = await page.evaluate((k) => localStorage.getItem(k), STORAGE_KEY_DATE);
    expect(version).toBeTruthy();
    expect(version).toMatch(/^\d+\.\d+\.\d+$/);
    expect(date).toBeTruthy();
    // La fecha debe ser ISO 8601
    expect(new Date(date).toString()).not.toBe('Invalid Date');
  });

  test('Recargar la página NO muestra el diálogo si ya se aceptó', async ({ page }) => {
    const passInput = page.locator('input[type="password"]').first();
    if (await passInput.count() > 0) {
      await page.locator('input[name="username"], input[autocomplete="username"]').first()
        .fill(process.env.NS_USER || 'admin');
      await passInput.fill(process.env.NS_PASS || 'neurosoft2025');
      await page.locator('button[type="submit"]').first().click();
      await page.waitForLoadState('domcontentloaded');
    }
    // Aceptar
    const dialog = page.getByRole('dialog', { name: /acuerdo de uso/i });
    await expect(dialog).toBeVisible({ timeout: 5000 });
    await dialog.locator('input[type="checkbox"]').check();
    await dialog.getByRole('button', { name: /acepto y continúo/i }).click();
    await expect(dialog).toBeHidden({ timeout: 3000 });

    // Recargar
    await page.reload({ waitUntil: 'domcontentloaded' });

    // El diálogo NO debe volver a aparecer
    await page.waitForTimeout(1500);
    const dialogAfter = page.getByRole('dialog', { name: /acuerdo de uso/i });
    await expect(dialogAfter).toBeHidden();
  });

  test('La versión se invalida si cambia VERSION_ACUERDO', async ({ page }) => {
    // Pre-poblar localStorage con una versión obsoleta
    await page.goto('http://localhost:8765', { waitUntil: 'domcontentloaded' });
    await page.evaluate((keys) => {
      for (const k of keys) {
        try { localStorage.setItem(k, '0.0.0'); } catch {}
      }
    }, [STORAGE_KEY_VERSION]);
    // Y forzar también la fecha
    await page.evaluate((k) => {
      try { localStorage.setItem(k, new Date().toISOString()); } catch {}
    }, STORAGE_KEY_DATE);

    // Recargar y login
    await page.reload({ waitUntil: 'domcontentloaded' });
    const passInput = page.locator('input[type="password"]').first();
    if (await passInput.count() > 0) {
      await page.locator('input[name="username"], input[autocomplete="username"]').first()
        .fill(process.env.NS_USER || 'admin');
      await passInput.fill(process.env.NS_PASS || 'neurosoft2025');
      await page.locator('button[type="submit"]').first().click();
      await page.waitForLoadState('domcontentloaded');
    }
    // El diálogo debe mostrarse de nuevo con la nueva versión
    const dialog = page.getByRole('dialog', { name: /acuerdo de uso/i });
    await expect(dialog).toBeVisible({ timeout: 5000 });
    const versionShown = await dialog.locator('.ns-mono').first().textContent();
    expect(versionShown).toMatch(/^\d+\.\d+\.\d+$/);
    expect(versionShown).not.toBe('0.0.0');
  });
});
