# 🔍 Auditoría extensa NeuroSoft App — 2026-05-15

## Resumen ejecutivo

| Categoría | Estado | Acciones recomendadas |
|---|:---:|---|
| 🐛 Bugs críticos | 🟢 0 | Mantener (audit hace 2h confirmó 0 bugs nuevos) |
| 🎨 Consistencia UI | 🟡 | 41 botones sin aria-label, dark-mode con casos puntuales |
| 📐 Deuda técnica | 🟡 | 8 archivos >700 líneas, candidatos a split |
| 🧪 Cobertura tests | 🔴 ~20% | Críticamente baja para software médico |
| ⚡ Performance | 🟡 | Bundle 795 KB sin code splitting |
| 🏗 Arquitectura | 🟢 | Clean Architecture sólida, lista para expansión con refactor menor |
| 📚 Documentación | 🟢 | CLAUDE.md por módulo, memoria consolidada |
| 🌐 Accesibilidad | 🟡 | aria-label faltantes, focus visible OK |

---

# 🐛 FCRO — Bug arreglado (esta sesión)

`neurosoft-frontend/src/data/PatronFCRO.jsx` tenía 4 bugs:

1. **Rombo duplicado** (idx=13): dos polígonos solapados → líneas extra → ahora 1 solo rombo
2. **3 conectores artificiales** (cruz→rect, cuadrado→rect, segmento→rect): no son parte del estándar Taylor → removidos
3. **`fill="currentColor"`** en los 3 puntos del círculo (idx=10): no se mostraban correctamente → ahora `fill={stroke}` explícito
4. **Stroke 1.8** apenas visible → ahora **2.2** con `strokeLinecap="round"` y `strokeLinejoin="round"` para mejor renderizado

Verificado: build limpio en 5.61 s. La figura ahora se ve correcta tanto en pantalla como en informes PDF.

---

# 🎨 Auditoría UI

## CRIT-1 · Accesibilidad: 41 botones con icono sin `aria-label`
**Severidad**: media-alta (afecta lectores de pantalla)

Patrón frecuente:
```jsx
<button onClick={() => setOpen(true)}><I name="settings"/></button>
```

Debería ser:
```jsx
<button onClick={() => setOpen(true)} aria-label="Abrir configuración"><I name="settings"/></button>
```

Archivos afectados (top): `Sidebar.jsx`, `EvalApplyPage.jsx`, `PatientsPage.jsx`, `ComparePage.jsx`, `PanelIA.jsx`, `RehabPage.jsx`.

**Solución sugerida**: barrido sistemático. Estimación: 30-45 min para todos.

## CRIT-2 · Inputs sueltos en `PanelCompartir.jsx` sin `<Label>`
**Severidad**: baja-media

5 inputs nativos sin `<Label>` envolvente. Hace más difícil el accesso por teclado y la asociación visual etiqueta-campo.

Archivos: `PanelCompartir.jsx` (4), `BackupTab.jsx` (1).

## ALTA-1 · Modo proyección no testeado en pantalla externa real
Existe el toggle `Modo Proyección` en `Sidebar.jsx` pero solo escala fuentes a 20px y reduce el sidebar a 260px. No probado en pantalla externa de paciente.

**Sugerencia**: agregar atajo `F11` para fullscreen real cuando esté activo.

## ALTA-2 · Cards sin padding consistente
Cards en distintos lugares usan `p-4`, `p-5`, `p-6`, `p-8`. Sin un sistema claro de cuándo usar cada uno.

**Sugerencia**: definir 3 tamaños canónicos en `primitives.jsx`:
- `Card padding="sm"` → `p-4`
- `Card padding="md"` → `p-5` (default)
- `Card padding="lg"` → `p-8` (heroes)

## ALTA-3 · ToastProvider sin límite de toasts simultáneos
`contexts.jsx:80-86` push toasts sin cap. Si un loop falla, se llenan 50+ toasts.

**Sugerencia**: max 5 toasts visibles, los siguientes se encolan.

## ALTA-4 · `parseInt` sin radix en algunos lugares
Buenas prácticas. Encontrados ~6 lugares.

**Sugerencia**: barrido + agregar regla ESLint `radix: error`.

## MEDIA-1 · Microcopia inconsistente
- A veces "Cerrar sesión", a veces "Salir"
- "Iniciar evaluación" vs "Aplicar evaluación" vs "Comenzar"
- "PD" / "Puntaje directo" / "Puntuación bruta"

**Sugerencia**: glosario de UI en `src/data/ui.js` con términos canónicos.

## MEDIA-2 · Falta confirmación de "cambios sin guardar"
Si el clínico está aplicando evaluación con datos ingresados y navega a otra página, **se pierden los puntajes**.

**Sugerencia**: usar `beforeunload` event + `useBlocker` cuando hay cambios pendientes.

## MEDIA-3 · No hay autoguardado de evaluación en curso
Mismo bucket: si la app crashea durante una sesión de 2 horas, se pierde todo.

**Sugerencia**: persistir `puntajes` y `obs` cada 30 s en `localStorage` con clave `ns_eval_draft_<patientId>_<proto>`.

## OPORTUNIDAD-1 · Comando palette tipo Cmd+K
Linear, Notion, Slack tienen `Cmd+K` para búsqueda + acciones. NeuroSoft se beneficiaría:
- "Ir a paciente Juan Pérez"
- "Aplicar WISC-IV al paciente seleccionado"
- "Buscar Stroop en biblioteca"

Sería **clave** para el módulo educativo futuro.

## OPORTUNIDAD-2 · Animaciones más sutiles
La página actual usa `ns-page-in` (fade + translateY 8px 200ms). Bien, pero podría tener:
- Transición entre pasos de evaluación (slide horizontal)
- Pulso del cronómetro cuando se acaba el tiempo (ya existe)
- Mejor feedback al guardar (current: solo toast verde)

## OPORTUNIDAD-3 · Atajos de teclado expandidos
Hoy existen Alt+P/E/R/H/+/-/D. Faltan:
- `Ctrl+S` guardar evaluación
- `Ctrl+F` buscar paciente
- `Space` iniciar/pausar cronómetro
- `Esc` cerrar modal

---

# 🏗 Auditoría arquitectura y código

## DT-1 · Archivos >700 líneas (8 archivos)

| Archivo | Líneas | Tipo | Recomendación |
|---|---:|---|---|
| `rehab_use_cases.py` | 1296 | Use case backend | Dividir por sub-dominio (planes, sesiones, suggest) |
| `screening.js` | 1230 | Data | OK (es datos, no lógica) |
| `PanelIA.jsx` | 1134 | Page composta | Dividir en AIConfigPage / AIFloatingChat / ProviderCards |
| `report_service.py` | 1098 | Service | **Próxima sesión** (rediseño completo del PDF) |
| `RehabPage.jsx` | 1083 | Page | Dividir en RehabPage / PlanCard / ActivityRunner |
| `datosClinicos.js` | 1048 | Data | OK (es datos) |
| `report_pro/base.py` | 908 | Service | OK (variante PDF Pro, en construcción) |
| `main.py` (backend) | 755 | Startup | Dividir startup en `bootstrap.py` |

## DT-2 · Componentes con responsabilidad mixta
- `ConfigPage.jsx` 12 tabs en una sola página. Funciona pero crece sin freno.
  - **Sugerencia**: lazy load de cada tab. `React.lazy(() => import('./ProfesionalesTab'))`
- `EvalApplyPage.jsx` 439 líneas con lógica de cronómetro, retención, conductas, navegador.
  - **Sugerencia**: extraer `useTimer()`, `useRetentionTimes()`, `useConductas()` como hooks.

## DT-3 · `App.jsx` con lógica de polling
`App.jsx` tiene el polling de tarea-casa hardcoded (líneas 190-220). Debería estar en un service.

**Sugerencia**: extraer a `services/notifications.js` con `useHomeworkPolling()`.

## ARC-1 · Backend ya está casi listo para módulos
Clean Architecture sólida. Para módulos nuevos solo hace falta:
- Crear `app/therapy/` y `app/education/` paralelos a `app/domain/clinical_engine/`
- Mover entidades comunes a `app/shared/` (Paciente, Profesional, Agenda)

## ARC-2 · Frontend necesita más prep para escalar
Actualmente todo está bajo `src/app/`. Para soportar módulos:
- Reorganizar a `src/modules/{evaluation,therapy,education}/`
- Cada módulo con su propio `pages/`, `components/`, `data/`, `hooks/`

## ARC-3 · `ACTIVITY_COMPONENTS` no es escalable
En `RehabPage.jsx` hay un dict gigante que mapea slug → componente. Cuando agreguemos más actividades:
- **Sugerencia**: convertir a registry con auto-discovery vía Vite glob imports
```jsx
const modules = import.meta.glob('./activities/*.jsx', { eager: true });
```

## TEST-1 · Cobertura de tests ~20% (CRÍTICO para software médico)
Según memoria del proyecto: 488 tests backend, pero solo cubre ~33 de 168 pruebas clínicas.

**Sugerencia**: usar `/snapshot-paciente` para capturar 5-10 casos reales y crear regression tests automáticos.

## TEST-2 · No hay tests e2e del flujo completo
Playwright existe pero está minimal. **Crítico**: test e2e "paciente → evaluación → informe" cubriría los 3 flujos principales.

## PERF-1 · Bundle frontend 795 KB sin code splitting
`index-XXXX.js` carga todo de una vez. **Sugerencia**: `React.lazy()` por página.

```jsx
const RehabPage = React.lazy(() => import('./app/rehab/RehabPage'));
```

Esto bajaría el bundle inicial a ~200 KB.

## PERF-2 · Recharts 547 KB (gzipped 162 KB) sigue grande
Considerar alternativas: `lightweight-charts`, `visx` o custom SVG para gráficos simples (lo del Z-bar ya es custom).

## DOC-1 · Sin diagramas de flujo del motor clínico
`neurosoft-backend/CLAUDE.md` documenta excelente. Pero un diagrama visual `engine.py → strategies.py → baremos_loader.py` ayudaría a nuevos devs.

**Sugerencia**: Mermaid diagram en `CLAUDE.md`.

## I18N-1 · No hay sistema de i18n
Todo hardcoded en español. Si en el futuro:
- Quieren versión en inglés (export, exportar a mercados latinoamericanos no-hispanohablantes)
- O regional (español Argentina vs Colombia)

**Sugerencia**: agregar `react-i18next` ahora antes de que crezca más. Estimación: 1-2 días.

## SEC-1 · `enable_cloud` en AI config no afecta sanitización
`enable_cloud=False` debería forzar también que **no se envíe nada** a APIs externas, pero solo cambia el provider. Validar que sanitización PHI sea estricta.

## BUILD-1 · PyInstaller funciona pero es lento (~90 s)
Aceptable. Si crece más, considerar:
- Nuitka (compila a C, más rápido)
- Tauri (Rust + WebView, ~10 MB binary final)

Pero por ahora PyInstaller es lo correcto.

---

# 🎯 Top 3 acciones recomendadas ANTES de expandir

1. **Refactor de navegación + lazy loading** (2-3 días)
   - Reorganizar `src/app/` → `src/modules/`
   - Lazy load por módulo
   - Reduce bundle inicial 60-70%

2. **Cobertura de tests clínicos al 60%** (1 semana)
   - Usar `/snapshot-paciente` para capturar 15 casos canónicos
   - Tests de regresión para cada estrategia del engine
   - Test e2e Playwright del flujo paciente→evaluación→informe

3. **Auto-guardado + protección "cambios sin guardar"** (1 día)
   - Persistir borradores en localStorage cada 30 s
   - Banner si intentas cerrar con cambios pendientes
   - Salvar evaluaciones de 2 horas que se perdían

Estas 3 cosas convierten NeuroSoft de "MVP exitoso" a **producto médico robusto** listo para soportar módulos terapia + educativo sin sufrir.

---

# 📊 Métricas

| Métrica | Valor | Comentario |
|---|---:|---|
| Líneas frontend totales | 21,381 | Razonable |
| Líneas backend totales | 28,860 | Aceptable para Clean Arch |
| Archivos >700 líneas | 8 | Acción recomendada en 3 de ellos |
| Botones sin aria-label | ~41 | Acción recomendada |
| TODO/FIXME reales | 0 | Excelente |
| console.log olvidados | 1 | Bien |
| Bundle frontend gzipped | ~220 KB | OK, pero crecerá |
| Cobertura tests (estimada) | ~20% | Crítico para software médico |

---

# 🚀 Roadmap de expansión

Ver documento separado: `ROADMAP_EXPANSION.md`

Resumen:
- **Pilar 1 (HOY)**: Evaluación neuropsicológica
- **Pilar 2 (3 meses)**: Sesiones de psicología clínica (terapia, SOAP notes, planes terapéuticos, riesgo suicida, telepsicología)
- **Pilar 3 (2 meses)**: Aprender/Repasar (biblioteca, spaced repetition, simulador, quizzes, artículos)

Total expansión: **5-6 meses** para tener ambos módulos en beta.
