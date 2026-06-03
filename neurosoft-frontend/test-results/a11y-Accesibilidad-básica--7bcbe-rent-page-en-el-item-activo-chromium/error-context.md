# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: a11y.spec.js >> Accesibilidad básica (S3.3) >> Sidebar usa aria-current="page" en el item activo
- Location: e2e\a11y.spec.js:48:3

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5173/
Call log:
  - navigating to "http://localhost:5173/", waiting until "load"

```

# Test source

```ts
  1  | /**
  2  |  * S3.3: Tests de accesibilidad (A11y) — Skip link, aria-current.
  3  |  *
  4  |  * Verifica que la app cumple con los básicos de WCAG 2.1 AA:
  5  |  *  - El link "Saltar al contenido principal" es accesible por teclado
  6  |  *  - El elemento <main> tiene tabindex=-1 para recibir foco programático
  7  |  *  - Los items del Sidebar usan aria-current="page" cuando activos
  8  |  */
  9  | 
  10 | import { test, expect } from "@playwright/test";
  11 | 
  12 | test.describe('Accesibilidad básica (S3.3)', () => {
  13 |   test.beforeEach(async ({ page }) => {
  14 |     // Login
> 15 |     await page.goto('http://localhost:5173');
     |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5173/
  16 |     await page.waitForLoadState('domcontentloaded');
  17 |     const isLogin = await page.locator('input[type="password"]').count();
  18 |     if (isLogin > 0) {
  19 |       await page.locator('input[name="username"], input[autocomplete="username"]').first()
  20 |         .fill(process.env.NS_USER || 'admin');
  21 |       await page.locator('input[type="password"]').first()
  22 |         .fill(process.env.NS_PASS || 'admin');
  23 |       await page.locator('button[type="submit"]').first().click();
  24 |     }
  25 |     await page.waitForLoadState('domcontentloaded');
  26 |   });
  27 | 
  28 |   test('Skip link existe y es accesible por teclado', async ({ page }) => {
  29 |     // El link debe existir en el DOM
  30 |     const skip = page.getByRole('link', { name: /saltar al contenido principal/i });
  31 |     await expect(skip).toBeAttached();
  32 | 
  33 |     // Foco por teclado debe revelarlo (display:none → block al focus)
  34 |     await page.keyboard.press('Tab');
  35 |     // No es estrictamente verificable sin axe-core, pero verificamos
  36 |     // que el href apunte al main content.
  37 |     const href = await skip.getAttribute('href');
  38 |     expect(href).toBe('#ns-main-content');
  39 |   });
  40 | 
  41 |   test('Elemento <main> tiene id y aria-label', async ({ page }) => {
  42 |     const main = page.locator('#ns-main-content');
  43 |     await expect(main).toBeAttached();
  44 |     const aria = await main.getAttribute('aria-label');
  45 |     expect(aria).toMatch(/contenido principal/i);
  46 |   });
  47 | 
  48 |   test('Sidebar usa aria-current="page" en el item activo', async ({ page }) => {
  49 |     // Estamos en "dashboard" por default tras login
  50 |     const current = page.locator('[aria-current="page"]').first();
  51 |     await expect(current).toBeAttached();
  52 | 
  53 |     // El label debe ser "Dashboard" o similar
  54 |     const text = await current.textContent();
  55 |     expect(text).toBeTruthy();
  56 |   });
  57 | 
  58 |   test('Cambiar a "Pacientes" actualiza aria-current', async ({ page }) => {
  59 |     await page.getByRole('button', { name: /pacientes/i }).first().click();
  60 |     await page.waitForTimeout(300);
  61 |     const current = page.locator('[aria-current="page"]').first();
  62 |     const text = await current.textContent();
  63 |     expect(text).toMatch(/pacientes/i);
  64 |   });
  65 | });
  66 | 
```