# Solicitud Codex para Open Source — NeuroSoft

Formulario: https://openai.com/es-419/form/codex-for-oss/

## Antes de enviar — UN SOLO COMANDO

Desde la carpeta del proyecto (`D:\NeuroSoftApp`):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/abrir-todo-codex-oss.ps1
```

Eso abre en el navegador (con tu sesión de GitHub ya iniciada):

1. El repo → para editar **About**
2. **3 issues** ya rellenados → solo **Submit** en cada pestaña
3. El **formulario Codex OSS** de OpenAI
4. La página del **Organization ID** (`org-...`)

### Si no estás logueado en GitHub

1. Abre https://github.com/login e inicia sesión como `mrhyde42098`
2. Vuelve a ejecutar el script de arriba

### About — qué pegar (pestaña 1)

En el engranaje ⚙ junto a **About** (columna derecha del repo):

**Description:**
```
OSS neuropsychology platform for Colombia/LATAM — clinical scoring engine, Colombian norms, PDF reports, RIPS. FastAPI + React. 1000+ tests.
```

**Topics:** `neuropsychology` `healthcare` `fastapi` `react` `python` `colombia` `open-source` `clinical-software` `sqlite` `mental-health`

→ **Save changes**

### Organization ID (pestaña OpenAI)

En platform.openai.com copia el ID que empieza con `org-...` y pégalo en el formulario.

---

## Campos del formulario

### Nombre / Apellido / Email

Completar con tus datos. Email = el de ChatGPT.

### Nombre de usuario de GitHub

```
mrhyde42098
```

### URL del repositorio de GitHub

```
https://github.com/mrhyde42098/NeuroSoft
```

### Rol

**Maintainer principal**

### ¿Por qué este repositorio es elegible?

```
Soy autor y maintainer principal de NeuroSoft: OSS Apache 2.0 para evaluación neuropsicológica offline-first en Colombia/LATAM. Repo público reciente; en beta con clínicas reales. ~1016 tests pytest, motor clínico con 173 baremos (~114k claves), FastAPI+React+desktop Windows. Cubre normas locales, RIPS 2275 y PHI on-premise. Pocos OSS especializados en neuropsicología regional; un error en baremos puede alterar un diagnóstico — mantenimiento de alta responsabilidad.
```

### Me interesa…

- [x] Codex Security
- [x] Créditos de API para mi proyecto

### Id. de organización de OpenAI

*(Pegar tu `org-...` desde platform.openai.com)*

### ¿Cómo usarás los créditos API?

```
Automatizar revisión de PRs y regresiones del motor clínico (strategies.py, baremos_loader, informes PDF); generar fixtures de casos clínicos para pytest; auditar manejo de PII antes de integraciones IA; documentación y scripts de release (PyInstaller/Inno Setup); triage de issues de beta testers. Objetivo: reducir carga de mantenimiento de un solo maintainer sin bajar el rigor clínico ni la trazabilidad de baremos.
```

### ¿Hay algo más que debamos tomar en cuenta?

```
Mantenedor único con años de desarrollo antes de publicar en GitHub (0★ hoy). Proyecto nicho pero crítico: flujo HC→screening→evaluación WISC/WAIS→informe NPS con baremos colombianos. CI con pytest+ESLint. Codex Security es prioritario: JWT, soft-delete de historias (Res. 1995), redactor PII en logs (Ley 1581), consentimiento informado. No es dispositivo médico certificado; herramienta de apoyo profesional.
```

---

## Issues sugeridos (crear en GitHub → Issues → New issue)

### 1. Roadmap — E2E paciente → WISC → informe PDF

**Título:** `[roadmap]: E2E Playwright paciente → evaluación → informe Pro`

**Cuerpo:**
```
Flujo crítico de regresión antes de releases beta.

- [ ] Crear paciente sintético
- [ ] Aplicar subtest WISC con baremo conocido
- [ ] Generar informe Pro y validar CI esperado

Ref: docs/ESTADO_VIVO.md
```

### 2. Roadmap — Etiquetas de pacientes (QW-6)

**Título:** `[roadmap]: Etiquetas/tags en panel de pacientes`

**Cuerpo:**
```
Quick win pendiente del roadmap 2026. Permitir filtrar pacientes por etiquetas
clínicas (TDAH, adulto mayor, remisión EPS, etc.).

Prioridad: P1
```

### 3. Feature — REACTIVOS WISC/WAIS visuales

**Título:** `[feature]: Placeholders visuales de estímulos WISC/WAIS en evaluación`

**Cuerpo:**
```
Mejorar fidelidad del flujo de aplicación mostrando estímulos desde
stimuli_manifest.json. Sin copiar material con copyright en el repo.

Ref: docs/stimuli/STIMULI_INVENTORY.md
```
