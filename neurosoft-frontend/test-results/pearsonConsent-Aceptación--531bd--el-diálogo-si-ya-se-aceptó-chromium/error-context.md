# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: pearsonConsent.spec.js >> Aceptación one-time material con copyright (S5.1x) >> Recargar la página NO muestra el diálogo si ya se aceptó
- Location: e2e\pearsonConsent.spec.js:100:3

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('input[name="username"], input[autocomplete="username"]').first()

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - generic [ref=e6]:
    - img "NeuroSoft" [ref=e10]
    - heading "NeuroSoft" [level=1] [ref=e17]
    - paragraph [ref=e18]: Sistema de Gestión Neuropsicológica
    - generic [ref=e19]:
      - generic [ref=e20]:
        - generic [ref=e21]: psychology
        - generic [ref=e22]: Evaluaciones
        - generic [ref=e23]: Protocolos WISC-IV, WAIS-III
      - generic [ref=e24]:
        - generic [ref=e25]: fitness_center
        - generic [ref=e26]: Rehabilitación
        - generic [ref=e27]: Estimulación cognitiva
      - generic [ref=e28]:
        - generic [ref=e29]: description
        - generic [ref=e30]: Informes PDF
        - generic [ref=e31]: Generación automática
    - generic [ref=e32]: Evaluación + Rehabilitación
  - main [ref=e36]:
    - generic [ref=e37]:
      - heading "Bienvenido de nuevo" [level=2] [ref=e40]
      - paragraph [ref=e41]: Acceda a su entorno clínico seguro.
    - generic [ref=e42]:
      - generic [ref=e43]:
        - generic [ref=e44]: ID Profesional
        - generic [ref=e45]:
          - generic:
            - generic: badge
          - textbox "usuario" [ref=e46]
      - generic [ref=e47]:
        - generic [ref=e48]: Clave de Seguridad
        - generic [ref=e49]:
          - generic:
            - generic: lock
          - textbox "••••••••" [ref=e50]
          - button "visibility" [ref=e51] [cursor=pointer]:
            - generic [ref=e52]: visibility
      - button "Iniciar Sesión →" [ref=e53] [cursor=pointer]:
        - generic [ref=e54]: Iniciar Sesión →
    - paragraph [ref=e58]: NeuroSoft App
    - generic [ref=e60]:
      - paragraph [ref=e61]: Al iniciar sesión, el profesional confirma que cuenta con el consentimiento informado del titular para el tratamiento de sus datos de salud.
      - button "policy Política de Privacidad · Ley 1581 de 2012" [ref=e62] [cursor=pointer]:
        - generic [ref=e63]: policy
        - text: Política de Privacidad · Ley 1581 de 2012
```

# Test source

```ts
  4   |  *
  5   |  * Cobertura:
  6   |  *  - El diálogo de aceptación se muestra en el primer inicio.
  7   |  *  - El clínico debe marcar la casilla de confirmación antes de aceptar.
  8   |  *  - Una vez aceptado, el diálogo NO se vuelve a mostrar (persistencia
  9   |  *    en localStorage con VERSION_ACUERDO).
  10  |  *  - Tras revocar, vuelve a aparecer.
  11  |  *  - Al navegar a una página con un test verbatim, se muestra el
  12  |  *    SelloProtegidoBadge y el ApoyoClinicoPanel.
  13  |  *
  14  |  * Precondición: dist/ compilado (npm run build) y backend en :8765.
  15  |  */
  16  | 
  17  | import { test, expect } from "@playwright/test";
  18  | 
  19  | const STORAGE_KEY_VERSION = 'ns_pearson_consent_version';
  20  | const STORAGE_KEY_DATE = 'ns_pearson_consent_global';
  21  | 
  22  | test.describe('Aceptación one-time material con copyright (S5.1x)', () => {
  23  | 
  24  |   test.beforeEach(async ({ page, context }) => {
  25  |     // Limpiar cualquier aceptación previa para garantizar un estado limpio
  26  |     await context.clearCookies();
  27  |     await page.goto('http://localhost:8765', { waitUntil: 'domcontentloaded' });
  28  |     await page.evaluate((keys) => {
  29  |       for (const k of keys) {
  30  |         try { localStorage.removeItem(k); } catch {}
  31  |       }
  32  |     }, [STORAGE_KEY_VERSION, STORAGE_KEY_DATE]);
  33  |   });
  34  | 
  35  |   test('Muestra el diálogo la primera vez que se inicia la app', async ({ page }) => {
  36  |     // Login
  37  |     const passInput = page.locator('input[type="password"]').first();
  38  |     if (await passInput.count() > 0) {
  39  |       await page.locator('input[name="username"], input[autocomplete="username"]').first()
  40  |         .fill(process.env.NS_USER || 'admin');
  41  |       await passInput.fill(process.env.NS_PASS || 'neurosoft2025');
  42  |       await page.locator('button[type="submit"]').first().click();
  43  |       await page.waitForLoadState('domcontentloaded');
  44  |     }
  45  |     // El diálogo debe estar visible
  46  |     const dialog = page.getByRole('dialog', { name: /acuerdo de uso/i });
  47  |     await expect(dialog).toBeVisible({ timeout: 5000 });
  48  |     await expect(dialog).toContainText(/WISC-IV/);
  49  |     await expect(dialog).toContainText(/WAIS-III/);
  50  |   });
  51  | 
  52  |   test('El checkbox de confirmación es obligatorio para aceptar', async ({ page }) => {
  53  |     const passInput = page.locator('input[type="password"]').first();
  54  |     if (await passInput.count() > 0) {
  55  |       await page.locator('input[name="username"], input[autocomplete="username"]').first()
  56  |         .fill(process.env.NS_USER || 'admin');
  57  |       await passInput.fill(process.env.NS_PASS || 'neurosoft2025');
  58  |       await page.locator('button[type="submit"]').first().click();
  59  |       await page.waitForLoadState('domcontentloaded');
  60  |     }
  61  |     const dialog = page.getByRole('dialog', { name: /acuerdo de uso/i });
  62  |     await expect(dialog).toBeVisible({ timeout: 5000 });
  63  |     // Botón "Acepto" debe estar deshabilitado sin el checkbox
  64  |     const acceptBtn = dialog.getByRole('button', { name: /acepto y continúo/i });
  65  |     await expect(acceptBtn).toBeDisabled();
  66  |     // Marcar el checkbox
  67  |     const checkbox = dialog.locator('input[type="checkbox"]');
  68  |     await checkbox.check();
  69  |     // Ahora debe estar habilitado
  70  |     await expect(acceptBtn).toBeEnabled();
  71  |   });
  72  | 
  73  |   test('Aceptar persiste en localStorage con VERSION_ACUERDO', async ({ page }) => {
  74  |     const passInput = page.locator('input[type="password"]').first();
  75  |     if (await passInput.count() > 0) {
  76  |       await page.locator('input[name="username"], input[autocomplete="username"]').first()
  77  |         .fill(process.env.NS_USER || 'admin');
  78  |       await passInput.fill(process.env.NS_PASS || 'neurosoft2025');
  79  |       await page.locator('button[type="submit"]').first().click();
  80  |       await page.waitForLoadState('domcontentloaded');
  81  |     }
  82  |     const dialog = page.getByRole('dialog', { name: /acuerdo de uso/i });
  83  |     await expect(dialog).toBeVisible({ timeout: 5000 });
  84  |     await dialog.locator('input[type="checkbox"]').check();
  85  |     await dialog.getByRole('button', { name: /acepto y continúo/i }).click();
  86  | 
  87  |     // Esperar a que el diálogo se cierre
  88  |     await expect(dialog).toBeHidden({ timeout: 3000 });
  89  | 
  90  |     // Verificar localStorage
  91  |     const version = await page.evaluate((k) => localStorage.getItem(k), STORAGE_KEY_VERSION);
  92  |     const date = await page.evaluate((k) => localStorage.getItem(k), STORAGE_KEY_DATE);
  93  |     expect(version).toBeTruthy();
  94  |     expect(version).toMatch(/^\d+\.\d+\.\d+$/);
  95  |     expect(date).toBeTruthy();
  96  |     // La fecha debe ser ISO 8601
  97  |     expect(new Date(date).toString()).not.toBe('Invalid Date');
  98  |   });
  99  | 
  100 |   test('Recargar la página NO muestra el diálogo si ya se aceptó', async ({ page }) => {
  101 |     const passInput = page.locator('input[type="password"]').first();
  102 |     if (await passInput.count() > 0) {
  103 |       await page.locator('input[name="username"], input[autocomplete="username"]').first()
> 104 |         .fill(process.env.NS_USER || 'admin');
      |          ^ Error: locator.fill: Test timeout of 30000ms exceeded.
  105 |       await passInput.fill(process.env.NS_PASS || 'neurosoft2025');
  106 |       await page.locator('button[type="submit"]').first().click();
  107 |       await page.waitForLoadState('domcontentloaded');
  108 |     }
  109 |     // Aceptar
  110 |     const dialog = page.getByRole('dialog', { name: /acuerdo de uso/i });
  111 |     await expect(dialog).toBeVisible({ timeout: 5000 });
  112 |     await dialog.locator('input[type="checkbox"]').check();
  113 |     await dialog.getByRole('button', { name: /acepto y continúo/i }).click();
  114 |     await expect(dialog).toBeHidden({ timeout: 3000 });
  115 | 
  116 |     // Recargar
  117 |     await page.reload({ waitUntil: 'domcontentloaded' });
  118 | 
  119 |     // El diálogo NO debe volver a aparecer
  120 |     await page.waitForTimeout(1500);
  121 |     const dialogAfter = page.getByRole('dialog', { name: /acuerdo de uso/i });
  122 |     await expect(dialogAfter).toBeHidden();
  123 |   });
  124 | 
  125 |   test('La versión se invalida si cambia VERSION_ACUERDO', async ({ page }) => {
  126 |     // Pre-poblar localStorage con una versión obsoleta
  127 |     await page.goto('http://localhost:8765', { waitUntil: 'domcontentloaded' });
  128 |     await page.evaluate((keys) => {
  129 |       for (const k of keys) {
  130 |         try { localStorage.setItem(k, '0.0.0'); } catch {}
  131 |       }
  132 |     }, [STORAGE_KEY_VERSION]);
  133 |     // Y forzar también la fecha
  134 |     await page.evaluate((k) => {
  135 |       try { localStorage.setItem(k, new Date().toISOString()); } catch {}
  136 |     }, STORAGE_KEY_DATE);
  137 | 
  138 |     // Recargar y login
  139 |     await page.reload({ waitUntil: 'domcontentloaded' });
  140 |     const passInput = page.locator('input[type="password"]').first();
  141 |     if (await passInput.count() > 0) {
  142 |       await page.locator('input[name="username"], input[autocomplete="username"]').first()
  143 |         .fill(process.env.NS_USER || 'admin');
  144 |       await passInput.fill(process.env.NS_PASS || 'neurosoft2025');
  145 |       await page.locator('button[type="submit"]').first().click();
  146 |       await page.waitForLoadState('domcontentloaded');
  147 |     }
  148 |     // El diálogo debe mostrarse de nuevo con la nueva versión
  149 |     const dialog = page.getByRole('dialog', { name: /acuerdo de uso/i });
  150 |     await expect(dialog).toBeVisible({ timeout: 5000 });
  151 |     const versionShown = await dialog.locator('.ns-mono').first().textContent();
  152 |     expect(versionShown).toMatch(/^\d+\.\d+\.\d+$/);
  153 |     expect(versionShown).not.toBe('0.0.0');
  154 |   });
  155 | });
  156 | 
```