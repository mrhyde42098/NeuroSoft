# Tests E2E — flujo Rehab end-to-end

## Estado actual
**Diferido a sesión dedicada.** Razón: instalar Playwright/Cypress + configurar el
runner + mockear el backend (o levantar uno real para CI) requiere ~2 h de trabajo
focalizado. No tiene sentido empezarlo a medias en una sesión donde se cerraron
otros 4 features.

## Lo que cubrirá esta suite cuando se construya

```
test('Flujo completo Evaluar → Rehabilitar → Tarea-casa', async ({ page }) => {
  // 1. LOGIN
  await page.goto('/');
  await page.fill('input[placeholder="usuario"]',  'admin');
  await page.fill('input[type="password"]',        'neurosoft2025');
  await page.click('button:has-text("Iniciar Sesión")');

  // 2. SELECCIONAR PACIENTE Y ABRIR EVALUACIÓN EXISTENTE
  await page.click('text=Pacientes');
  await page.click('[title="Historial"]:first');

  // 3. DESDE LOS RESULTADOS DE LA EVALUACIÓN, INICIAR REHAB
  await page.click('text=Iniciar Rehabilitación');
  // Verificar que la sugerencia se aplicó (dominios pre-seleccionados)
  await expect(page.locator('text=Mejorar atención sostenida')).toBeVisible();

  // 4. EDITAR PLAN Y FIRMAR
  await page.fill('textarea[placeholder*="objetivos"]', 'Atención sostenida y memoria de trabajo');
  await page.click('text=Guardar plan');
  await page.click('text=Firmar');
  await page.click('button:has-text("Confirmar")');

  // 5. COMPARTIR LINK PÚBLICO
  await page.click('text=Compartir');
  const url = await page.locator('div:has-text("/shared/rehab/")').textContent();

  // 6. CONTEXTO PACIENTE (sin login)
  const ctx2 = await context.browser().newContext();
  const pacientePage = await ctx2.newPage();
  await pacientePage.goto(url);

  // 7. PACIENTE REALIZA STROOP
  await pacientePage.click('text=Comenzar');                  // Intro Stroop
  // 30 ensayos: simular click en el botón ROJO (asumiendo todos rojos para test)
  for (let i = 0; i < 30; i++) {
    await pacientePage.click('button:has-text("ROJO")');
  }
  await expect(pacientePage.locator('text=¡Sesión completada!')).toBeVisible();

  // 8. CLÍNICO VE EL RESULTADO Y LA NOTIFICACIÓN
  await page.click('text=Sesiones');
  await expect(page.locator('text=tarea_casa')).toBeVisible();
  // Toast de notificación
  await expect(page.locator('text=actividad(es) de rehabilitación')).toBeVisible();

  // 9. VERIFICAR ADHERENCIA EN DASHBOARD
  await page.click('text=Inicio');
  await expect(page.locator('text=Adherencia a planes')).toBeVisible();
  await expect(page.locator('text=%').first()).toBeVisible();
});
```

## Pasos para implementar (próxima sesión)

1. `npm install -D @playwright/test`
2. `npx playwright install chromium` (o firefox/webkit)
3. Crear `playwright.config.js`:
   ```js
   export default {
     testDir: './e2e',
     use: { baseURL: 'http://localhost:8000' },
     webServer: {
       command: 'cd ../neurosoft-backend && uvicorn app.main:app --port 8000',
       port: 8000,
       reuseExistingServer: !process.env.CI,
     },
   };
   ```
4. Crear `e2e/rehab-flow.spec.js` con el escenario de arriba.
5. Crear `e2e/seed.sql` o helper que inserte un paciente + una evaluación con
   resultados bajos pre-cargados (para que la sugerencia tenga datos).
6. Añadir a `package.json`:
   ```json
   "test:e2e": "playwright test"
   ```
7. CI (GitHub Actions): añadir workflow `e2e.yml` que arranque el backend +
   levante chromium + corra los tests.

## Por qué Playwright y no Cypress
- Soporta múltiples contextos (clínico + paciente) en el mismo test.
- Trace viewer integrado para debugging.
- Más rápido en CI (un binario vs Electron).
- Auto-wait nativo: menos `waitForSelector` explícitos.

## Casos adicionales a cubrir (después del MVP)
- Plan firmado bloquea edición de `objetivos` (debe rechazar con 409).
- Link expirado → vista pública responde 410.
- Paciente sin plan activo → endpoint `/rehab/adherence/{id}` devuelve `has_plan:false`.
- Suggest sobre evaluación sin resultados bajos → lista vacía (no error).
- N-back, Fluencia y Tachado completables al menos hasta el "Listo".
