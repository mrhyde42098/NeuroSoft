# Flujo de Datos — NeuroSoft App

**Versión:** 2.0 · **Fecha:** 2026-06-03

Diagrama de flujo de datos (DFD) nivel 1: cómo viaja la información desde la captura clínica hasta el informe final.

---

## 1. Diagrama (texto, nivel 1)

```
┌─────────────┐
│  PSICÓLOGO  │ (usuario)
│  CLÍNICO    │
└──────┬──────┘
       │ 1) Login (username + password)
       ▼
┌──────────────────────────────────────┐
│  FRONTEND (React + Vite + pywebview) │
└──────┬───────────────────────────────┘
       │ HTTPS / Bearer JWT
       ▼
┌──────────────────────────────────────┐
│  BACKEND FastAPI                     │
│  ┌───────────────────────────────┐   │
│  │ Auth (JWT + rate limit)       │   │
│  │  → 401 si token inválido      │   │
│  └───────┬───────────────────────┘   │
│          ▼                            │
│  ┌───────────────────────────────┐   │
│  │ Rutas /api/v1/*               │   │
│  │  → presentation/api/v1/...    │   │
│  └───────┬───────────────────────┘   │
│          ▼                            │
│  ┌───────────────────────────────┐   │
│  │ Use Cases (application/)      │   │
│  └───────┬───────────────────────┘   │
│          ▼                            │
│  ┌───────────────────────────────┐   │
│  │ Dominio (clinical_engine)     │   │
│  │  → strategies.py              │   │
│  │  → engine.py                  │   │
│  │  → baremos_loader.py          │   │
│  └───────┬───────────────────────┘   │
│          ▼                            │
│  ┌───────────────────────────────┐   │
│  │ Repositorios (infrastructure) │   │
│  │  → ORM SQLAlchemy             │   │
│  └───────┬───────────────────────┘   │
└──────────┼────────────────────────────┘
           ▼
┌──────────────────────────────┐
│  SQLITE (data/neurosoft.db)  │
│  + Alembic migrations        │
└──────────────────────────────┘
           ▲
           │ Lectura
┌──────────┴────────────────────────┐
│  ReportLab PDF                    │
│  → report_pro (7 variantes)       │
│  → bytes PDF                      │
└──────────┬────────────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Descarga / Email / Impresión │
└──────────────────────────────┘
```

---

## 2. Casos de uso principales

### 2.1 Captura de evaluación

```
1. Psicólogo abre EvalApplyPage
2. Carga protocolo sugerido (F6.1 sugerenciaProtocolo) o selecciona manualmente
3. Para cada test:
   a. Lee ítems desde protocolLoader.js (frontend)
   b. Captura PD (puntaje directo) por ítem
   c. Cronómetro mide tiempo
4. Click "Calcular" → POST /api/v1/evaluaciones
5. Backend:
   a. Validate input (Pydantic)
   b. Audit log entry (listeners.py)
   c. ClinicalEngine.score(puntajes, ctx)
   d. Persiste ResultadosPrueba en BD
   e. Retorna EngineResult con interpretaciones
6. Frontend renderiza EvalResultsPage
7. Psicólogo redacta impresión diagnóstica en texto libre
```

### 2.2 Generación de informe

```
1. Click "Descargar PDF" en EvalResultsPage
2. POST /api/v1/reports/pdf/{eval_id}?template=pro
3. Backend:
   a. Carga ReportData desde BD
   b. Construye narrativa con narrative.py (valida 7 principios F6.2 + F9.2)
   c. Llama generate_pro_pdf(data, template) en report_pro
   d. Inyecta metadatos PDF/A (F9.3)
   e. Inyecta bloque legal del encabezado (F9.3)
   f. Footer con normograma 2026.06 (F5.3)
   g. Retorna bytes PDF
4. Frontend descarga el archivo
5. Si email: POST /api/v1/reports/{eval_id}/send-email (F5.1 plantilla)
```

### 2.3 Screening (tamizaje)

```
1. Psicólogo abre ScreeningPage
2. F8.2: ScreeningWizard sugiere batería según motivo + edad
3. Psicólogo selecciona test (PHQ-9, GAD-7, MMSE, etc.)
4. Captura respuestas (ítems Likert o binarios)
5. Click "Guardar" → POST /api/v1/patients/{id}/screening
6. Backend:
   a. Calcula score con computeResult
   b. Detecta red-flags (p.ej. PHQ-9 ítem 9 = ideación suicida → C-SSRS)
   c. Persiste como observación clínica del paciente
7. Frontend muestra resultado + interpretación + recomendaciones
```

### 2.4 Aplicación de protocolo de orden clínico

```
1. OrdenClinicoBanner muestra siguiente test recomendado
2. Timer mide ≥20 min entre codificación y recobro Grober
3. Detección de interferencias (TMT-B después de TMT-A)
4. Actualización del estado del protocolo
```

---

## 3. Almacenamiento

### 3.1 Base de datos SQLite

| Tabla | Propósito | Datos sensibles |
|---|---|---|
| `users` | Credenciales de acceso | hashed_password (bcrypt) |
| `patients` | Datos demográficos del paciente | documento, nombre, contacto |
| `clinical_histories` | Historia clínica completa | antecedentes, motivo, alergias |
| `evaluations` | Evaluaciones neuropsicológicas | puntajes, observaciones, conclusiones |
| `pruebas` | Catálogo de pruebas | (catálogo, no datos de pacientes) |
| `results` | Resultados detallados por subtest | escalares, percentiles, bandas |
| `companions` | Acompañantes del paciente | nombre, parentesco, contacto |
| `risk_assessments` | Evaluaciones C-SSRS | nivel de riesgo, plan de seguridad |
| `audit_logs` | Bitácora inmutable de accesos | user_id, timestamp, action |
| `ai_logs` | Trazabilidad de uso de IA | prompt, tokens, NO contenido PHI |
| `therapy_sessions` | Sesiones clínicas | notas SOAP |
| `config_smtp` | Configuración SMTP | password cifrada con Fernet |
| `config_email_templates` | Plantillas email editables | contenido HTML |
| `screening_results` | Resultados de screening | score + interpretación |

### 3.2 Archivos

| Archivo | Ubicación | Cifrado |
|---|---|---|
| `data/neurosoft.db` | Raíz backend | No (SQLite + Fernet para campos sensibles) |
| `data/BD_NEURO_MAESTRA.json` | Backend | No (solo lectura) |
| `data/backups/*.enc.gz` | Backend | AES-256 + HMAC (S4.3) |
| `app/assets/fonts/*.ttf` | Backend | No (Inter, Lora) |
| `institucion_*` | BD (tabla config) | AES-256 (S4.3 crypto.py) |

### 3.3 LocalStorage (frontend)

| Clave | Contenido | Cifrado |
|---|---|---|
| `ns_token` | JWT | No (Bearer es un token firmado, no reversible) |
| `ns_user_id` | UUID del usuario | No |
| `ns_user_name` | Nombre del usuario | No |
| `ns_user_role` | Rol | No |
| `ns_pearson_consent_global` | Timestamp de aceptación | No |
| `ns_pearson_consent_version` | Versión del acuerdo | No |
| `ns_dark` | Modo oscuro (on/off) | No |
| `ns_high_contrast` | Alto contraste (on/off) | No |
| `ns_a11y_font_scale` | Escala de fuente | No |
| `ns_aprender_*` | Progreso Leitner boxes | No |

> **Nota de seguridad:** LocalStorage es XSS-vulnerable. Los items sensibles (PHI) NUNCA van a localStorage. El JWT se considera aceptable porque: (a) tiene expiración corta, (b) está firmado con HMAC, (c) tiene blacklist server-side.

---

## 4. Eventos de auditoría

Todos estos eventos disparan una entrada en `audit_logs`:

| Evento | Endpoint | Campos auditados |
|---|---|---|
| Login exitoso | POST /auth/login | user_id, ip, timestamp |
| Login fallido | POST /auth/login | user_id (si existe), ip |
| Crear paciente | POST /api/v1/patients | user_id, patient_id (hash) |
| Ver paciente | GET /api/v1/patients/{id} | user_id, patient_id (hash) |
| Modificar paciente | PUT /api/v1/patients/{id} | user_id, patient_id (hash), cambios (whitelist) |
| Eliminar paciente | DELETE /api/v1/patients/{id} | user_id, patient_id (hash) |
| Crear evaluación | POST /api/v1/evaluaciones | user_id, eval_id |
| Generar PDF | POST /api/v1/reports/pdf/{id} | user_id, eval_id, template |
| Enviar email | POST /api/v1/reports/{id}/send-email | user_id, eval_id, destinatario (hash) |
| Backup | scheduler | timestamp, ruta, sha256 |
| Restore | admin endpoint | timestamp, ruta, user_id |
| Cambio de config | PUT /api/v1/config/* | user_id, campos modificados |
| Logout | POST /auth/logout | user_id, jti (token revocado) |

**Redacción PHI en audit:** los campos sensibles (HC, motivo, antecedentes, documentos, observaciones) NO se serializan. Se hashean con SHA-256 y se almacena el hash.

---

## 5. Backups

- **Automáticos** vía APScheduler (S4.3):
  - Diario a las 02:00 (retención 7 días)
  - Semanal domingo 03:00 (retención 30 días)
  - Mensual día 1 (retención 365 días)
- **Cifrado:** AES-256 + HMAC-SHA256 con clave derivada de `SECRET_KEY`.
- **Ubicación:** `data/backups/` (local) + manual a disco externo.
- **Verificación:** SHA-256 del plaintext se almacena en `BackupMetadata`.

Ver `docs/DRP.md` para RTO/RPO.

---

## 6. Eventos externos

| Evento | Origen | Acción |
|---|---|---|
| Email entrante (confirmación de cita) | SMTP | Procesar y guardar en inbox |
| Webhook de pago (RIPS/factura) | DIAN | No aplica aún (F19) |
| Alerta de saturación de oxígeno | (no aplica — sistema clínico) | — |
| Auto-update | GitHub Releases | Verificar HMAC + aplicar (S0.1) |
