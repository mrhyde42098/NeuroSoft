# Mapa de Riesgos — NeuroSoft App

**Versión:** 2.0 · **Fecha:** 2026-06-03

Matriz de riesgos identificados, su probabilidad, impacto y mitigación. Cubre riesgos técnicos, clínicos, regulatorios y operativos.

---

## 1. Matriz resumen

| # | Riesgo | Probabilidad | Impacto | Mitigación actual | Residual |
|---|---|---|---|---|---|
| R1 | Baremos incorrectos (AdBeck) | Media | Crítico | F7.2 plan + validación web Beck et al. 1996 | Bajo |
| R2 | Bug silencioso en motor de scoring | Baja | Crítico | 27 tests engine + 134 ground truth + audit mensual | Muy bajo |
| R3 | Filtración de PHI por audit log | Baja | Crítico | F10.1.3 redacción PHI + whitelist | Muy bajo |
| R4 | Pérdida de BD sin backup | Baja | Crítico | Backups automáticos cifrados (S4.3) | Muy bajo |
| R5 | Pearson reclama copyright | Baja | Alto | S5.x verbatim one-time + disclaimers + audit log | Bajo |
| R6 | Cambio regulatorio MinSalud no anticipado | Baja | Alto | Monitoreo bimestral normograma + suscripción SIC | Medio |
| R7 | Beta tester reporta bug clínico post-release | Media | Crítico | Ground truth + hotfix <24h + rollback | Bajo |
| R8 | Auto-update mal firmado | Baja | Crítico | HMAC-SHA256 (S0.1) | Muy bajo |
| R9 | Reclamación de tercero por atribución | Baja | Medio | Scrub completo + docs internos sin atribución | Bajo |
| R10 | Saturación de rate limiter por uso legítimo | Baja | Bajo | 5 req/min por IP configurable vía env | Muy bajo |
| R11 | Pérdida de SECRET_KEY | Baja | Crítico | Backups externos + plan de rotación documentado | Bajo |
| R12 | Falla de energía durante evaluación | Media | Bajo | UPS + guardado incremental + auto-save | Muy bajo |
| R13 | Versión PDF incompatible con lectores | Baja | Medio | Test con 5 lectores (Adobe, Foxit, navegador) | Muy bajo |
| R14 | Saturación de IA cloud (rate limit provider) | Media | Bajo | Fallback a Ollama local + caché de respuestas | Bajo |
| R15 | PHI enviado a cloud por error | Baja | Crítico | F5 sanitización + log de prompts | Muy bajo |

---

## 2. Detalle de riesgos críticos (R1, R2, R3, R4, R7, R8, R11, R15)

### R1 — Baremos incorrectos (AdBeck)

**Descripción:** La entrada `AdBeck` en `data/BD_NEURO_MAESTRA.json` tiene una estructura con valores atípicos (`1619`) que no corresponden al baremo oficial del BDI-II (Beck, Steer & Brown, 1996).

**Probabilidad:** Media (dato ya verificado, falta ejecutar la migración).

**Impacto:** Crítico (afecta la impresión diagnóstica de pacientes con depresión).

**Mitigación actual:**
- F7.1 auditoría identificó la anomalía.
- F7.2 plan de migración con 10 fases documentado.
- Validación con literatura (web research en Beck et al. 1996 + Bonnett et al. 2004).
- Backup defensivo antes de cualquier cambio.

**Riesgo residual:** Bajo (post-ejecución de F7.2.1-F7.2.10).

**Plan de contingencia:** Si la migración causa regresión en ground truth, rollback al backup y bloqueo del test en el motor con flag `baremo_en_revision`.

---

### R2 — Bug silencioso en motor de scoring

**Descripción:** Una falla no detectada en `strategies.py` o `engine.py` podría producir un escalar clínico incorrecto sin que el clínico lo note.

**Probabilidad:** Baja (gracias a la cobertura de tests).

**Impacto:** Crítico (escalares clínicos reales; un CI mal calculado = diagnóstico incorrecto).

**Mitigación actual:**
- 27 tests del engine clínico (pytest).
- 134 escalares verificados en 15 ground truth fixtures.
- Audit mensual del comportamiento del motor (siguiente: 2026-07-01).
- Alertas automáticas si se detecta un valor anómalo (> 3 SD del baremo).

**Riesgo residual:** Muy bajo.

**Plan de contingencia:** Smoke test post-cambio de baremos + revisión manual por clínico antes de release.

---

### R3 — Filtración de PHI por audit log

**Descripción:** El listener SQLAlchemy podría serializar campos sensibles (HC, motivo, antecedentes) en el campo `changes` del audit log.

**Probabilidad:** Baja (F10.1.3 cerró el riesgo).

**Impacto:** Crítico (Ley 1581/2012 art. 17h — notificación obligatoria a SIC).

**Mitigación actual:**
- Whitelist de campos auditables en `audit/listeners.py`.
- Hash SHA-256 de campos sensibles (no se almacena el valor).
- Test de regresión que sube un paciente, hace cambios, lee audit y valida que NO hay PII.

**Riesgo residual:** Muy bajo.

**Plan de contingencia:** Si se detecta filtración, notificación a SIC en 15 días hábiles (Circular 005/2017).

---

### R4 — Pérdida de BD sin backup

**Descripción:** Falla de hardware, ransomware, o error humano podría dejar la BD irrecuperable.

**Probabilidad:** Baja.

**Impacto:** Crítico (Res. 1995/1999 obliga a conservar HC por 15+ años).

**Mitigación actual:**
- Backups automáticos diarios/semanales/mensuales (S4.3).
- Cifrado AES-256 + HMAC.
- Verificación de integridad (SHA-256).
- DRP documentado en `docs/DRP.md` con RTO ≤ 4h, RPO ≤ 24h.

**Riesgo residual:** Muy bajo.

**Plan de contingencia:** Restauración desde último backup verificado + acta de disposición (F5.4).

---

### R7 — Beta tester reporta bug clínico post-release

**Descripción:** Después de distribuir el release, un beta tester descubre un bug que afecta el scoring o el informe.

**Probabilidad:** Media (1-2 reportes esperados por trimestre).

**Impacto:** Crítico (depende del bug; peor caso: escalar mal calculado).

**Mitigación actual:**
- 855+ tests backend + 134 ground truth.
- 6 Playwright E2E.
- Hotfix SLA: <24h para crítico, <72h para alto.
- Rollback documentado: `git tag` + `git checkout` + re-build.

**Riesgo residual:** Bajo.

**Plan de contingencia:** Si el bug afecta pacientes reales: (1) notificación a beta tester, (2) emisión de fe de erratas para informes afectados, (3) fix + re-release, (4) actualización de ground truth.

---

### R8 — Auto-update mal firmado

**Descripción:** Si un atacante puede firmar un `.nsupdate` con la clave correcta (o la clave se filtra), puede ejecutar código arbitrario en el servidor.

**Probabilidad:** Baja (F10.1.1 cerró la mayoría de vectores).

**Impacto:** Crítico (ejecución remota de código = compromiso total).

**Mitigación actual:**
- HMAC-SHA256 con clave en `NEUROSOFT_UPDATE_HMAC_KEY` (separada de SECRET_KEY).
- Endpoint `/system/update` requiere rol admin (F10.1.1).
- Log obligatorio de user_id que subió el update.
- Verificación post-update: si el HMAC no coincide, rollback automático.

**Riesgo residual:** Muy bajo.

**Plan de contingencia:** Si se compromete la clave: rotación inmediata + auditoría de todos los updates previos.

---

### R11 — Pérdida de SECRET_KEY

**Descripción:** Si la SECRET_KEY se pierde (disco dañado, .env no respaldado), todos los JWT emitidos quedan invalidados y los datos cifrados con Fernet son irrecuperables.

**Probabilidad:** Baja (con backups).

**Impacto:** Crítico (todos los datos sensibles cifrados se perderían).

**Mitigación actual:**
- Backups del .env en disco externo (procedimiento documentado).
- SECRET_KEY derivable de un master password (configurable, no obligatorio).
- Datos sensibles en BD son Fernet (cifrado simétrico); con la clave pueden recuperarse.

**Riesgo residual:** Bajo.

**Plan de contingencia:** Si se pierde la clave: (1) los JWTs emitidos se invalidan (los usuarios deben re-login), (2) los datos cifrados con Fernet son irrecuperables — restaurar desde backup ANTES del cifrado (es decir, del SQLite pre-encryption migration).

---

### R15 — PHI enviado a cloud por error

**Descripción:** El asistente IA podría recibir un prompt que contenga datos del paciente (documento, nombre, motivo) y enviarlo a Gemini/Claude/OpenAI.

**Probabilidad:** Baja (F5 sanitización implementada).

**Impacto:** Crítico (Ley 1581/2012 art. 17h + HIPAA internacional).

**Mitigación actual:**
- `sanitize_clinical_input()` quita documentos, fechas, emails, teléfonos.
- Log de prompts en `ai_logs` con metadata (NO contenido).
- Modo "Ollama local" como opción por defecto para beta tester.
- Banner persistente en pantalla cuando se usa IA: "Los datos se envían a un proveedor cloud".

**Riesgo residual:** Muy bajo.

**Plan de contingencia:** Si se detecta filtración: (1) deshabilitar cloud IA inmediatamente, (2) notificar SIC en 15 días hábiles, (3) cambiar a Ollama local permanente.

---

## 3. Riesgos regulatorios (R6)

### R6 — Cambio regulatorio no anticipado

**Descripción:** MinSalud o la SIC emiten una nueva resolución que afecta el formato de informes, retención de HC, RIPS, etc.

**Probabilidad:** Baja (cambios cada 2-3 años).

**Impacto:** Alto (requiere actualización de código + plantillas + re-distribución).

**Mitigación actual:**
- Monitoreo bimestral de normograma (responsable: Johan Salgado).
- Suscripción a alertas SIC y MinSalud.
- Diseño modular permite actualizar plantillas sin tocar lógica.
- `NORMOGRAMA_COLOMBIANO_VERSION` bumpeado al cambiar (lockstep frontend/backend).

**Riesgo residual:** Medio.

**Plan de contingencia:** Si hay cambio: emitir parche en <7 días con re-emisión del bloque legal.

---

## 4. Plan de revisión

- **Trimestral:** revisión de la matriz, actualización de mitigaciones.
- **Tras incidente:** post-mortem + actualización del mapa.
- **Anual:** auditoría externa de seguridad (recomendado, no obligatorio).

---

## 5. Aceptación de riesgos

El responsable del tratamiento (Johan Sebastián Salgado Sarmiento) ACEPTA los siguientes riesgos residuales como parte del modelo de operación unipersonal:

- **R10** Saturación de rate limiter en uso legítimo — mitigado por capacidad de ajustar `NEUROSOFT_RATE_LIMIT_PER_MIN`.
- **R12** Falla de energía — mitigado por guardado incremental y por el modelo de backup (no se trabaja simultáneamente en dos sesiones).

Cualquier otro riesgo residual MEDIO o ALTO requiere acción inmediata.
