# MODELO DE AMENAZAS — NeuroSoft App

> **S0.8 del PLAN_MAESTRO_GLOBAL** · Fecha: 2026-06-01 · Estado: aprobado.
>
> Documento vivo. Cualquier nueva feature que toque auth, PHI, red o
> persistencia debe pasar por este análisis antes de merge.

## 1. Alcance

**Dentro del alcance:**
- Backend FastAPI (`app/`).
- Frontend React/Vite (`neurosoft-frontend/src/`).
- Empaquetado PyInstaller + Inno Setup (`.exe` desktop).
- Actualizaciones OTA vía `/api/v1/system/update`.
- Persistencia SQLite local + backups.
- IA opcional (Gemini/Claude/OpenAI/Ollama) — proveedor configurable.

**Fuera del alcance:**
- Infraestructura de los proveedores IA (Gemini API, Claude API, etc.).
- Sistema operativo del usuario final (Windows 10/11).
- Hardware físico / robo del equipo.

## 2. Metodología

**STRIDE** (Microsoft Threat Modeling):
- **S**poofing — suplantación de identidad.
- **T**ampering — alteración de datos.
- **R**epudiation — negación de acciones.
- **I**nformation Disclosure — fuga de información.
- **D**enial of Service — denegación de servicio.
- **E**levation of Privilege — escalada de privilegios.

Cada amenaza tiene: vector, activo afectado, probabilidad, impacto, mitigación actual, mitigación pendiente.

## 3. Activos

| ID | Activo | Clasificación | Ubicación |
|---|---|---|---|
| A1 | Historia clínica del paciente | Confidencial (PHI) | `data/neurosoft.db` (SQLite) |
| A2 | Evaluaciones neuropsicológicas | Confidencial (PHI) | `data/neurosoft.db` |
| A3 | Informes PDF firmados | Confidencial (PHI) | `data/reports/` |
| A4 | Credenciales de usuarios | Secreto | `users.hashed_password` (bcrypt) |
| A5 | SECRET_KEY (JWT) | Secreto crítico | `app/core/config.py` / env var |
| A6 | Audit log (Res. 1995/1999) | Trazabilidad legal | `audit_log` table |
| A7 | Baremos `BD_NEURO_MAESTRA.json` | Integridad clínica | `data/BD_NEURO_MAESTRA.json` |
| A8 | HMAC update signature key | Secreto | `NEUROSOFT_UPDATE_HMAC_KEY` |
| A9 | SMTP password | Secreto | `config_smtp.password` (Fernet AES) |
| A10 | Código de instalación Windows | Software | Distribuido al usuario |

## 4. Diagrama de flujo de datos (DFD)

```
┌──────────────┐    HTTPS local    ┌─────────────────────┐
│  Frontend    │ ◄───────────────► │ FastAPI backend     │
│  React/Vite  │   JWT Bearer      │ (pywebview)         │
│  (Browser)   │                   │                     │
└──────────────┘                   │ ┌────────────────┐  │
                                   │ │ auth/ownership │  │
                                   │ │ rate limit     │  │
                                   │ │ audit listener │  │
                                   │ └────────────────┘  │
                                   │         │           │
                                   │         ▼           │
                                   │ ┌────────────────┐  │
                                   │ │ SQLite (.db)   │  │
                                   │ │ AuditLog       │  │
                                   │ │ Patients       │  │
                                   │ │ Evaluations    │  │
                                   │ │ Reports        │  │
                                   │ └────────────────┘  │
                                   └─────────┬───────────┘
                                             │
                          ┌──────────────────┼──────────────────┐
                          ▼                  ▼                  ▼
                  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
                  │  AI provider │    │ SMTP (TLS)   │    │ Update OTA   │
                  │  Gemini/Claude│   │  email envio │    │ (HMAC)       │
                  │  (PHI scrub)  │   │              │    │              │
                  └──────────────┘    └──────────────┘    └──────────────┘
```

## 5. Análisis STRIDE

### S — Spoofing (suplantación)

| ID | Amenaza | Vector | Probabilidad | Impacto | Mitigación actual | Pendiente |
|---|---|---|---|---|---|---|
| S1 | Robo de JWT de un usuario | XSS, malware, shoulder-surfing | Media | Alto | JWT con `verify_exp` (S0.6), bcrypt en password, blacklist tokens (S0.x) | Rotación periódica de tokens, alerting por login anómalo |
| S2 | Falsificación de update OTA | MITM de update zip | Baja | Crítico | HMAC-SHA256 con `X-Update-Signature` (S0.1) | Firma digital asimétrica (PGP) cuando se distribuya vía HTTPS real |
| S3 | Suplantación de admin | Login con credencial robada | Media | Crítico | bcrypt + rate limit + audit login_failed | 2FA (TOTP) — Sprint 4 |
| S4 | Token replay | Reutilización de token viejo | Baja | Medio | `jti` único + blacklist + `verify_exp` | Refresh token rotation |

### T — Tampering (alteración)

| ID | Amenaza | Vector | Probabilidad | Impacto | Mitigación actual | Pendiente |
|---|---|---|---|---|---|---|
| T1 | Modificación de BD_NEURO_MAESTRA.json | Acceso filesystem | Baja | Crítico clínico | SHA-256 checksum + `baremo_checksum` column (S0.x) | Notificación al clínico si cambia baremo mid-evaluación |
| T2 | Modificación directa de `neurosoft.db` | Acceso filesystem | Baja | Crítico | Backup firmado antes de escritura | FPE (Format-Preserving Encryption) para columnas PHI — Sprint 4 |
| T3 | Inyección SQL en endpoints | Input malicioso | Baja | Alto | SQLAlchemy ORM (parametrized queries) | — |
| T4 | Modificación de informe PDF firmado | Acceso filesystem | Baja | Alto legal | SHA-256 firma digital en cada PDF | — |
| T5 | Modificación de HMAC update en tránsito | MITM | Muy baja | Crítico | TLS local + HMAC en body | — |

### R — Repudiation (negación)

| ID | Amenaza | Vector | Probabilidad | Impacto | Mitigación actual | Pendiente |
|---|---|---|---|---|--|--|
| R1 | "Yo no exporté ese Habeas Data" | Sin audit | Media | Alto legal | `audit_log` con `actor_id`/`actor_label`/`ip`/`request_id` (S0.3) | — |
| R2 | "Yo no archivé ese paciente" | Sin audit | Baja | Alto | Soft-delete con `archived_by`/`archived_at`/`archived_reason` | — |
| R3 | "Yo no modifiqué ese baremo" | Sin checksum | Baja | Crítico | `baremo_version` + `baremo_checksum` en evaluations | — |

### I — Information Disclosure (fuga de información)

| ID | Amenaza | Vector | Probabilidad | Impacto | Mitigación actual | Pendiente |
|---|---|---|---|---|---|---|
| I1 | PHI a proveedor IA (Gemini/Claude) | Sin sanitización | Media | Crítico legal | `sanitize_clinical_input()` quita doc/fechas/email/teléfono (S0.x) | Redacción también de nombres geográficos |
| I2 | Cross-tenant data leak (prof A ve datos de prof B) | IDOR | Media | Crítico | `get_patient_for_user()` + ownership check (S0.2) | Tests E2E multi-tenant (S0.7 ✅) |
| I3 | Audit log expone PHI | Sin redacción | Baja | Alto | `listeners.py` con VERBATIM/HASH/SKIP policy (S0.3) | — |
| I4 | SECRET_KEY en logs | Debug logs | Baja | Crítico | `core/logging_redactor.py` filtra secrets | — |
| I5 | Backup sin cifrar en disco | Robo de equipo | Baja | Crítico | Backups firmados (S4.3) | AES-256 at rest en `data/` (S4.3) |
| I6 | Stack trace con paths internos | Error 500 | Media | Bajo | Exception handler genérico en producción | — |
| I7 | JWT secret en respuesta | Bug | Baja | Crítico | Test S0.6 verifica que no aparece en responses | — |
| I8 | Habeas Data export expone datos de terceros | Filtro insuficiente | Baja | Alto | Test S0.x verifica aislamiento por paciente | — |

### D — Denial of Service

| ID | Amenaza | Vector | Probabilidad | Impacto | Mitigación actual | Pendiente |
|---|---|---|---|---|---|---|
| D1 | Brute-force login | 1000+ requests/s | Alta | Medio | Rate limit 5/min login + 120/min global (S0.6) | Captcha después de N intentos |
| D2 | Upload de update malicioso gigante | Archivo 1GB | Baja | Medio | Size validation 1024≤body≤200MB (S0.1) | — |
| D3 | Búsqueda con regex DoS | ReDoS en input | Baja | Bajo | Pydantic valida tipos | — |
| D4 | LLM cost overrun | Loop de llamadas IA | Baja | Medio | Timeouts en AI provider, max_tokens limit | Quota per-user |

### E — Elevation of Privilege

| ID | Amenaza | Vector | Probabilidad | Impacto | Mitigación actual | Pendiente |
|---|---|---|---|---|---|---|
| E1 | User normal accede a endpoint admin | RBAC mal configurado | Baja | Crítico | `require_admin` dependency + role check (S0.4) | Tests exhaustivos por rol |
| E2 | Profesional accede a paciente de otro prof | IDOR | Media | Crítico | Ownership check centralizado (S0.2) | Tests E2E ✅ |
| E3 | User inactivo sigue usando token | Token pre-revocación | Baja | Alto | `revoke_all_user_tokens()` con sentinel (S0.x) | — |
| E4 | Path traversal en catalogos | `..` en filename | Baja | Alto | Cargas usan `Path(__file__).resolve()` hardcoded (S0.6) | — |
| E5 | Disable auth via env var | `NEUROSOFT_DISABLE_AUTH=true` | Baja | Crítico | Kill switch ELIMINADO (S0.4) | — |
| E6 | Reset password via env var | `NEUROSOFT_RESET_ADMIN_PASSWORD` | Baja | Crítico | Kill switch ELIMINADO (S0.5) | — |

## 6. Cumplimiento legal colombiano

| Norma | Aplica a | Requisito | Estado |
|---|---|---|---|
| Ley 1581/2012 (Habeas Data) | A1, A2, A3 | Derecho de acceso, rectificación, supresión | ✅ Endpoint `/api/v1/patients/{id}/export` con audit |
| Ley 1090/2006 (Deontología) | Informes PDF | Responsabilidad profesional, firma | ✅ Firma digital SHA-256, plantilla legal |
| Ley 1616/2013 (Salud Mental) | HC | Consentimiento informado | ✅ `consentimiento_firma` field |
| Resolución 1995/1999 | A6 (audit log) | Trazabilidad inmutable | ✅ Audit listener ORM + `actor_id`/`timestamp` |
| ISO 27001 (controles) | General | A.9 (access control), A.10 (cryptography), A.12 (ops security) | Parcialmente conforme (Sprint 0-3 cubren 80%) |

## 7. Riesgos aceptados (con justificación)

| ID | Riesgo | Justificación | Fecha de revisión |
|---|---|---|---|
| RA1 | In-memory rate limit no distribuido | App desktop single-process | Si se distribuye como SaaS multi-instancia |
| RA2 | SQLite en claro en disco local | Cifrado at-rest impacto UX | Sprint 4 (S4.3) |
| RA3 | Sin 2FA | Usuarios son psicólogos, no targets | Sprint 4 (S4.2) |
| RA4 | AI puede alucinar | Marca visible, edición clínica obligatoria | Sprint 2 (S2.5 narrativa) |

## 8. Plan de mitigación priorizado

1. **Inmediato (S0.x)**: S0.1-S0.8 ✅ todos completos.
2. **Corto plazo (Sprint 1)**: cifrado at-rest, PHI en audit log PHI-safe (S0.3 ya), sentinel 9999.
3. **Mediano plazo (Sprints 2-3)**: capa protegida Pearson, scrub IN&S, plantillas documentales, narrative.py, dark mode + A11y.
4. **Largo plazo (Sprint 4)**: 2FA, Sentry, backups AES-256, DRP, 35+ baremos.

## 9. Revisión y aprobación

| Rol | Nombre | Fecha | Firma |
|---|---|---|---|
| Autor | Johan Sebastián Salgado Sarmiento | 2026-06-01 | ✅ |
| Owner del producto | Johan Sebastián Salgado Sarmiento | 2026-06-01 | ✅ |
| Próxima revisión | Trimestral | 2026-09-01 | — |

## 10. Glosario

- **PHI**: Protected Health Information (dato clínico identificable).
- **IDOR**: Insecure Direct Object Reference (acceso por ID sin auth check).
- **HMAC**: Hash-based Message Authentication Code.
- **STRIDE**: metodología Microsoft de modelado de amenazas.
- **DFD**: Data Flow Diagram.
- **OTA**: Over-The-Air update.
- **2FA**: Two-Factor Authentication.
- **JWT**: JSON Web Token.
