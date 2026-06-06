# Plan — Sprint Estética (UI, Plantillas, Animaciones, Informes PDF)

**Fecha:** 2026-06-03
**Autor:** Claude + Johan
**Duración estimada:** 3 semanas (1 semana por área, priorización 1→4)
**Estado:** Pendiente de aprobación

---

## 🎯 Objetivo

Elevar la calidad visual y de experiencia de NeuroSoft App al nivel de un producto SaaS de clase mundial, manteniendo:

- **Cumplimiento normativo** (Ley 1090/2006, Res. 1995/1999, Ley 1581/2012) — sin modificar
- **Performance** (< 2s en operaciones críticas, < 100MB ejecutable)
- **Offline-first** (sin CDN obligatorio)
- **A11y** (WCAG 2.1 AA) — ya implementado en F11
- **0 dependencia pesada** en frontend (no Recharts, no Framer-Motion si no se necesita)

---

## 📋 Inventario del estado actual (auditoría rápida)

### Frontend — `neurosoft-frontend\src\ui\`

| Componente | Función | Refactor necesario |
|---|---|---|
| `primitives.jsx` | Btn, Card, Input, Modal base | Media — faltan variants, sizes |
| `tokens.js` | Design tokens (colores, spacing, typography) | Baja — falta `motion` tokens |
| `Skeleton.jsx` | Loading states | Baja — listo, falta integrar más |
| `NeuroCanvas.jsx` | Visualización neuropsicológica | Alta — diseño genérico |
| `AvatarUploader.jsx` | Foto paciente | Baja — funcional |
| `GlossaryTerm.jsx` | Tooltip términos clínicos | Baja — listo |
| `PearsonConsentDialog.jsx` | Modal consentimiento | Baja — funcional |
| `SelloProtegidoBadge.jsx` | Badge PDF protegido | Baja — funcional |
| `ApoyoClinicoPanel.jsx` | Panel de apoyo clínico | Media — agregar variantes |
| `ErrorBoundary.jsx` | Error boundary | Baja — funcional |
| `a11y.jsx` | Utilidades accesibilidad | Baja — listo |

**No existe:** `theme.js` runtime, `motion.js` animaciones reutilizables, `Toaster` componente, `Dropdown` con teclado.

### Backend — `app\infrastructure\report_pro\`

| Archivo | Función | Refactor necesario |
|---|---|---|
| `base.py` | ReportLab base | Baja — funcional |
| `charts.py` | Gráficos SVG/PNG | Alta — gráficos básicos, falta radar/spider |
| `helpers.py` | Utilidades PDF | Baja — funcional |
| `narrative.py` | Generación de narrativa | Media — plantillas estáticas, falta variants |
| `theme.py` | Tema visual PDF | Media — falta dark-mode PDF |
| `variants/` | Variantes informe | Pendiente auditoría |

**No existe:** `template_service.py` para CRUD de plantillas documentales editables.

### Frontend — Animaciones

**Librerías instaladas:** NINGUNA
- `framer-motion`: NO instalado (10KB gzip, opcional)
- `react-spring`: NO instalado
- `lottie-react`: NO instalado
- CSS keyframes: disponibles nativamente

**Recomendación:** Usar **CSS keyframes + transitions** como primera opción (0 KB extra). Solo si se justifica, agregar `framer-motion` (~10KB gzip).

---

## 🗓️ Sprint 1 (Semana 1): Animaciones + microinteracciones

**Foco:** Pulir la experiencia de uso sin cambiar funcionalidad. Bajo riesgo.

### 1.1 Tokens de motion (nuevo)
**Archivo:** `src\ui\motion.js`

```js
export const motion = {
  duration: { fast: 150, normal: 250, slow: 400 },
  easing: {
    default: 'cubic-bezier(0.4, 0, 0.2, 1)',
    emphasized: 'cubic-bezier(0.2, 0, 0, 1)',
    decel: 'cubic-bezier(0, 0, 0.2, 1)',
  },
  stagger: { 1: 30, 2: 60, 3: 100 },
};

// CSS variables (en index.css o tailwind.config.js)
:root {
  --motion-duration-fast: 150ms;
  --motion-duration-normal: 250ms;
  --motion-easing-default: cubic-bezier(0.4, 0, 0.2, 1);
}
```

### 1.2 Page transitions
**Archivo:** `src\App.jsx` (modificar)

```jsx
// Usar CSS transitions nativas
.page-enter { opacity: 0; transform: translateY(8px); }
.page-enter-active { opacity: 1; transform: translateY(0); transition: all 250ms var(--motion-easing-default); }
```

**Páginas a transicionar:** Dashboard, Pacientes, Evaluaciones, Informes, Sesiones, Configuración.

### 1.3 Skeleton loaders
**Estado:** Componente `Skeleton.jsx` ya existe. **Falta integrar en:**

- `PatientsListPage.jsx` — tabla mientras carga
- `EvaluationsListPage.jsx`
- `InformesPage.jsx`
- `ConfigPage.jsx` (tabs)
- `DashboardPage.jsx` (widgets)

**Estimación:** 1-2 horas.

### 1.4 Toast system
**Archivo nuevo:** `src\ui\Toaster.jsx`

```jsx
// API
toast.success('Evaluación firmada correctamente');
toast.error('No se pudo guardar');
toast.warning('Sesión próxima a expirar');
toast.info('Recordatorio programado');

// Auto-dismiss en 4s, click-outside, Esc to close
// A11y: role="status" aria-live="polite"
```

**Reemplaza:** `alert()`, `console.log()`, mensajes inline.

### 1.5 Animaciones de éxito
**Archivo:** `src\ui\Confetti.jsx` (opcional, ~200 líneas)

Trigger en:
- Firma de informe completada
- Evaluación finalizada con éxito
- Paciente archivado

**Decisión:** Opcional. Si se justifica, instalar `canvas-confetti` (~5KB gzip).

### 1.6 Refinamiento de primitivos
**Archivo:** `src\ui\primitives.jsx` (modificar)

- `Btn` agregar: `variant="primary|secondary|ghost|destructive"`, `size="sm|md|lg"`, `loading` state con spinner
- `Card` agregar: `hoverable`, `clickable` (ripple effect sutil)
- `Input` agregar: `icon` prop (lupa, calendario, usuario)
- `Modal` agregar: `size="sm|md|lg|full"`, animaciones de entrada/salida

### 1.7 Pruebas visuales (Playwright visual regression)
**Nuevo:** `neurosoft-frontend\e2e\visual\`

- Capturar screenshots de páginas clave (Dashboard, Evaluación, Informe)
- Comparar con baseline (pixelmatch)
- Ejecutar en CI

**Estimación:** 2-3 horas setup + ~50 baselines.

### Sprint 1 entregables

- ✅ Tokens de motion
- ✅ Page transitions
- ✅ Skeleton loaders integrados
- ✅ Toast system
- ✅ Primitivos refinados
- ⏸️ Confetti (decidir después de feedback)
- ⏸️ Visual regression (setup + 1 página piloto)

**Estimación:** 3-4 días de trabajo.

---

## 🗓️ Sprint 2 (Semana 2): Informes PDF — diseño profesional

**Foco:** Llevar el PDF a calidad de "consultorio privado premium". No cambiar datos, solo presentación.

### 2.1 Auditoría de `report_pro\`
**Acción:** Leer todos los archivos en `app\infrastructure\report_pro\` y `variants/`. Listar:
- Plantillas actuales (cuántas, qué cubren)
- Elementos visuales (logos, headers, footers, marcas de agua)
- Gráficos (qué tipos: barras, líneas, radar, heatmap)
- Tipografía (qué fuentes, si son legibles en grayscale)
- Datos fijos vs configurables (nombre clínica, logo, colores)

**Skill útil:** `mejorar-informe-pdf` ya existe en `.claude/skills/`.

### 2.2 Plantilla "Executive Summary" 1-página
**Nuevo:** `app\infrastructure\report_pro\variants\executive.py`

**Contenido (1 cara A4):**
- Logo + nombre clínica (configurable)
- Nombre paciente + edad
- Motivo de consulta (1 línea)
- 3 hallazgos principales (1 línea cada uno, top 3 dominios deficitarios)
- 1 recomendación prioritaria
- Perfil cognitivo resumido (1 frase)
- QR con link a informe completo (futuro portal paciente)
- Firma del profesional

**Uso:** Para juntas médicas, envío rápido, vista previa.

### 2.3 Gráficos clínicos avanzados
**Archivo:** `app\infrastructure\report_pro\charts.py` (extender)

- **Radar/Spider chart** para perfil cognitivo multi-dominio
- **Heatmap** para comparación baremo vs paciente (por edad, por dominio)
- **Barras agrupadas** para Pre/Post intervención
- **Timeline** para evolución temporal

**Libs:** `matplotlib` ya está en backend. Generar PNG transparent background, embeber en ReportLab.

### 2.4 Tema visual configurable
**Archivo:** `app\infrastructure\report_pro\theme.py` (extender)

- Colores primarios (configurables desde `ConfigInstitucion`)
- Logo (subido por usuario, `ConfigInstitucion.logo_path`)
- Tipografía (default: Roboto/Helvetica; permitir custom .ttf)
- Estilo de tabla (filas alternadas, bordes sutiles)
- Marca de agua opcional (texto diagonal "CONFIDENCIAL" o logo)

### 2.5 Narrativa mejorada
**Archivo:** `app\infrastructure\report_pro\narrative.py` (extender)

- Variantes por audiencia: "técnico" (psicólogo), "paciente" (lenguaje claro), "familiar" (educativo)
- Tono: 3 niveles (formal, semi-formal, accesible)
- Conectores enriquecidos: "Adicionalmente...", "Cabe destacar que...", "En contraste con..."
- Eliminación de muletillas técnicas para audiencia paciente

### 2.6 Variantes de informe
**Auditoría:** Revisar `variants/` actual.

**Propuesta de 4 variantes:**
1. **pro** (estándar) — actual, 4-8 páginas
2. **executive** (nuevo) — 1 página resumen
3. **seguimiento** — solo Pre/Post, comparativo
4. **familiar** — lenguaje accesible para padres/cuidadores

### Sprint 2 entregables

- ✅ Auditoría completa de `report_pro\`
- ✅ Variante "Executive Summary" funcional
- ✅ 2 nuevos gráficos (radar + heatmap)
- ✅ Tema visual configurable
- ✅ Narrativa con 3 audiencias
- ✅ 4 variantes de informe operativas

**Estimación:** 5-6 días de trabajo.

---

## 🗓️ Sprint 3 (Semana 3): Plantillas documentales editables

**Foco:** Que el clínico pueda crear/editar plantillas sin tocar código. Auditoría clínica + jurídica.

### 3.1 Modelo de datos
**Nuevo:** `app\infrastructure\orm_models.py` agregar:

```python
class PlantillaDocumentalORM(Base):
    __tablename__ = "plantillas_documentales_usuario"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    institucion_id: Mapped[str] = mapped_column(String(36), ForeignKey("config_institucion.id"))
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)  # informe, remision, etc.
    version: Mapped[int] = mapped_column(Integer, default=1)
    contenido_html: Mapped[str] = mapped_column(Text, nullable=False)
    merge_fields: Mapped[str] = mapped_column(Text)  # JSON con campos disponibles
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(String(50))
    updated_at: Mapped[str] = mapped_column(String(50))
```

### 3.2 Servicio de plantillas
**Nuevo:** `app\infrastructure\template_service.py`

```python
class TemplateService:
    def listar(self, institucion_id, tipo=None) -> list[PlantillaResumen]
    def obtener(self, plantilla_id) -> PlantillaDetalle
    def crear(self, institucion_id, nombre, tipo, contenido, merge_fields) -> str
    def actualizar(self, plantilla_id, cambios) -> PlantillaDetalle
    def versionar(self, plantilla_id) -> str  # crea nueva versión
    def eliminar(self, plantilla_id) -> bool
    def renderizar(self, plantilla_id, contexto) -> bytes  # genera PDF/DOCX
```

### 3.3 Motor de merge fields
**Nuevo:** `app\infrastructure\template_engine.py`

- Sintaxis: `{{ paciente.nombre }}`, `{{ eval.fecha }}`, `{{ resultados.bdi.banda }}`
- Filtros: `{{ fecha | format_date("%d/%m/%Y") }}`, `{{ numero | round(2) }}`
- Condicionales: `{% if paciente.edad < 18 %}infantil{% endif %}`
- Loops: `{% for resultado in resultados %}{{ resultado.test }}{% endfor %}`

**Implementación:** Usar `Jinja2` (10KB) o motor custom (~100 líneas). **Recomendación:** `Jinja2` (battle-tested, ya es dep de FastAPI o casi).

### 3.4 Editor visual
**Frontend:** `src\app\config\PlantillasEditorPage.jsx` (nuevo)

- Vista previa en vivo (al editar HTML, refresca render)
- Validación de merge fields (autocomplete con campos disponibles)
- Historial de versiones (timeline)
- Bloqueo de edición concurrente (lock por usuario durante 5 min)

**Editor:** Usar `react-quill` (~30KB) o `tiptap` (~50KB). **Recomendación:** `tiptap` (más moderno, mejor a11y).

### 3.5 UI: Configuración de plantillas
**Frontend:** Integrar en `ConfigPage.jsx`, tab "Plantillas".

- Lista de plantillas (institución)
- Botón "Nueva plantilla" → wizard (nombre, tipo, contenido base)
- Acciones: editar, duplicar, versionar, eliminar (soft delete)
- Buscar por nombre/tipo

### 3.6 Tests
**Backend:** `tests\infrastructure\test_template_service.py` (15-20 tests)
- CRUD básico
- Versionado
- Renderizado con merge fields
- Validación de sintaxis

**Frontend:** Playwright para editor visual.

### Sprint 3 entregables

- ✅ Modelo `PlantillaDocumentalORM` + migración
- ✅ `TemplateService` con CRUD + versionado
- ✅ Motor de merge fields con Jinja2
- ✅ Editor visual con tiptap
- ✅ Integración en `ConfigPage`
- ✅ 15-20 tests del servicio

**Estimación:** 5-6 días de trabajo.

---

## 📅 Resumen de prioridad

| Sprint | Área | Impacto | Esfuerzo | Semana |
|---|---|---|---|---|
| 1 | Animaciones + UI polish | Medio (UX) | 3-4 días | 1 |
| 2 | Informes PDF premium | **Alto** (cliente) | 5-6 días | 2 |
| 3 | Plantillas editables | **Alto** (autonomía) | 5-6 días | 3 |

**Recomendación:** Empezar con Sprint 2 (Informes PDF) — mayor impacto visible para el usuario final. Sprint 1 se puede hacer en paralelo si hay 2 personas.

---

## ⚠️ Riesgos y decisiones pendientes

### Riesgos
1. **Complejidad PDF ReportLab** — los gráficos avanzados (radar, heatmap) requieren matplotlib embebido. Riesgo: tiempo de generación > 5s para informes largos.
   - **Mitigación:** Generar en background (job) + notificar al usuario.
2. **Editor visual tiptap** — dependencia pesada (~50KB). Puede ralentizar ConfigPage.
   - **Mitigación:** Lazy load del editor (React.lazy).
3. **Plantillas institucionales** — contenido editable por usuario. Riesgo legal si se omite Disclaimer.
   - **Mitigación:** Disclaimer obligatorio + auditoría automática (regex de cláusulas faltantes).

### Decisiones a tomar
1. ¿Agregar `framer-motion` (10KB) o quedarse con CSS? **Recomendación:** CSS.
2. ¿`canvas-confetti` (5KB) o sin confetti? **Recomendación:** Sin confetti (nicho, peso).
3. ¿`tiptap` (50KB) o `react-quill` (30KB)? **Recomendación:** tiptap (mejor a11y).
4. ¿`Jinja2` o motor custom? **Recomendación:** Jinja2.
5. ¿4 variantes de informe o solo 2? **Recomendación:** 2 (pro + executive). Las otras se pueden agregar después.

---

## 🎯 Criterios de éxito

| Criterio | Medición |
|---|---|
| Lighthouse score | > 90 (performance, a11y, best practices) |
| Bundle size | < 500KB gzipped (frontend) |
| PDF generation | < 3s para informe estándar de 6 páginas |
| A11y | WCAG 2.1 AA mantenido |
| Tests | 0 regresión, +30 tests nuevos |
| Feedback beta tester | > 80% positivo en UI |

---

## 🚀 Para empezar mañana

1. **Checkpoint** (`/checkpoint`) — congelar estado actual antes de refactor.
2. **Auditoría `report_pro/`** — leer todos los archivos, listar estado.
3. **Sprint 1 día 1:** Crear `src\ui\motion.js` con tokens.
4. **Feedback continuo:** Mostrar avances al usuario cada 2-3 días.

---

**Documento de planificación, no de implementación. Esperando aprobación del propietario para empezar Sprint 1.**
