# Procedimiento de Gestión de Incidentes de Seguridad y Privacidad

**Normograma aplicable:** Ley 1581 de 2012, art. 17 literales (g) y (h) · Decreto 1377 de 2013, art. 22 · Circular Externa 005 de 2017 (SIC) · Ley 1273 de 2009 (delitos informáticos) · Ley 1581/2012, art. 18 (sanciones).

**Alcance:** Todo incidente que afecte la confidencialidad, integridad o disponibilidad de datos personales tratados por NeuroSoft App, incluyendo:

- Acceso no autorizado a la base de datos de historias clínicas.
- Modificación, alteración o destrucción no autorizada de datos clínicos.
- Pérdida de respaldo cifrado (backup Fernet).
- Vulneración de credenciales (filtración de JWT secret, contraseñas en logs, etc.).
- Caída del servicio que impida atender pacientes por > 4 horas.
- Inconsistencias detectadas en el módulo de auditoría clínica.

---

## 1. Definiciones

| Término | Definición |
|---|---|
| **Incidente** | Evento confirmado o sospechoso que comprometa la confidencialidad, integridad o disponibilidad de datos personales o clínicos. |
| **Responsable del tratamiento** | Johan Sebastián Salgado Sarmiento, propietario de NeuroSoft App. |
| **Encargado** | Persona o sistema que trata datos por cuenta del responsable. En la versión actual no hay encargados externos; el software opera en el consultorio del responsable. |
| **Titular** | Paciente o acompañante cuyos datos son tratados. |
| **SIC** | Superintendencia de Industria y Comercio — autoridad de vigilancia en protección de datos en Colombia. |
| **RNBD** | Registro Nacional de Bases de Datos — inscripción ante la SIC. |
| **SGSI** | Sistema de Gestión de Seguridad de la Información — marco de controles. |

---

## 2. Clasificación de incidentes

| Severidad | Criterios | SLA respuesta | SLA notificación SIC | SLA notificación titulares |
|---|---|---|---|---|
| **Crítico (I)** | Pérdida o acceso no autorizado a > 100 HCs. Modificación de datos clínicos. Caída de servicio > 4h. | Inmediato (≤ 1h) | **15 días hábiles** desde detección | **5 días hábiles** desde detección |
| **Alto (II)** | Acceso no autorizado a 1-100 HCs. Vulneración de credenciales admin/beta. Pérdida de respaldo cifrado sin compromiso de clave. | ≤ 4h | **15 días hábiles** | **5 días hábiles** |
| **Medio (III)** | Intento de acceso bloqueado. Anomalía detectada pero sin impacto confirmado. Falla de bitácora de auditoría. | ≤ 24h | Reporte en informe anual SIC | No obligatoria |
| **Bajo (IV)** | Caída de UI sin pérdida de datos. Logs con warnings de seguridad. | ≤ 72h | Solo acumulado anual | No obligatoria |

**Base normativa de plazos:** Circular Externa 005/2017 SIC §III, numerales 2.2 y 2.3 (15 días hábiles para reportar incidentes que afecten datos sensibles); Ley 1581/2012 art. 17h.

---

## 3. Flujo de respuesta

### 3.1 Detección y reporte interno

1. **Detección**: Puede ser:
   - Automática (rate limiter, audit listener SQLAlchemy, sistema de monitoreo de backups).
   - Manual (reporte de un usuario, queja de un paciente, hallazgo en revisión).
   - Externa (denuncia, investigación de autoridad).

2. **Reporte interno**: Cualquier persona del equipo (o, en esta versión, el único responsable) que detecte un incidente debe:
   - Documentar fecha/hora exacta del evento o de la detección.
   - Preservar evidencia (logs, volcado de BD, capturas).
   - Iniciar el cuaderno del incidente (`docs/seguridad/INCIDENTES.md`).

3. **Activación**: Si severidad ≥ II, el responsable activa el modo de contención (ver §3.2).

### 3.2 Contención (primeras 4 horas)

| Acción | Comando / Procedimiento |
|---|---|
| Bloquear acceso de credenciales comprometidas | Invalidar JWT vigente (rotar `NEUROSOFT_SECRET_KEY`); forzar logout de todas las sesiones. |
| Aislar base de datos | Detener servicio (`uvicorn`), copiar BD a `forensics/` para análisis, no usar la original. |
| Preservar logs | Respaldar `data/logs/` y stdout a almacenamiento inmutable. No rotar logs. |
| Bloquear endpoint afectado | Si aplica, montar `MaintenanceMiddleware` o cerrar la ruta en `main.py`. |
| Cambiar claves críticas | `SECRET_KEY`, `NEUROSOFT_BETA_PASSWORD`, password cifrada SMTP (Fernet). |

### 3.3 Investigación (días 1-10)

1. **Análisis forense** sobre la copia de BD:
   - `audit_logs` (tabla `ai_logs`, `audit_listeners`) — buscar accesos anómalos.
   - Timestamps, IPs, user-agents de eventos sospechosos.
   - Identificar vector de ataque: SQL injection, robo de credencial, vulnerabilidad en dependencia, insider.

2. **Documentar causa raíz** en `docs/seguridad/INCIDENTES.md`:
   - Cronología detallada.
   - Datos afectados (tipos, volumen, sensibilidad).
   - Categorías de titulares impactados.
   - Controles que fallaron.
   - Controles que funcionaron.

3. **Evaluar alcance real** vs. alcance potencial:
   - ¿Qué datos se accedieron/modificaron de hecho?
   - ¿Qué datos estaban expuestos pero no accedidos?

### 3.4 Notificación a la SIC (días 1-15 hábiles)

**Plazo:** 15 días hábiles desde la detección. Si se requiere prórroga, solicitar formalmente antes del día 10.

**Canal:**
- Formulario web en https://www.sic.gov.co/responsabilidad-demostrada (módulo "Reporte de incidentes").
- Correo físico a la Superintendencia (Delegatura para la Protección de Datos).
- Si afecta > 10.000 titulares, adicionalmente al CERT de MinTIC.

**Contenido del reporte (Circular Externa 005/2017 SIC):**

1. Datos del responsable del tratamiento.
2. Fecha y hora de detección del incidente.
3. Fecha y hora estimada de inicio del incidente.
4. Descripción del incidente y vectores identificados.
5. Categorías de datos personales afectados (sensible: salud).
6. Número estimado de titulares afectados.
7. Medidas de contención adoptadas.
8. Plan de remediación.
9. Datos de contacto del responsable para seguimiento.
10. Certificación de inscripción en el RNBD (si aplica).

**Plantilla interna:** `docs/seguridad/PLANTILLA_REPORTE_SIC.md` (a crear en primera iteración).

### 3.5 Notificación a titulares (días 1-5 hábiles)

**Plazo:** 5 días hábiles desde la confirmación del alcance real.

**Canal preferido (Ley 1581 art 17h):**
- Correo electrónico (si el titular lo autorizó en la HC).
- Mensaje en la próxima sesión presencial.
- Carta física como último recurso (custodia de 5 años).

**Contenido mínimo al titular:**

1. Descripción clara del incidente y sus posibles consecuencias.
2. Tipos de datos afectados.
3. Medidas adoptadas por el responsable.
4. Medidas recomendadas al titular (rotación de contraseñas, monitoreo de credenciales, etc.).
5. Datos de contacto para consultas.
6. Derecho a presentar queja ante la SIC.

**Excepciones** (no notificación individual):
- Datos estaban cifrados de forma que la clave no fue comprometida.
- Se han tomado medidas que neutralizan el riesgo de daño.
- La notificación exige un esfuerzo desproporcionado (en ese caso, publicar aviso público).

### 3.6 Remediación y cierre (días 15-30)

1. **Aplicar controles correctivos** según causa raíz.
2. **Verificar eficacia** mediante pruebas de penetración internas o revisión por par.
3. **Documentar lecciones aprendidas** en `docs/seguridad/POSTMORTEM_<INCIDENTE>.md`:
   - ¿Qué funcionó?
   - ¿Qué falló?
   - ¿Qué se cambia para que no se repita?
4. **Actualizar** `MODELO_AMENAZAS.md` con el nuevo vector.
5. **Cerrar el incidente** formalmente con acta firmada por el responsable.

---

## 4. Matriz de roles (versión single-user actual)

| Rol | Persona |
|---|---|
| **Responsable del tratamiento** | Johan Sebastián Salgado Sarmiento |
| **Encargado del tratamiento** | N/A (no hay terceros en versión actual) |
| **Oficial de seguridad** | Johan Sebastián Salgado Sarmiento (rol autoasignado) |
| **Operador de base de datos** | Johan Sebastián Salgado Sarmiento |
| **Desarrollador de respuesta** | Johan Sebastián Salgado Sarmiento |

> En la versión actual del sistema (consultorio unipersonal), el mismo individuo cubre los cinco roles. Esto es aceptado por la SIC siempre que la segregación de funciones esté respaldada por controles técnicos automatizados (audit logs inmutables, JWT firmado, bitácora de accesos). Si en el futuro se agregan otros usuarios, se debe implementar segregación real.

---

## 5. Comunicación con la autoridad

### 5.1 SIC — Superintendencia de Industria y Comercio

- **Web:** https://www.sic.gov.co/proteccion-de-datos-personales
- **Teléfono:** +57 (1) 587 0000 ext. 20100
- **Canal PQRS:** https://www.sic.gov.co/responsabilidad-demostrada
- **Plazo legal de respuesta a quejas de titulares:** 15 días hábiles.

### 5.2 MinTIC — Ministerio de Tecnologías de la Información

Solo si el incidente supera 10.000 titulares o afecta infraestructura crítica nacional. En ese caso, notificar al **ColCERT** (Grupo de Respuesta a Emergencias Cibernéticas):
- **Web:** https://www.colcert.gov.co/
- **Email:** contacto@colcert.gov.co

### 5.3 Fiscalía General de la Nación

Si el incidente involucra:
- Hurto o comercialización no autorizada de datos (art. 269A-C Código Penal, Ley 1273/2009).
- Suplantación de identidad (art. 296 Código Penal).
- Acceso abusivo a sistema informático (art. 269A).

Denunciar en: https://www.fiscalia.gov.co/

---

## 6. Bitácora de incidentes

Cada incidente se registra en `docs/seguridad/INCIDENTES.md` con:

```markdown
## INC-YYYY-NNN: <título corto>

- **Fecha detección:** YYYY-MM-DD HH:MM
- **Severidad:** I | II | III | IV
- **Estado:** detección | contención | investigación | notificación | remediación | cerrado
- **Vector:** sqli | credencial_robada | insider | dependencia_vulnerable | otro
- **Datos afectados:** [categorías]
- **Titulares afectados (n):** N
- **SIC notificado:** sí/no (fecha)
- **Titulares notificados:** sí/no (fecha)
- **Resumen:** (1-3 líneas)
- **Link al reporte completo:** docs/seguridad/INCIDENTES/INC-YYYY-NNN.md
```

---

## 7. Limitaciones reconocidas

1. **Sin SGSI certificado:** NeuroSoft no está certificada ISO 27001 ni Habeas Data. El procedimiento documenta buenas prácticas, no un sistema formal certificado.
2. **Sin red de contención aislada:** No hay red de cuarentena; la contención se hace sobre el mismo hardware.
3. **Auditoría humana única:** La validación periódica de logs la hace el responsable sin par revisor. Riesgo aceptado por el modelo unipersonal.
4. **Sin redundancia geográfica de backups:** El DRP (`docs/DRP.md`) tiene como máximo un respaldo en un disco externo local. Sin réplica off-site.
5. **Notificación SIC manual:** El envío del reporte se hace por formulario web; no hay integración automatizada con la SIC.

Estas limitaciones se compensan con:
- Audit log append-only a nivel de ORM.
- Bitácora con hash chain.
- JWT firmado con expiración explícita.
- SECRET_KEY rotable y blacklist de tokens.
- Rate limiting por IP.
- Validación de entrada en TODAS las rutas (Pydantic + ownership check).

---

## 8. Referencias

- **Ley 1581 de 2012**, arts. 17g, 17h, 18 — Deberes del responsable, plazos de notificación, sanciones.
- **Decreto 1377 de 2013**, art. 22 — Procedimiento para reporte de incidentes.
- **Circular Externa 005 de 2017 SIC** — Lineamientos para reportar incidentes de seguridad.
- **Ley 1273 de 2009** — Delitos informáticos (arts. 269A-E).
- **Resolución 1995 de 1999** — Historia clínica (numeral 14: deber de confidencialidad).
- **Ley 1090 de 2006** — Código Deontológico del Psicólogo (art. 36: secreto profesional).
- `docs/seguridad/MODELO_AMENAZAS.md` — Análisis STRIDE previo.
- `docs/DRP.md` — Plan de recuperación ante desastres (RTO ≤ 4h, RPO ≤ 24h).
