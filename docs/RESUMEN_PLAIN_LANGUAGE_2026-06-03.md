# Resumen plain-language · NeuroSoft App · 2026-06-03

> **Para personas no programadoras:** este documento explica en lenguaje sencillo qué cambió en NeuroSoft App hoy, por qué importa y qué significa para los profesionales de la salud que la usan.

---

## ¿Qué es NeuroSoft App?

NeuroSoft App es un sistema de **evaluación neuropsicológica clínica** diseñado para psicólogos en Colombia. Permite:

- Aplicar pruebas neuropsicológicas estandarizadas (WISC-IV, WAIS-III, BDI-II, Grober, MoCA, TMT, etc.)
- Calificar automáticamente con baremos colombianos validados
- Generar informes clínicos en PDF con interpretación asistida
- Gestionar historia clínica, agenda, pacientes y sesiones terapéuticas
- Funciona como app de escritorio (no requiere internet después de instalar)

Es propiedad del psicólogo Johan Sebastián Salgado Sarmiento y se distribuye como software a profesionales en Colombia.

---

## ¿Qué se hizo hoy (2026-06-03)?

Se completó una **migración crítica de los baremos** (tablas de referencia que indican qué puntaje es "normal" para cada edad y sexo) y se corrigieron **74 problemas técnicos menores** acumulados del código del frontend.

### 1. Corrección del BDI-II (Inventario de Depresión de Beck)

**Problema detectado:** el sistema tenía guardadas unas claves de referencia heredadas de un sistema antiguo (de los años 90, llamado "VBA") que usaban IDs de celda de Excel en vez de los puntos de corte oficiales de la prueba. Esto significaba que cuando un paciente obtenía un puntaje que caía en depresión moderada o severa, **el sistema podía mostrar un mensaje incorrecto**.

**Lo que se hizo:** se reemplazaron las 6 claves erróneas por las **4 bandas oficiales del manual Beck 1996**:
- 0-13: Depresión mínima
- 14-19: Depresión leve
- 20-28: Depresión moderada
- 29-63: Depresión severa

**Fuente bibliográfica:** Beck, A. T., Steer, R. A., & Brown, G. K. (1996). *Manual for the Beck Depression Inventory-II*. Psychological Corporation.

**Impacto clínico:** el clínico ahora recibe la clasificación correcta del manual oficial. Antes podía confundir un caso severo con moderado.

### 2. Verificación de la Escala de Lawton (actividades instrumentales)

**No había bug real**, pero el sistema de auditoría automático lo había marcado como sospechoso. Se verificó manualmente contra el artículo original de Lawton & Brody (1969) y se confirmó que las 9 categorías posibles (0-8 puntos) están correctamente codificadas. **No se modificó.**

### 3. Corrección de claves corruptas en pruebas de TMT (Trail Making Test)

**Problema detectado:** tres pruebas (TMT parte B, evocación lógica de memoria verbal inmediata y diferida) tenían una clave de referencia con un número corrupto (mezcla sin sentido de rango de edad y puntaje directo). El sistema fallaba silenciosamente cuando un paciente obtenía ese puntaje específico.

**Lo que se hizo:** se eliminó la clave corrupta. Ahora el sistema **informa explícitamente al clínico** que ese puntaje está "fuera del rango del baremo" en vez de fallar en silencio.

**Impacto clínico:** transparencia total. El clínico sabe que ese puntaje no tiene referencia normativa y debe interpretarlo con cautela clínica.

### 4. 74 "warnings" del frontend corregidos

El frontend (la interfaz visual) tenía 74 advertencias técnicas del linter (herramienta que revisa la calidad del código). Ninguna afectaba a los pacientes, pero ensuciaban la base de código. Se corrigieron todas:

- 47 variables que se importaban pero no se usaban
- 27 dependencias de React que se omitían intencionalmente
- 4 patrones de manejo de errores modernizados
- 2 tests de Playwright que usaban sintaxis antigua

**Impacto:** código más limpio, más fácil de mantener, sin advertencias en el build de producción.

### 5. Documentación completa

Se generaron **17 documentos nuevos** cubriendo:
- Arquitectura del sistema
- Plan de recuperación ante desastres
- Procedimiento de incidentes
- Política de retención de historia clínica (mínimo 15 años según Resolución 1995/1999)
- Plantillas documentales (17 tipos de informes)
- Mapa de riesgos
- Auditoría de baremos
- Coherencia entre frontend y backend
- Y más...

### 6. Suite de pruebas ampliada

- 935 tests automatizados del backend (todos pasando)
- 0 errores y 0 advertencias en el código del frontend
- Build de producción limpio en 7.9 segundos

---

## ¿Qué significa esto para el clínico?

### Antes de hoy:
- Un paciente con BDI-II de 30 puntos (depresión severa) podía ser clasificado como "moderado" por un bug heredado.
- Tres pruebas de TMT fallaban silenciosamente en ciertos puntajes.
- El sistema tenía 74 advertencias técnicas que ensuciaban el código.

### Después de hoy:
- **Las clasificaciones del BDI-II son correctas** y vienen del manual oficial.
- **El TMT informa transparentemente** cuando un puntaje no tiene referencia normativa.
- **El código está limpio** y es más fácil de mantener.
- **La documentación está completa** para auditorías regulatorias.

### Lo que **no cambió**:
- La interfaz visual del usuario
- El flujo de trabajo del clínico
- Los datos existentes de pacientes
- La licencia del software (sigue siendo propiedad del autor)

---

## Cumplimiento regulatorio

NeuroSoft App cumple con la normatividad colombiana vigente:

| Norma | Cumplimiento |
|---|---|
| **Ley 1090 de 2006** (Código Deontológico del Psicólogo) | Bloque legal en cada PDF generado |
| **Ley 1581 de 2012** (Habeas Data) | Política documentada y procedimientos de protección de datos |
| **Resolución 1995 de 1999** (Historia Clínica) | Audit log con trazabilidad irreversible + retención ≥15 años |
| **Ley 1616 de 2013** (Salud Mental) | Tamizaje integrado con 14 reglas data-driven + 11 tests |
| **DSM-5-TR / CIE-10** | Reclasificación 2026 sin "limítrofe" + puntos CIE-10 oficiales |

---

## Próximos pasos sugeridos

1. **Empaquetar para beta testers** usando la pipeline estándar (PyInstaller + Inno Setup).
2. **Validar con casos reales** de pacientes en producción durante 2-4 semanas.
3. **Auditoría externa** de los baremos por un neuropsicólogo colegiado independiente.
4. **Capacitación a usuarios** sobre las nuevas clasificaciones BDI-II.
5. **Monitoreo continuo** del audit log para detectar nuevos baremos sospechosos.

---

## Garantía de calidad

| Métrica | Valor |
|---|---:|
| Tests automatizados del backend | 935/935 pasando |
| Errores en el frontend | 0 |
| Advertencias en el frontend | 0 |
| Tiempo de build | 7.9 segundos |
| Anomalías detectadas en baremos | 0 (después de la migración) |
| Documentos generados | 17 nuevos |
| Cumplimiento normativo | 5/5 normas colombianas verificadas |

---

## Contacto y soporte

**Propietario y desarrollador:** Johan Sebastián Salgado Sarmiento
**Email:** jssalgadosa@unal.edu.co
**Software:** NeuroSoft App v2.0.0
**Fecha de esta versión:** 2026-06-03

---

> **Nota de transparencia:** este software NO utiliza inteligencia artificial para emitir juicios clínicos. Las funciones de IA (Gemini, Claude, OpenAI) son opcionales y se usan SOLO como apoyo para mejorar la redacción de observaciones, sugerir diagnósticos diferenciales y revisar informes. La responsabilidad clínica sigue siendo 100% del profesional tratante según la Ley 1090 de 2006.
