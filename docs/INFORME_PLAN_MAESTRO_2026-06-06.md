# Informe de implementación — PLAN MAESTRO NeuroSoft
**Fecha:** 6 de junio de 2026  
**Alcance:** Sprints 0–8 del `PLAN_MAESTRO_DESARROLLO.md` + consentimiento email/impresión + build distribuible.

---

## Resumen ejecutivo

Se ejecutó el plan maestro de UI/UX y módulos clínicos priorizando calidad sobre velocidad. El sistema queda listo para beta con instalador `NeuroSoft-Setup.exe`. El consentimiento informado usa **firma digital + PDF imprimible + envío por correo SMTP** (sin OTP/SMS — no requiere proveedor de mensajería).

---

## 1. Sistema de diseño (Sprint 0 — DS-1..5)

| Componente | Archivo | Para qué sirve |
|---|---|---|
| `StatTile` | `src/ui/StatTile.jsx` | KPIs editoriales en dashboard (número grande, sin bordes de color) |
| `ActionTile` | `src/ui/ActionTile.jsx` | Accesos rápidos clickeables (evaluación, terapia, agenda…) |
| `SectionCard` | `src/ui/SectionCard.jsx` | Reemplaza `border-l-4` — cabecera tipográfica editorial |
| `FloatingTimer` | `src/ui/FloatingTimer.jsx` | Cronómetro flotante en evaluación (no bloquea la cabecera) |
| `SegmentedNav` | `src/ui/SegmentedNav.jsx` | Navegador vertical de subtests con estado por punto |
| `GuideAccordion` | `src/ui/GuideAccordion.jsx` | Guía de aplicación en acordeón (materiales, tips, discontinuación) |
| `Popover` | `src/ui/Popover.jsx` | Desgloses hover en indicadores |

**DS-4:** Migrados todos los `border-l-4` detectados a `SectionCard` o bordes hairline.  
**DS-5:** Regla documentada en `neurosoft-frontend/CLAUDE.md`.

---

## 2. Dashboard y navegación (Sprint 1)

| Cambio | Para qué sirve |
|---|---|
| `DashboardPage` 3 zonas | Hero accionable + indicadores + módulos (menos ruido visual) |
| `EstadisticasPage` | Gráficos de tendencia/demografía fuera del inicio |
| `Sidebar` CTA "Nuevo paciente" | Flujo directo al registro |
| Ruta `estadisticas` en `App.jsx` | Acceso desde sidebar y ActionTiles |

---

## 3. Pacientes e historia clínica (Sprint 2 — PX)

| ID | Implementación | Para qué sirve |
|---|---|---|
| PX-1 | Campo `via_atencion` + migración 007 | Enruta a neuro / terapia / rehab / mixto |
| PX-2 | `RegisterPage` paso vía + redirect contextual | Tras guardar va al módulo correcto |
| PX-3 | HC **4 pasos** + screening aparte | Desarrollo → Antecedentes → Familiar → Plan; MMSE/escalas en módulo Screening |
| CIE dual | `codigo_cie11` + API `/cie11/map` | Transición CIE-11 sin romper RIPS (CIE-10) |
| Pre-Post | Botón en `PatientsPage` → `compare` | Seguimiento longitudinal |

---

## 4. Agenda (Sprint 3 — AG)

| Campo / feature | Para qué sirve |
|---|---|
| EPS, régimen, CUPS, autorización | Preflight RIPS y facturación EPS |
| `cupsPsicologia.js` + `aseguradoresColombia.js` | Catálogos en frontend |
| Botón nuevo paciente desde agenda | No bloquear cita si el paciente no existe |
| `SectionCard` en formulario | UI editorial coherente |

---

## 5. Evaluación neuropsicológica (Sprint 4 — EV)

| Feature | Para qué sirve |
|---|---|
| Portada intro (`portadaOk`) | Checklist antes de aplicar batería |
| `FloatingTimer` | Cronómetro sin ocupar todo el ancho |
| `SegmentedNav` | Navegación rápida entre subtests |
| `GuideAccordion` | Guía lateral desglosada |
| `ScoreInput` endurecido | Bloqueo 9999, rangos Yesavage |
| Link Screening desde TopBar | Screening con mismo paciente/contexto |
| `ValidezPanel` | Criterios Slick + TOMM/Rey en peritaje |

---

## 6. Screening (Sprint 5 — SC)

| Feature | Para qué sirve |
|---|---|
| Layout 2 columnas | Categorías verticales izquierda, instrumento derecha |
| Wizard y validez colapsados | Menos ruido; opcionales por defecto |
| Dedup NPIQ/Zarit | Corrige duplicados en selector |

---

## 7. RIPS y normativa (Sprint 6)

| Feature | Para qué sirve |
|---|---|
| `RipsPage.jsx` | Preflight semáforo + export ZIP/TXT mensual |
| Backend RIPS/CIE/CUPS | Ya existía; ahora con UI |

---

## 8. Psicoterapia e IA (Sprint 7)

| Feature | Para qué sirve |
|---|---|
| Meet/Zoom en `SesionSOAPForm` | Telepsicología más allá de Jitsi |
| `TherapyPage` modal catálogo fix | No cierra al hacer click interno |
| PanelIA pulls MedGemma/Meditron | Modelos clínicos locales Ollama en un clic |
| `PanelCompartir` video opcional | Link Meet/Zoom al copiar informe |

---

## 9. Aprender y configuración (Sprint 8)

| Feature | Para qué sirve |
|---|---|
| `AprenderHub` tabs internos | Navegación sin salir del hub |
| Pruebas en `ConfigPage` embebidas | Catálogo técnico en ajustes, sin TopBar duplicado |
| `BibliotecaPage` cards clickeables | Abre URL/DOI del recurso |

---

## 10. Consentimiento informado (CONS — alternativa práctica)

**Decisión:** No implementar OTP/SMS (complejidad operativa). En su lugar:

| Endpoint / UI | Para qué sirve |
|---|---|
| `GET /consentimientos/pdf/plantilla/{tipo}` | PDF imprimible para firma presencial |
| `GET /consentimientos/{id}/pdf` | Copia firmada con firma manuscrita |
| `POST /consentimientos/enviar-email` | Envía plantilla o copia firmada vía SMTP |
| `ConsentModal` | Imprimir, enviar correo, firmar digitalmente |

**Configuración SMTP:** Ajustes → Comunicaciones (Gmail app-password, Office 365, etc.).

---

## 11. Build y artefactos (regenerado 6 jun 2026 noche)

| Artefacto | Ubicación |
|---|---|
| `NeuroSoft.exe` | `dist/NeuroSoft.exe` (**47.3 MB**) |
| `NeuroSoft-Setup.exe` | `dist/NeuroSoft-Setup.exe` (~1.34 GB, incluye Ollama separado) |

Pipeline: `npm run build` → `py_compile` → `python build.py --skip-frontend --skip-ollama` → Inno Setup.

**Informe de cierre ampliado:** `docs/INFORME_CIERRE_2026-06-06.md`

---

## 12. Pendiente real (no bloquea beta)

- OTP Ley 527 (opcional futuro si contratan SMS)
- Placeholders visuales REACTIVOS WISC/WAIS (sprint clínico aparte)
- E2E manual paciente → WISC → PDF Pro
- QW-6 etiquetas pacientes, QW-8 backup programado
- Dark mode pasada en `evaluation/` residual

---

## 13. Sugerencias futuras

1. **GitHub Actions CI** — pytest + eslint en cada push (ya hay workflows; activar en repo remoto).
2. **Firma OTP** — solo si hay presupuesto Twilio/Infobip; hasta entonces email+PDF es suficiente para Ley 1581.
3. **RIPS XML electrónico** — cuando EPS exija Res. 2275 completa.
4. **PWA paciente** — consentimiento y tareas terapéuticas desde móvil.
5. **Tests E2E Playwright** — automatizar checklist pre-beta.

---

## 14. Subir a GitHub personal — ventajas

| Ventaja | Detalle |
|---|---|
| **Backup** | Código fuera del PC; recuperación ante fallo de disco |
| **Historial** | Commits trazables por feature/sprint |
| **CI** | GitHub Actions corre tests en cada cambio |
| **Colaboración** | Otros devs o IAs clonan el mismo repo |
| **Releases** | Tags + assets (instalador) para beta testers |
| **Issues/Projects** | Kanban de bugs de beta sin mezclar con código |

**Repo privado recomendado** — contiene lógica clínica y baremos; no publicar `BD_NEURO_MAESTRA.json` en repos públicos sin revisar licencias Pearson.
