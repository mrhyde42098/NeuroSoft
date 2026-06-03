# Guía Práctica: Registro de Software como Dispositivo Médico ante el INVIMA (Colombia)

> Documento técnico-jurídico para NeuroSoft
> Fecha: 2026-05-13
> Estado: Investigación preliminar — requiere revisión por abogado especializado

---

## 1. ¿ES NEUROSOFT UN DISPOSITIVO MÉDICO?

### Definición Legal (Decreto 677 de 1995, art. 2)
"Dispositivo médico: toda instrumento, aparato, equipo, máquina, implemento, material u otro artículo similar, usado solo o en combinación, incluyendo los programas informáticos necesarios para su correcto funcionamiento o aplicación, destinados por el fabricante para ser utilizados en seres humanos con fines de diagnóstico, prevención, seguimiento, tratamiento o alivio de enfermedades."

### Aplicación a NeuroSoft
| Característica | NeuroSoft | ¿Cumple? |
|---|---|---|
| Es software | Sí | ✅ |
| Usado en seres humanos | Sí (pacientes) | ✅ |
| Fines de diagnóstico | Indirecto — apoya decisión clínica | ⚠️ **Gris** |
| Fines de seguimiento | Sí — evaluaciones longitudinales | ✅ |
| Controla otro dispositivo | No | ❌ |
| Administra medicamentos | No | ❌ |

**Conclusión:** NeuroSoft probablemente califica como **Software como Dispositivo Médico (SaMD)** de **Clase I** (bajo riesgo), o posiblemente **Clase IIa** si se argumenta que influye significativamente en decisiones diagnósticas.

### Clasificación según INVIMA (Resolución 481 de 2022)
**Regla 11** — Software:
- Clase I: Software que proporciona información para tomar decisiones de tratamiento o diagnóstico
- Clase IIa: Software que proporciona información que puede conducir a decisiones de tratamiento o diagnóstico que pueden causar daño al paciente
- Clase IIb: Software que proporciona información para tomar decisiones de tratamiento o diagnóstico donde un error puede causar muerte o lesión grave

**Recomendación para NeuroSoft:** Solicitar registro como **Clase I** inicialmente, con documentación robusta que demuestre que NO toma decisiones autónomas.

---

## 2. DOCUMENTOS REQUERIDOS PARA REGISTRO INVIMA

### 2.1 Solicitud de Registro Sanitario
- Formato oficial INVIMA (disponible en www.invima.gov.co)
- Diligenciado por el fabricante o representante legal en Colombia
- Para software desarrollado en Colombia: el propio desarrollador es el fabricante

### 2.2 Descripción del Producto
Debe incluir:
- Nombre comercial: **NeuroSoft**
- Nombre genérico: "Software de evaluación neuropsicológica"
- Versión del software
- Descripción funcional detallada
- Arquitectura técnica (diagrama)
- Requisitos de sistema (hardware, SO, navegador)
- Flujo de trabajo del usuario (diagrama de flujo)

### 2.3 Etiqueta Propuesta
Contenido obligatorio:
- Nombre del producto
- Nombre y dirección del fabricante
- Número de registro sanitario (cuando se obtenga)
- Indicaciones de uso
- Contraindicaciones
- Advertencias y precauciones
- Instrucciones de uso
- Especificaciones técnicas
- Número de lote o versión
- Fecha de expiración o vigencia (para software: versión)

### 2.4 Manual de Usuario
Requisitos específicos para software médico:
- Instalación y configuración
- Requisitos previos (formación del usuario)
- Procedimiento paso a paso de uso
- Mensajes de error y soluciones
- Limitaciones conocidas
- Advertencias de seguridad
- Procedimiento de backup y recuperación
- Información de soporte técnico

### 2.5 Evidencia de Validación
Para software, esto incluye:
- **Verificación del software:** Pruebas unitarias, de integración, de sistema
  - NeuroSoft ya tiene 488 tests automatizados — documentar cobertura
- **Validación clínica:** Evidencia de que el software produce resultados correctos
  - Comparación con baremos publicados (WISC-IV, WAIS-III, Neuronorma)
  - Casos de prueba documentados (los 8 perfiles validados hoy son un excelente inicio)
- **Validación de usabilidad:** Pruebas con usuarios finales (profesionales de la salud)
- **Pruebas de seguridad:** Penetration testing, validación de autenticación

### 2.6 Análisis de Riesgos (ISO 14971)
Documento formal que identifica:
- Riesgos del software (tabla de riesgos)
- Probabilidad y severidad de cada riesgo
- Medidas de mitigación
- Residual risk después de mitigación
- Aceptabilidad del riesgo residual

**Ejemplo de riesgos para NeuroSoft:**
| Riesgo | Probabilidad | Severidad | Mitigación | Residual |
|---|---|---|---|---|
| Cálculo incorrecto de escalar | Baja | Alta | Tests automatizados + checksum de baremos | Aceptable |
| Pérdida de datos del paciente | Baja | Alta | Backups automáticos + soft delete | Aceptable |
| Acceso no autorizado | Media | Media | Auth JWT + roles + audit log | Aceptable |
| Interrupción del servicio | Media | Baja | Modo offline + SQLite local | Aceptable |

### 2.7 Certificado de Sistema de Gestión de Calidad (opcional para Clase I, recomendado)
- ISO 13485 (sistemas de gestión de calidad para dispositivos médicos)
- Si no se tiene, puede solicitarse el registro sin este certificado, pero es un diferenciador

### 2.8 Declaración de Conformidad del Fabricante
Documento firmado por el representante legal que declara:
- Que el producto cumple con los requisitos esenciales
- Que se ha realizado el control de calidad correspondiente
- Que la información proporcionada es veraz

### 2.9 Evidencia de Software Development Life Cycle (SDLC)
Para software médico, INVIMA espera ver:
- Plan de desarrollo de software
- Requisitos de software documentados
- Arquitectura de software
- Plan de pruebas
- Reportes de pruebas
- Gestión de configuración
- Gestión de cambios
- Registro de bugs y resoluciones

**NeuroSoft ya tiene:**
- Git repository con historial de cambios
- Tests automatizados (pytest)
- CI/CD implícito (build.py)
- Versionado de baremos con checksum
- Documentación en CLAUDE.md

**Falta formalizar:**
- Documento de requisitos de software (SRS)
- Documento de arquitectura
- Plan de pruebas formal
- Reporte de pruebas ejecutadas

---

## 3. PROCESO DE REGISTRO PASO A PASO

### Paso 1: Preparación (2-4 semanas)
- [ ] Reunir todos los documentos listados arriba
- [ ] Elaborar manual de usuario completo
- [ ] Ejecutar suite de pruebas y generar reporte
- [ ] Documentar análisis de riesgos ISO 14971
- [ ] Elaborar etiqueta propuesta
- [ ] Preparar descripción técnica del producto

### Paso 2: Solicitud en línea (1 día)
- [ ] Ingresar a www.invima.gov.co → Servicios en línea → Dispositivos médicos
- [ ] Crear cuenta de usuario (si no existe)
- [ ] Diligenciar formulario de solicitud de registro sanitario
- [ ] Adjuntar todos los documentos en formato PDF
- [ ] Pagar tarifa de registro (~$1.500.000 - $2.500.000 COP estimado para Clase I)

### Paso 3: Evaluación por INVIMA (3-6 meses)
- INVIMA revisa la documentación
- Pueden solicitar aclaraciones o documentos adicionales
- Para Clase I, generalmente no requieren inspección física
- Para software, pueden solicitar demostración funcional

### Paso 4: Respuesta (1-2 semanas después de aprobación)
- Si aprobado: se emite el Registro Sanitario con número único
- Si rechazado: se recibe informe de deficiencias con plazo para corregir
- El registro tiene vigencia de **5 años**

### Paso 5: Renovación (cada 5 años)
- Solicitar renovación 6 meses antes de la expiración
- Presentar evidencia de vigilancia post-mercado (quejas, incidentes)
- Actualizar documentación si hubo cambios significativos

---

## 4. VIGILANCIA POST-MERCADO (OBLIGATORIA)

Una vez registrado, el fabricante debe:

### Reporte de Incidentes
- Reportar al INVIMA cualquier incidente adverso en **10 días hábiles**
- Incidente = cualquier falla del software que pueda haber causado daño
- Ejemplos para NeuroSoft:
  - Pérdida de datos de paciente
  - Cálculo incorrecto que llevó a diagnóstico erróneo
  - Caída del sistema durante evaluación crítica

### Reporte Periódico de Seguridad
- Anual o semestral (según lo determine INVIMA)
- Resumen de quejas recibidas
- Acciones correctivas tomadas
- Tendencias de incidentes

### Recall / Retiro del Mercado
- Si se detecta defecto crítico de seguridad
- Notificación inmediata al INVIMA
- Plan de acción para usuarios afectados

---

## 5. REGLAMENTO DE TELEMEDICINA (Resolución 1409 de 2022)

Si NeuroSoft incluye funciones de:
- Teleconsulta
- Compartir informes con pacientes/remitentes
- Videollamadas
- Mensajería clínica

**Requisitos adicionales:**
- Registro como Prestador de Servicios de Salud (solo si se prestan servicios médicos directos)
- Para software de apoyo: no requiere registro como prestador, pero sí cumplir con:
  - Confidencialidad de comunicaciones
  - Integridad de datos transmitidos
  - Disponibilidad del servicio
  - Consentimiento informado específico para telemedicina

**NeuroSoft actual:** Solo comparte informes (no teleconsulta en tiempo real), por lo que **no requiere registro como prestador**.

---

## 6. PROTECCIÓN DE DATOS (Ley 1581 de 2012)

### Requisitos Obligatorios

#### 6.1 Registro de Bases de Datos ante la SIC
- Registro gratuito en www.sic.gov.co
- Debe hacerse **antes** de iniciar operaciones comerciales
- Requiere:
  - Nombre de la base de datos
  - Descripción de datos tratados
  - Finalidad del tratamiento
  - Mecanismos de consulta
  - Política de privacidad

#### 6.2 Política de Privacidad
Debe estar disponible públicamente e incluir:
- Identidad del responsable del tratamiento
- Datos personales que se recolectan
- Finalidad específica del tratamiento
- Derechos de los titulares (ARCO)
- Procedimiento para ejercer derechos
- Fecha de entrada en vigor
- Mecanismos de seguridad

#### 6.3 Aviso de Privacidad
Debe mostrarse al momento de la recolección de datos:
- Pantalla de registro de paciente
- Primer uso del software
- Cada vez que se crea un nuevo paciente

#### 6.4 Consentimiento Informado
Debe ser:
- Libre (sin coerción)
- Previo (antes de la recolección)
- Expreso (claro e inequívoco)
- Informado (el titular sabe para qué se usan sus datos)

**Para menores de edad:** Consentimiento del representante legal.

#### 6.5 Medidas de Seguridad
- Cifrado de base de datos (SQLCipher recomendado)
- Control de acceso por roles
- Auditoría de accesos
- Backup cifrado
- Eliminación segura cuando corresponda

#### 6.6 Derechos ARCO
Implementar mecanismos para que pacientes puedan:
- **A**cceder: Ver sus datos
- **R**ectificar: Corregir datos incorrectos
- **C**ancelar: Solicitar eliminación
- **O**ponerse: Rechazar ciertos usos

**Nota:** En salud, el derecho de cancelación tiene limitaciones por la Resolución 1995 de 2017 (historia clínica debe conservarse 15 años).

---

## 7. HISTORIA CLÍNICA ELECTRÓNICA (Resolución 1995 de 2017)

### Requisitos para NeuroSoft
- Conservación mínima: **15 años**
- No puede eliminarse físicamente (solo archivado lógico)
- Debe garantizarse confidencialidad
- Debe ser legible durante todo el tiempo de conservación
- Copias de seguridad periódicas
- NeuroSoft ya implementa soft delete — **cumple parcialmente**

### Mejoras necesarias:
- [ ] Exportación a formato estándar (XML, HL7 FHIR)
- [ ] Impresión en formato físico estándar
- [ ] Firma digital de cada entrada
- [ ] Sello de tiempo (timestamp)

---

## 8. CHECKLIST LEGAL COMPLETO

### Antes de la primera venta/distribución:
- [ ] Registro de base de datos ante SIC
- [ ] Política de privacidad publicada
- [ ] Aviso de privacidad en UI
- [ ] Consentimiento informado implementado
- [ ] Disclaimer clínico en informes
- [ ] Manual de usuario completo
- [ ] Análisis de riesgos ISO 14971
- [ ] Reporte de pruebas de verificación
- [ ] Etiqueta propuesta
- [ ] Solicitud de registro INVIMA presentada

### Durante operación:
- [ ] Vigilancia post-mercado activa
- [ ] Backup periódico de datos
- [ ] Auditoría de accesos trimestral
- [ ] Actualizaciones de seguridad oportunas
- [ ] Registro de quejas/incidentes

### Renovación cada 5 años:
- [ ] Actualización de documentación
- [ ] Reporte de vigilancia post-mercado
- [ ] Pago de tarifa de renovación

---

## 9. COSTOS ESTIMADOS (COP)

| Concepto | Costo estimado | Frecuencia |
|---|---|---|
| Tarifa INVIMA registro Clase I | $1.500.000 - $2.500.000 | Única |
| Tarifa INVIMA renovación | $800.000 - $1.500.000 | Cada 5 años |
| Asesoría legal especializada | $3.000.000 - $8.000.000 | Única (preparación) |
| Elaboración de documentación | $2.000.000 - $5.000.000 | Única |
| Certificación ISO 13485 (opcional) | $15.000.000 - $30.000.000 | Cada 3 años |
| Registro SIC base de datos | Gratuito | Única |
| Auditoría de seguridad informática | $5.000.000 - $12.000.000 | Anual |
| Seguro de responsabilidad civil | $2.000.000 - $5.000.000 | Anual |
| **TOTAL INICIAL ESTIMADO** | **~$15.000.000 - $35.000.000** | |
| **TOTAL ANUAL ESTIMADO** | **~$7.000.000 - $17.000.000** | |

---

## 10. TIMELINE SUGERIDO

| Fase | Duración | Actividades |
|---|---|---|
| Preparación documental | 4-6 semanas | Manual, riesgos, pruebas, etiqueta |
| Asesoría legal | 2-3 semanas | Revisión de documentos, estrategia regulatoria |
| Solicitud INVIMA | 1 semana | Presentación en línea, pago |
| Evaluación INVIMA | 3-6 meses | Espera, posibles aclaraciones |
| Correcciones (si aplica) | 2-4 semanas | Atender requerimientos del INVIMA |
| **TOTAL ESTIMADO** | **5-8 meses** | Desde preparación hasta aprobación |

---

## 11. RECURSOS OFICIALES

- INVIMA: www.invima.gov.co
- SIC (Protección de Datos): www.sic.gov.co
- Ministerio de Salud: www.minsalud.gov.co
- Decreto 677 de 1995: www.secretariasenado.gov.co
- Resolución 481 de 2022: www.invima.gov.co
- Resolución 1409 de 2022 (Telemedicina): www.minsalud.gov.co
- Resolución 1995 de 2017 (Historia Clínica): www.minsalud.gov.co

---

## NOTA IMPORTANTE

Este documento es una **guía de investigación preliminar** basada en conocimiento regulatorio. **No constituye asesoría legal.** Se recomienda encarecidamente consultar con un abogado especializado en derecho sanitario y regulación de dispositivos médicos en Colombia antes de iniciar cualquier proceso formal ante el INVIMA.

---

*Documento generado por NeuroSoft AI Assistant como parte de investigación extensiva solicitada.*
