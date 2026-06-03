# CLAUDE.md — NeuroSoft Frontend

## Qué es esto
Frontend React/Vite del sistema de evaluación neuropsicológica NeuroSoft.
Es una **SPA** (Single Page App) que se comunica con el backend FastAPI en `http://localhost:8000`.
En producción empaquetada como app desktop via pywebview + PyInstaller (via `build.py` en la raíz). NO usa Electron ni Tauri.

---

## Comandos esenciales

```bash
# Instalar dependencias
npm install

# Servidor de desarrollo (puerto 5173)
npm run dev

# Build de producción
npm run build

# Tests e2e (Playwright)
npm run test:e2e

# Verificar tipos/lint
npx vite build --mode development   # confirma que compila
```

---

## Estructura de carpetas

```
src/
├── api/
│   └── client.js              ← cliente HTTP (axios-like), gestiona token JWT
├── app/                       ← páginas por dominio
│   ├── agenda/                ← citas / calendario
│   ├── auth/                  ← login
│   ├── compartir/
│   │   └── PanelCompartir.jsx ← compartir informes vía link (telemedicina)
│   ├── config/                ← ajustes, formatos, plantillas, accesibilidad
│   ├── dashboard/             ← panel principal con KPIs
│   ├── evaluation/            ← aplicación de evaluación (núcleo)
│   │   ├── EvalApplyPage.jsx  ← cronómetro + reactivos + guía lateral
│   │   ├── EvalResultsPage.jsx← scoring + redacción de informe
│   │   ├── ReactivePanel.jsx  ← captura ítem por ítem (REACTIVOS)
│   │   ├── ScreeningPage.jsx  ← escalas de tamizaje (screening.js)
│   │   └── ...                ← otros componentes de evaluación
│   ├── history/               ← historial + comparativo longitudinal
│   ├── ia/
│   │   └── PanelIA.jsx        ← asistente IA (AIConfigPage, AIFloatingChat, improveWithAI)
│   ├── layout/
│   │   └── Sidebar.jsx        ← sidebar de navegación principal
│   ├── patients/              ← registro, HC, consentimiento
│   ├── rehab/                 ← rehabilitación cognitiva
│   │   ├── RehabPage.jsx      ← página principal de rehab + ACTIVITY_COMPONENTS
│   │   └── *Activity.jsx      ← componentes de actividades (CPT, GoNoGo, etc.)
│   └── reports/
│       └── InformesPage.jsx   ← listado de informes generados
├── contexts.jsx               ← AuthProvider, DarkProvider, ToastProvider, A11yProvider
├── data/                      ← datos clínicos y estímulos estáticos
│   ├── clinical.js            ← OBS_TEMPLATES, CONDUCTAS, GUIA_HC, REACTIVOS, INSTRUCCIONES
│   ├── datosClinicos.js       ← RECOMMENDATIONS_LIB, DIAGNOSTIC_ALGORITHMS, DSM5_DIAGNOSES
│   ├── index.js               ← barrel export de datos clínicos
│   ├── IndicesCI.jsx          ← cálculo y panel IQ (IQPanel)
│   ├── PatronesCubos.jsx      ← SVG estímulos Diseño con Cubos (CubosPattern, CubosPoster)
│   ├── PatronFCRO.jsx         ← SVG Figura Compleja de Rey-Osterrieth (FCROFigure)
│   ├── screening.js           ← escalas de tamizaje (SCREENING_FORMS)
│   ├── stimuli.jsx            ← NativeStimuli: mapa testId → componente visual
│   └── ui.js                  ← REPORT_TEMPLATES, DISCREPANCY_PAIRS, SHORTCUTS
├── ui/                        ← sistema de diseño (sin lógica de negocio)
│   ├── primitives.jsx         ← I, Card, Btn, Input, Sel, Txta, Label, TopBar, MsgBanner
│   └── tokens.js              ← TEAL, NAVY, CREAM, COLORS, SIZES
└── utils/                     ← helpers puros
    ├── colores.js             ← lc() — color por nivel de interpretación clínica
    ├── pediatricValidator.js  ← validaciones para evaluación pediátrica
    ├── rci.js                 ← Reliable Change Index (confiabilidad del cambio)
    ├── sattlerShortForms.js   ← formas breves y estimación de CIT (Sattler)
    └── wiscDiscrepancy.js     ← discrepancias WISC-IV/WAIS-III (ICG, ICC)
```

---

## Sistema de diseño — reglas

### Componentes UI
Importar SIEMPRE de `../../ui/primitives.jsx`. Nunca crear botones/inputs inline.

```jsx
import { Btn, Card, I, Input, Label, MsgBanner, Sel, TopBar, Txta } from "../../ui/primitives.jsx";
```

### Colores
- Token principal: `TEAL = "#0D9488"` — importar de `../../ui/tokens.js`
- Variables CSS `--ns-*` para superficies, texto, bordes (se invierten en dark mode)
- Clase `.high-contrast` en `<html>` para accesibilidad (gestionada por A11yProvider)

### Iconos
Material Symbols Outlined. Usar el componente `<I name="nombre_icono" />`.
Con fill: `<I name="task_alt" fill />`.

---

## Contextos globales

| Hook | Qué provee |
|---|---|
| `useAuth()` | `user`, `token`, `login()`, `logout()` |
| `useDark()` | `dark`, `setDark()` |
| `useToast()` | `toast(msg, type)` — tipos: success, error, warn, info |
| `useA11y()` | `highContrast`, `fontScale`, `setHighContrast()`, `setFontScale()` |

Todos en `src/contexts.jsx`. Wrappers en `App.jsx` en orden:
`A11yProvider > DarkProvider > ToastProvider > AuthProvider`.

---

## Datos clínicos — dónde está cada cosa

| Constante | Archivo | Descripción |
|---|---|---|
| `REACTIVOS` | `data/clinical.js` | Ítems por subtest para captura ítem por ítem |
| `CONDUCTAS` | `data/clinical.js` | Listas de conductas observables por subtest |
| `INSTRUCCIONES` | `data/clinical.js` | Instrucciones estándar por subtest |
| `OBS_TEMPLATES` | `data/clinical.js` | Plantillas de observaciones narrativas |
| `GUIA_HC` | `data/clinical.js` | Guía de historia clínica |
| `GUIA_INFORME` | `data/clinical.js` | Guía de redacción de informe |
| `SCREENING_FORMS` | `data/screening.js` | Escalas de tamizaje (BAI, HADS, BARTHEL, etc.) |
| `REPORT_TEMPLATES` | `data/ui.js` | Plantillas de informe (estándar, pediátrico, retest…) |
| `RECOMMENDATIONS_LIB` | `data/datosClinicos.js` | Biblioteca de recomendaciones por cuadro clínico |
| `DSM5_DIAGNOSES` | `data/datosClinicos.js` | Impresiones diagnósticas DSM-5/CIE-10 |

---

## Rehabilitación cognitiva — cómo agregar actividades

1. Crear `src/app/rehab/NombreActividad.jsx` con props `{ params, onFinish, onCancel }`.
2. Agregar el slug al mapa `ACTIVITY_COMPONENTS` en `RehabPage.jsx`.
3. Agregar la entrada a `DEFAULT_ACTIVITIES` en el backend (`rehab_use_cases.py`).

Actividades actuales: `stroop`, `n_back`, `fluency_verbal`, `tachado`, `corsi_forward`,
`corsi_backward`, `mental_rotation`, `ekman_recognition`, `spaced_retrieval`,
`cpt`, `go_no_go`, `set_shifting`, `denominacion_claves`,
`tower_of_london`, `mente_ojos`, `avd_dinero`.

---

## Escalas de tamizaje — cómo agregar una

1. En `data/screening.js`, agregar un objeto al array `SCREENING_FORMS`.
2. Tipos soportados: `binary_domains` (sí/no por dominio) y `likert_flat` (escala Likert plana).
3. En `app/evaluation/ScreeningPage.jsx`, agregar el dominio al grupo correcto en `SELECTOR_GROUPS`.

---

## Rutas de la SPA

La navegación es con estado (`setPage`) en `App.jsx`, no React Router.
Las rutas públicas (sin auth) son `/rehab/public/:token` y `/shared/view/:token`.

---

## Backend

- Dev: `http://localhost:8000`
- Prod: mismo origen (Vite proxy)
- Auth: Bearer JWT en `localStorage` con clave `ns_token`
- El cliente HTTP está en `src/api/client.js`

---

## Notas importantes

- No hay TypeScript. El proyecto usa JSX puro.
- Tailwind CSS + CSS custom properties (`--ns-*`). No usar estilos inline para colores de marca.
- `lc(interpretacion)` en `utils/colores.js` devuelve el color hex por nivel clínico.
- El `build.py` en la raíz empaqueta frontend + backend en un `.exe` usando PyInstaller.
- Tests e2e con Playwright en `e2e/`.

---

## Componentes nuevos (mayo 2026 — sprint quick wins + mejoras)

### Config + Comunicaciones
- `app/config/ComunicacionesTab.jsx` — tab "Comunicaciones" (índice 12) en `ConfigPage`. Form SMTP + sub-tab "Plantillas" (informe/remisión/evolución/RIPS/recordatorio/otro). Endpoint `/api/v1/config/smtp` y `/api/v1/config/email-templates`.

### Terapia + Riesgo
- `app/therapy/EnfoqueDetalle.jsx` — panel académico extendido (7 tabs). Open al doble click o "Ver más" en `CatalogoModal` de `TherapyPage`. CBT/ACT/EMDR tienen contenido completo; resto muestran "en preparación".
- `app/therapy/CSSRSForm.jsx` — modal C-SSRS con 6 preguntas escalonadas (leve→inminente) + cálculo automático nivel + plan de seguridad (Stanley & Brown) + contactos crisis Colombia (192-4, 106, 123).

### Pacientes
- `app/patients/CompanionsSection.jsx` — sección de acompañantes embebida en `ClinicalHistoryPage`. CRUD con autorizaciones (responder escalas proxy, recibir recordatorios), marca de "principal".
- `app/patients/ScreeningSugeridoBox.jsx` — caja standalone (complementaria a `BandejaEscalasSugeridas`) con sugerencias data-driven.

### Evaluación + Orden clínico
- `app/evaluation/OrdenClinicoBanner.jsx` — banner reactivo en `EvalApplyPage` con siguiente paso recomendado del protocolo + timer del intervalo de recobro (≥20 min) + detección de interferencias.

### Informes
- `app/reports/InformesPage.jsx` mejorada — botones Imprimir/Guardar como/Email + modal email completo + **completitud detallada por sección con bloqueos visibles** + botón descarga deshabilitado si CRÍTICO falta.

### Datos clínicos nuevos
- `data/screeningSugerencias.js` — `REGLAS_SCREENING` (14 reglas) + `sugerirScreenings()` data-driven (MC + edad + población → IDs de screening).
- `data/protocolosOrden.js` — `PROTOCOLOS_ORDEN` (3 protocolos: adulto_mayor, adulto_joven, infantil_wisc) con `orden_recomendado`, `pares_codificacion_recobro`, `interferencias`. Helpers: `protocoloParaTest()`, `parRecobroPara()`, `siguienteTestRecomendado()`, `detectarInterferencia()`.
- `data/enfoquesTerapeuticos.js` enriquecido — 3 enfoques piloto (CBT/ACT/EMDR) con campos extendidos: `descripcion_extendida`, `efecto_tamano`, `fases_aplicacion`, `tecnicas_detalladas`, `videos`, `bibliografia`, `casos_practicos`, `recursos_descargables`.
