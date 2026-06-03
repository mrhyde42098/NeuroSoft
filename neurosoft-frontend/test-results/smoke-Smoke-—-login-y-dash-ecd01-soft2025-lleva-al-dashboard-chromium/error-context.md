# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: smoke.spec.js >> Smoke — login y dashboard >> login admin/neurosoft2025 lleva al dashboard
- Location: e2e\smoke.spec.js:22:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('button').locator('text=Pacientes')
Expected: visible
Error: strict mode violation: locator('button').locator('text=Pacientes') resolved to 2 elements:
    1) <span class="text-[13px] font-medium">Pacientes</span> aka getByRole('button', { name: 'Pacientes', exact: true })
    2) <p class="text-sm font-bold leading-tight">Pacientes</p> aka getByRole('button', { name: 'person Pacientes Registra y' })

Call log:
  - Expect "toBeVisible" with timeout 15000ms
  - waiting for locator('button').locator('text=Pacientes')

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - link "Saltar al contenido principal" [ref=e4] [cursor=pointer]:
    - /url: "#ns-main-content"
  - complementary [ref=e5]:
    - generic [ref=e6]:
      - img [ref=e7]
      - generic [ref=e14]:
        - heading "NeuroSoft" [level=1] [ref=e15]
        - paragraph [ref=e16]: Gestión clínica
    - button "A Administrador admin expand_more" [ref=e18] [cursor=pointer]:
      - generic [ref=e19]: A
      - generic [ref=e20]:
        - paragraph [ref=e21]: Administrador
        - paragraph [ref=e22]: admin
      - generic [ref=e23]: expand_more
    - navigation [ref=e24]:
      - generic [ref=e25]:
        - paragraph [ref=e26]: Clínica
        - button "Inicio (página actual)" [ref=e27] [cursor=pointer]:
          - generic [ref=e29]: home
          - generic [ref=e30]: Inicio
        - button "Pacientes" [ref=e31] [cursor=pointer]:
          - generic [ref=e32]: group
          - generic [ref=e33]: Pacientes
        - button "Agenda" [ref=e34] [cursor=pointer]:
          - generic [ref=e35]: calendar_today
          - generic [ref=e36]: Agenda
      - generic [ref=e37]:
        - paragraph [ref=e38]: Evaluación
        - button "Aplicar evaluación" [ref=e39] [cursor=pointer]:
          - generic [ref=e40]: psychology
          - generic [ref=e41]: Aplicar evaluación
        - button "Screening" [ref=e42] [cursor=pointer]:
          - generic [ref=e43]: checklist
          - generic [ref=e44]: Screening
        - button "Historial" [ref=e45] [cursor=pointer]:
          - generic [ref=e46]: history
          - generic [ref=e47]: Historial
        - button "Pre–Post" [ref=e48] [cursor=pointer]:
          - generic [ref=e49]: compare_arrows
          - generic [ref=e50]: Pre–Post
        - button "Informes" [ref=e51] [cursor=pointer]:
          - generic [ref=e52]: description
          - generic [ref=e53]: Informes
      - generic [ref=e54]:
        - paragraph [ref=e55]: Psicoterapia
        - button "Sesiones clínicas" [ref=e56] [cursor=pointer]:
          - generic [ref=e57]: psychology_alt
          - generic [ref=e58]: Sesiones clínicas
      - generic [ref=e59]:
        - paragraph [ref=e60]: Rehabilitación
        - button "Plan & Actividades" [ref=e61] [cursor=pointer]:
          - generic [ref=e62]: fitness_center
          - generic [ref=e63]: Plan & Actividades
      - generic [ref=e64]:
        - paragraph [ref=e65]: Aprender
        - button "Centro de aprendizaje" [ref=e66] [cursor=pointer]:
          - generic [ref=e67]: school
          - generic [ref=e68]: Centro de aprendizaje
        - button "Biblioteca clínica" [ref=e69] [cursor=pointer]:
          - generic [ref=e70]: auto_stories
          - generic [ref=e71]: Biblioteca clínica
        - button "Glosario neuropsi" [ref=e72] [cursor=pointer]:
          - generic [ref=e73]: translate
          - generic [ref=e74]: Glosario neuropsi
        - button "Tarjetas estudio" [ref=e75] [cursor=pointer]:
          - generic [ref=e76]: psychology
          - generic [ref=e77]: Tarjetas estudio
        - button "Quizzes" [ref=e78] [cursor=pointer]:
          - generic [ref=e79]: quiz
          - generic [ref=e80]: Quizzes
        - button "Artículos clínicos" [ref=e81] [cursor=pointer]:
          - generic [ref=e82]: article
          - generic [ref=e83]: Artículos clínicos
        - button "Simulador de casos" [ref=e84] [cursor=pointer]:
          - generic [ref=e85]: psychology_alt
          - generic [ref=e86]: Simulador de casos
        - button "Pruebas disponibles" [ref=e87] [cursor=pointer]:
          - generic [ref=e88]: rule
          - generic [ref=e89]: Pruebas disponibles
      - generic [ref=e90]:
        - paragraph [ref=e91]: Herramientas
        - button "Asistente IA" [ref=e92] [cursor=pointer]:
          - generic [ref=e93]: smart_toy
          - generic [ref=e94]: Asistente IA
        - button "Telemedicina" [ref=e95] [cursor=pointer]:
          - generic [ref=e96]: share
          - generic [ref=e97]: Telemedicina
        - button "Ayuda" [ref=e98] [cursor=pointer]:
          - generic [ref=e99]: help
          - generic [ref=e100]: Ayuda
        - button "Registro de cambios" [ref=e101] [cursor=pointer]:
          - generic [ref=e102]: new_releases
          - generic [ref=e103]: Registro de cambios
    - generic [ref=e104]:
      - button "add Nueva evaluación" [ref=e105] [cursor=pointer]:
        - generic [ref=e106]: add
        - text: Nueva evaluación
      - generic [ref=e107]:
        - button "dark_mode Oscuro" [ref=e108] [cursor=pointer]:
          - generic [ref=e109]: dark_mode
          - text: Oscuro
        - button "zoom_out_map" [ref=e110] [cursor=pointer]:
          - generic [ref=e111]: zoom_out_map
        - button "keyboard" [ref=e112] [cursor=pointer]:
          - generic [ref=e113]: keyboard
  - main "Contenido principal" [ref=e114]:
    - generic [ref=e115]:
      - heading "Buenos días, Administrador" [level=2] [ref=e117]
      - main [ref=e118]:
        - generic [ref=e120]:
          - generic [ref=e121]:
            - paragraph [ref=e122]: Plataforma de evaluación neuropsicológica
            - heading "Buenos días, Administrador" [level=2] [ref=e123]
            - paragraph [ref=e124]: miércoles, 3 de junio de 2026
          - generic [ref=e125]:
            - generic [ref=e126]:
              - generic [ref=e127]: person
              - text: Pacientes
            - generic [ref=e128]:
              - generic [ref=e129]: clinical_notes
              - text: Evaluaciones
            - generic [ref=e130]:
              - generic [ref=e131]: checklist
              - text: Screening
            - generic [ref=e132]:
              - generic [ref=e133]: fitness_center
              - text: Rehabilitación
            - generic [ref=e134]:
              - generic [ref=e135]: psychology
              - text: Terapia
        - button "notifications Notificaciones Sin actividad reciente expand_more" [ref=e137] [cursor=pointer]:
          - generic [ref=e138]:
            - generic [ref=e140]: notifications
            - generic [ref=e141]:
              - paragraph [ref=e142]: Notificaciones
              - paragraph [ref=e143]: Sin actividad reciente
          - generic [ref=e144]: expand_more
        - generic [ref=e145]:
          - paragraph [ref=e146]: Indicadores
          - generic [ref=e147]:
            - generic [ref=e148] [cursor=pointer]:
              - generic [ref=e149]:
                - generic [ref=e150]: group
                - generic [ref=e151]: arrow_outward
              - paragraph [ref=e152]: "0"
              - paragraph [ref=e153]: Pacientes
            - generic [ref=e154]:
              - generic [ref=e156]: clinical_notes
              - paragraph [ref=e157]: "0"
              - paragraph [ref=e158]: Evaluaciones
            - generic [ref=e159] [cursor=pointer]:
              - generic [ref=e160]:
                - generic [ref=e161]: description
                - generic [ref=e162]: arrow_outward
              - paragraph [ref=e163]: "0"
              - paragraph [ref=e164]: Sin informe
            - generic [ref=e165]:
              - generic [ref=e167]: event_available
              - paragraph [ref=e168]: "0"
              - paragraph [ref=e169]: Este mes
            - generic [ref=e170]:
              - generic [ref=e172]: calendar_month
              - paragraph [ref=e173]: "0"
              - paragraph [ref=e174]: Este año
        - generic [ref=e175]:
          - generic [ref=e176]:
            - generic [ref=e177]:
              - paragraph [ref=e178]: Tendencia
              - heading "Evaluaciones aplicadas (últimos 6 meses)" [level=3] [ref=e179]
            - img [ref=e180]:
              - generic [ref=e181]: "10"
              - generic [ref=e182]: "8"
              - generic [ref=e183]: "5"
              - generic [ref=e184]: "3"
              - generic [ref=e185]: "0"
              - generic [ref=e186]:
                - generic [ref=e188]: "0"
                - generic [ref=e189]: ene
              - generic [ref=e190]:
                - generic [ref=e192]: "0"
                - generic [ref=e193]: feb
              - generic [ref=e194]:
                - generic [ref=e196]: "0"
                - generic [ref=e197]: mar
              - generic [ref=e198]:
                - generic [ref=e200]: "0"
                - generic [ref=e201]: abr
              - generic [ref=e202]:
                - generic [ref=e204]: "0"
                - generic [ref=e205]: may
              - generic [ref=e206]:
                - generic [ref=e208]: "0"
                - generic [ref=e209]: jun
          - generic [ref=e210]:
            - generic [ref=e211]:
              - paragraph [ref=e212]: Demografía
              - heading "Distribución por sexo" [level=3] [ref=e213]
            - paragraph [ref=e214]: Sin datos
        - generic [ref=e215]:
          - paragraph [ref=e216]: Módulos
          - generic [ref=e217]:
            - button "person Pacientes Registra y gestiona historias clínicas" [ref=e218] [cursor=pointer]:
              - generic [ref=e220]: person
              - generic [ref=e221]:
                - paragraph [ref=e222]: Pacientes
                - paragraph [ref=e223]: Registra y gestiona historias clínicas
            - button "clinical_notes Evaluación neuropsicológica Aplica baterías WISC-IV, WAIS-III y más de 50 pruebas" [ref=e224] [cursor=pointer]:
              - generic [ref=e226]: clinical_notes
              - generic [ref=e227]:
                - paragraph [ref=e228]: Evaluación neuropsicológica
                - paragraph [ref=e229]: Aplica baterías WISC-IV, WAIS-III y más de 50 pruebas
            - button "checklist Screening PHQ-9, GAD-7, MMSE, MoCA, SNAP-IV y otras escalas" [ref=e230] [cursor=pointer]:
              - generic [ref=e232]: checklist
              - generic [ref=e233]:
                - paragraph [ref=e234]: Screening
                - paragraph [ref=e235]: PHQ-9, GAD-7, MMSE, MoCA, SNAP-IV y otras escalas
            - button "fitness_center Rehabilitación cognitiva Planes de ejercicios y seguimiento de adherencia" [ref=e236] [cursor=pointer]:
              - generic [ref=e238]: fitness_center
              - generic [ref=e239]:
                - paragraph [ref=e240]: Rehabilitación cognitiva
                - paragraph [ref=e241]: Planes de ejercicios y seguimiento de adherencia
            - button "psychology Terapia Sesiones SOAP, enfoques CBT / ACT / EMDR y más" [ref=e242] [cursor=pointer]:
              - generic [ref=e244]: psychology
              - generic [ref=e245]:
                - paragraph [ref=e246]: Terapia
                - paragraph [ref=e247]: Sesiones SOAP, enfoques CBT / ACT / EMDR y más
            - button "calendar_today Agenda Citas, recordatorios y gestión de horarios" [ref=e248] [cursor=pointer]:
              - generic [ref=e250]: calendar_today
              - generic [ref=e251]:
                - paragraph [ref=e252]: Agenda
                - paragraph [ref=e253]: Citas, recordatorios y gestión de horarios
  - button "smart_toy" [ref=e254] [cursor=pointer]:
    - generic [ref=e255]: smart_toy
  - dialog "Material con copyright — Acuerdo de uso clínico" [ref=e256]:
    - generic [ref=e257]:
      - banner [ref=e258]:
        - generic [ref=e259]:
          - generic [ref=e260]: copyright
          - generic [ref=e261]:
            - heading "Material con copyright — Acuerdo de uso clínico" [level=2] [ref=e262]
            - paragraph [ref=e263]: "Versión del acuerdo: 1.0.0"
      - generic [ref=e264]:
        - paragraph [ref=e265]:
          - text: NeuroSoft App incluye reactivos verbatim de las pruebas
          - strong [ref=e266]: WISC-IV
          - text: "y"
          - strong [ref=e267]: WAIS-III
          - text: ", cuyo copyright pertenece a la"
          - emphasis [ref=e268]: Editorial El Manual Moderno / Pearson
          - text: . Estos reactivos son entregados
          - strong [ref=e269]: bajo licencia
          - text: al profesional y NO se distribuyen libremente.
        - generic [ref=e270]:
          - heading "Cobertura legal" [level=3] [ref=e271]
          - list [ref=e272]:
            - listitem [ref=e273]:
              - strong [ref=e274]: Ley 23 de 1982
              - text: (Colombia) — Derechos de autor.
            - listitem [ref=e275]:
              - strong [ref=e276]: Ley 44 de 1993
              - text: — Modificaciones a la Ley 23.
            - listitem [ref=e277]:
              - strong [ref=e278]: Decisión 486 de 2000
              - text: (Comunidad Andina) — Régimen Común sobre Propiedad Intelectual.
            - listitem [ref=e279]:
              - strong [ref=e280]: Tratados OMPI
              - text: (WIPO) sobre derechos de autor y obras intelectuales.
            - listitem [ref=e281]:
              - strong [ref=e282]: Contrato de licenciamiento
              - text: con Editorial El Manual Moderno / Pearson.
        - generic [ref=e283]:
          - heading "Compromisos del clínico" [level=3] [ref=e284]
          - list [ref=e285]:
            - listitem [ref=e286]: Poseo licencia válida del material (WISC-IV, WAIS-III) emitida por el editor o su distribuidor autorizado.
            - listitem [ref=e287]:
              - text: Usaré los ítems verbatim
              - strong [ref=e288]: exclusivamente con fines clínicos
              - text: (evaluación, diagnóstico, seguimiento) en el contexto de mis pacientes.
            - listitem [ref=e289]: No redistribuiré los ítems, ni los incluiré en informes, publicaciones o medios que salgan del flujo clínico-paciente.
            - listitem [ref=e290]: Conservaré los manuales originales como fuente de referencia y los consultaré ante cualquier duda sobre aplicación o baremación.
            - listitem [ref=e291]: Respetaré las condiciones de aplicación estandarizadas descritas en el manual original.
            - listitem [ref=e292]: Acepto que cada acceso a un ítem verbatim quede registrado en la bitácora de auditoría clínica del sistema.
        - generic [ref=e293]:
          - heading "Apoyo clínico incluido" [level=3] [ref=e294]
          - paragraph [ref=e295]: "Al activar este acuerdo tendrás disponible en cada prueba con ítems verbatim:"
          - list [ref=e296]:
            - listitem [ref=e297]:
              - strong [ref=e298]: Marca visual discreta
              - text: sobre cada ítem (no interrumpe la aplicación).
            - listitem [ref=e299]:
              - strong [ref=e300]: Referencia al manual original
              - text: (página, ISBN, editorial).
            - listitem [ref=e301]:
              - strong [ref=e302]: Errores frecuentes
              - text: y alternativas baremos abiertos cuando proceda.
            - listitem [ref=e303]:
              - strong [ref=e304]: Audit log
              - text: automático por cada acceso.
        - generic [ref=e305]:
          - heading "Identificación del clínico responsable" [level=3] [ref=e306]
          - textbox "Nombre completo" [ref=e307]
          - generic [ref=e308]:
            - textbox "Documento de identidad" [ref=e309]
            - textbox "Tarjeta profesional (Ley 1090/2006)" [ref=e310]
          - paragraph [ref=e311]: Estos datos se almacenan localmente en este dispositivo para registrar la aceptación. Se transmiten al backend solo como metadato de auditoría (no como PHI).
        - generic [ref=e312] [cursor=pointer]:
          - checkbox "Confirmo que he leído el acuerdo, cumplo los compromisos listados y acepto el registro de auditoría de cada acceso a ítems verbatim." [ref=e313]
          - generic [ref=e314]: Confirmo que he leído el acuerdo, cumplo los compromisos listados y acepto el registro de auditoría de cada acceso a ítems verbatim.
      - contentinfo [ref=e315]:
        - button "No acepto" [ref=e316] [cursor=pointer]
        - button "Acepto y continúo" [disabled] [ref=e317]
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
> 48 |     await expect(page.locator("button >> text=Pacientes")).toBeVisible({ timeout: 15_000 });
     |                                                            ^ Error: expect(locator).toBeVisible() failed
  49 |   });
  50 | 
  51 |   test("usuario beta entra sin permisos admin", async ({ request }) => {
  52 |     const login = await request.post("/api/v1/auth/login", {
  53 |       data: { username: "beta", password: "BetaTester2026!" },
  54 |     });
  55 |     expect(login.ok()).toBeTruthy();
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