# Plan de Recuperación ante Desastres (DRP)

NeuroSoft App — Plan de continuidad de negocio para datos clínicos.

> **Última revisión:** junio 2026 (Sprint 4).
> **Versión del sistema:** 2.0.0
> **Software propiedad de:** Johan Sebastián Salgado Sarmiento.

---

## 1. Alcance

Este documento cubre la recuperación ante desastres de **datos clínicos**
generados por NeuroSoft App en consultorios pequeños (2-5 psicólogos)
en Colombia. NO cubre:

- Infraestructura de red (es desktop-first, offline).
- Servicios externos opcionales (Gemini, Claude, OpenAI, Ollama remoto).
- Hardware del equipo del clínico (asumimos que el operador tiene sus
  propios procedimientos de backup de disco).

---

## 2. Objetivos de recuperación

| Métrica | Objetivo | Justificación |
|---|---|---|
| **RTO** (Recovery Time Objective) | ≤ 4 horas | Tiempo tolerable para que el consultorio reanude operaciones clínicas. |
| **RPO** (Recovery Point Objective) | ≤ 24 horas | Pérdida máxima tolerable: los datos del día anterior. Justificado por backup diario 02:00. |
| **MTTR** (Mean Time To Repair) | ≤ 2 horas | Tiempo esperado para que un operador técnico restaure desde un backup cifrado. |

---

## 3. Datos críticos a proteger

| Dato | Ubicación | Criticidad | Backup |
|---|---|---|---|
| Base de datos SQLite (pacientes, evaluaciones, HC) | `data/neurosoft.db` | CRÍTICA | Diario cifrado AES-256 |
| Baremos normativos | `data/BD_NEURO_MAESTRA.json` | ALTA (no cambia) | Backup Git + copia en instalador |
| PDFs generados | `data/reports/` o carpeta del usuario | ALTA | Derivado de la BD; regenerable |
| Configuración SMTP | Tabla `config_smtp` (cifrada) | MEDIA | Incluida en backup de BD |
| Plantillas email | Tabla `config_email_templates` | BAJA | Incluida en backup de BD |
| Tokens de sesión JWT | Tabla `tokens` (cifrada) | BAJA | Se invalidan al cambiar SECRET_KEY |
| Logs de auditoría | Tabla `audit_logs` | CRÍTICA (Res 1995) | Incluida en backup de BD |
| `data/last_update.json` | `data/last_update.json` | BAJA | Hash para validación de updates |

---

## 4. Procedimiento de backup

### 4.1 Automático (S4.3)

- **Cuándo**: diario a las 02:00 hora Colombia.
- **Cómo**: APScheduler job `backup_automatico` en `scheduler_service.py`.
- **Cifrado**: Fernet (AES-128-CBC + HMAC-SHA256) derivado del SECRET_KEY.
- **Compresión**: gzip nivel 6.
- **Ubicación**: `data/backups/ns-backup-YYYYMMDD-HHMMSS-ffffff.enc.gz`.
- **Retención**:
  - 7 backups diarios más recientes
  - 4 backups semanales (anteriores a 7 días)
- **Verificación de integridad**: SHA-256 dentro del header del backup.

### 4.2 Manual (CLI)

```bash
# Crear backup inmediato
python -m scripts.backup_cli crear --notas "Antes de migración 007"

# Listar backups disponibles
python -m scripts.backup_cli listar

# Restaurar a una ruta específica (no sobrescribe la BD activa)
python -m scripts.backup_cli restaurar data/backups/ns-backup-XYZ.enc.gz \
    --target /tmp/neurosoft_test.db

# Forzar rotación
python -m scripts.backup_cli rotar --diarios 7 --semanales 4
```

### 4.3 Desde código

```python
from pathlib import Path
from app.infrastructure.backup import (
    crear_backup, restaurar_backup, listar_backups,
)

# Crear
ruta = crear_backup(notas="Antes de cambiar SECRET_KEY")

# Listar
for b in listar_backups():
    print(b.timestamp, b.ruta, b.tamano_bytes)

# Restaurar a la BD activa
restaurar_backup(ruta)

# Restaurar a un target custom
restaurar_backup(ruta, target_path=Path("data/neurosoft_recovered.db"))
```

---

## 5. Procedimiento de recuperación

### 5.1 Escenario A: corrupción menor (un solo registro, una tabla)

1. **Detectar**: el clínico reporta inconsistencia.
2. **Aislar**: NO restaurar backup completo. Usar el endpoint
   `GET /api/v1/audit?entity_id=<paciente_id>` para ver qué cambió.
3. **Reparar**: usar SQL directo sobre `data/neurosoft.db` con la BD
   respaldada en `data/neurosoft.db.pre-restore-*.bak`.
4. **Verificar**: re-correr el caso clínico contra el motor y comparar
   con snapshot ground truth si está disponible.
5. **Documentar**: el incidente queda en `audit_logs` automáticamente.

### 5.2 Escenario B: corrupción mayor (BD ilegible o eliminada)

1. **Identificar** último backup válido:
   ```bash
   python -m scripts.backup_cli listar
   ```
2. **Verificar integridad** del backup elegido (ver §6).
3. **Restaurar**:
   ```bash
   python -m scripts.backup_cli restaurar data/backups/ns-backup-XYZ.enc.gz
   ```
   - El script crea automáticamente `data/neurosoft.db.pre-restore-YYYYMMDD-HHMMSS.bak`
     con el contenido anterior (si existía).
4. **Reiniciar** la aplicación.
5. **Smoke test**: login admin + abrir un paciente reciente + verificar
   que las evaluaciones se ven.
6. **Notificar al usuario** qué datos se perdieron (los posteriores al
   último backup).

### 5.3 Escenario C: pérdida total de la máquina (disco duro muerto)

1. **Reinstalar** NeuroSoft App en máquina nueva desde
   `NeuroSoft-Setup.exe`.
2. **NO iniciar** la aplicación todavía.
3. **Copiar** los archivos `.enc.gz` desde el backup externo a
   `data/backups/`.
4. **CRÍTICO**: configurar `NEUROSOFT_SECRET_KEY` en `.env` con el
   **mismo valor** que tenía la máquina anterior. Sin esto, los backups
   no se pueden descifrar.
5. Iniciar la aplicación y seguir Escenario B desde el paso 2.

---

## 6. Verificación de integridad de un backup

### 6.1 Automática

Cada backup lleva en su header un SHA-256 del contenido original.
Al listar o restaurar, el sistema valida y rechaza backups corruptos.

### 6.2 Manual

```python
import gzip, json
from app.infrastructure.backup import _descifrar_y_verificar

with gzip.open("data/backups/ns-backup-XYZ.enc.gz", "rb") as f:
    payload = f.read()
plain, header = _descifrar_y_verificar(payload)
print("SHA-256:", header["sha256"])
print("Tamaño:", len(plain), "bytes")
print("Metadata:", header["metadata"])
```

### 6.3 Programada (recomendado)

Job semanal `backup_integrity_check` (scheduler) que abre los últimos 5
backups y corre `PRAGMA integrity_check` de SQLite sobre cada uno.

---

## 7. Almacenamiento externo

**Recomendación** para producción:

1. **Backup local** (ya implementado): `data/backups/` dentro del
   directorio de datos del usuario.
2. **Backup externo semanal** (responsabilidad del operador): copiar
   los `.enc.gz` a un disco externo / nube cifrada. **Nunca** subir
   sin cifrar a servicios de terceros.
3. **Política 3-2-1**:
   - 3 copias del dato (BD activa + backup local + backup externo).
   - 2 medios diferentes (SSD local + disco externo / nube).
   - 1 copia off-site (backup externo fuera del consultorio).

---

## 8. Clasificación de incidentes

| Severidad | Descripción | RTO | Acción |
|---|---|---|---|
| **Crítico** | Pérdida total de BD; consultorio inoperante | ≤ 4h | Escenario C inmediato |
| **Alto** | Corrupción mayor; datos parcialmente recuperables | ≤ 24h | Escenario B + soporte remoto |
| **Medio** | Datos corruptos pero identificables; pérdida <24h | ≤ 72h | Escenario A + audit |
| **Bajo** | Inconsistencia menor sin impacto clínico | ≤ 1 semana | Documentar en audit log |

---

## 9. Bitácora de pruebas DRP

| Fecha | Escenario | Resultado | Operador |
|---|---|---|---|
| (pendiente) | A: paciente_test corrupt | — | — |
| (pendiente) | B: restaurar backup cifrado | — | — |
| (pendiente) | C: pérdida total simulada | — | — |

Se recomienda ejecutar un drill de Escenario B al menos 1 vez por trimestre.

---

## 10. Limitaciones conocidas

- **Sin replicación geográfica automática.** El operador debe copiar los
  `.enc.gz` a un medio externo manualmente (o vía cron + rclone).
- **Si se pierde el SECRET_KEY, los backups son irrecuperables.**
  Guardar el SECRET_KEY en lugar seguro FUERA de la BD
  (recomendación: variable de entorno del sistema o gestor de secretos
  del SO).
- **WAL no sincronizado.** Si la aplicación se cierra abruptamente
  (kill -9) durante un write, los últimos milisegundos podrían no estar
  en el backup. SQLite WAL generalmente recupera, pero el script de
  backup hace `PRAGMA wal_checkpoint(FULL)` para minimizar la ventana.
- **Backups encriptados con SECRET_KEY = 1 sola clave.** Rotación de
  clave requiere re-cifrar todos los backups. (Mejora futura: KMS.)

---

## 11. Contacto de emergencia

- **Autor / propietario**: Johan Sebastián Salgado Sarmiento
- **Email**: jssalgadosa@unal.edu.co
- **Documentación**: `docs/ARQUITECTURA.md`, `docs/seguridad/MODELO_AMENAZAS.md`
