"""
app/infrastructure/audit/listeners.py
======================================
Listeners SQLAlchemy que registran automáticamente cambios
sobre entidades clínicas críticas en la tabla audit_log.

Se activan con `register_audit_listeners()` una sola vez al
arrancar la aplicación (ver app.main).

El actor se obtiene de un ContextVar que la capa HTTP
(middleware) rellena con el usuario autenticado. Si no hay
contexto, el actor queda como 'system'.

§S0.3 del PLAN_MAESTRO — Política PHI:

  - VERBATIM: campos no-PHI (metadatos, IDs, booleanos, fechas) se
    registran tal cual para análisis forense.
  - HASH:    datos personales o clínicos se reemplazan por SHA-256
    (prefijo de 12 chars). Permite verificar que cambió, sin
    filtrar PHI al log.
  - SKIP:    blobs binarios (firmas, fotos, contenido de informes) y
    secretos (hashed_password) jamás se registran.

Esta política reduce drásticamente la superficie de exposición
de PHI en `audit_log.changes` y `audit_log.summary`, manteniendo
la trazabilidad clínica exigida por la Resolución 1995/1999.
"""

from __future__ import annotations

import hashlib
import json
import logging

logger = logging.getLogger(__name__)
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.infrastructure.database.orm_models import (
    AuditLogORM,
    ClinicalHistoryORM,
    ConsentimientoORM,
    EvaluationORM,
    EvolTerapiaORM,
    InformeInconclusoORM,
    PatientORM,
)

_log = logging.getLogger("neurosoft.audit.listeners")

# Entidades bajo auditoría automática
_WATCHED = {
    PatientORM:            ("patient",          "Paciente"),
    ClinicalHistoryORM:    ("clinical_history", "Historia Clínica"),
    EvaluationORM:         ("evaluation",       "Evaluación"),
    EvolTerapiaORM:        ("evolucion",        "Evolución"),
    ConsentimientoORM:     ("consentimiento",   "Consentimiento"),
    InformeInconclusoORM:  ("inconcluso",       "Informe Inconcluso"),
}

# Contexto de actor rellenado por la capa HTTP (ver auth middleware)
current_actor_id:    ContextVar[str | None] = ContextVar("ns_actor_id", default=None)
current_actor_label: ContextVar[str | None] = ContextVar("ns_actor_label", default=None)
current_ip:          ContextVar[str | None] = ContextVar("ns_actor_ip", default=None)


# ═══════════════════════════════════════════════════════════════
# §S0.3 — Política PHI: whitelist verbatim + hash fallback + skip
# ═══════════════════════════════════════════════════════════════

# Campos VERBATIM (no-PHI): metadatos, IDs, flags, fechas, codigos
_VERBATIM_FIELDS: frozenset[str] = frozenset({
    # Identificadores y FKs
    "id", "patient_id", "hc_id", "session_id", "user_id",
    "profesional_id", "evaluacion_id", "companion_id",
    "riesgo_id", "informe_id", "owner_id", "created_by",
    # Banderas / booleanos
    "is_active", "is_latest", "donante", "activo", "incapacidad",
    "pruebas_realizadas", "pruebas_sin_dato", "numero_sesiones",
    "row_version", "orden",
    # Catalogos y codigos
    "codigo_rips", "cups", "sexo", "lateralidad", "escolaridad",
    "tipo_documento", "finalidad_consulta", "protocolo",
    "estado", "estado_civil", "estrato", "localidad", "grupo_etnico",
    "lugar_nacimiento", "tipo_parto", "sosten_cefalico", "sedestacion",
    "gateo", "marcha", "balbuceo", "primeras_palabras", "habla_claro",
    "control_anual", "control_vesical", "incubadora", "ucin",
    "gestacion", "semanas", "peso_gr", "talla_cm", "no_gestacion",
    "riesgos", "edad_materna", "tipo", "nivel", "escala", "motivo_id",
    "version", "tamano", "tamano_bytes", "filename", "extension",
    "sha256",
    # Timestamps (no son PHI clinico)
    "created_at", "updated_at", "signed_at", "fecha_atencion",
    "fecha_nacimiento", "saved_at", "ts", "applied_at", "expires_at",
    "archived_at", "archived_by", "archived_reason",
    # Calculos clinicos (los escalares / CIs son parte del producto
    # clínico pero no son PHI identificable por si solos).
    "ci", "pd", "pd_ajustado", "escalar", "percentil", "z_score",
    "suma_escalares", "rango", "interpretacion",
    # Catalogos psicometricos
    "nombre", "titulo", "especialidad", "registro_profesional",
    "ciudad", "sitio_web", "direccion_oficina",
})

# Campos SKIP: blobs binarios, secretos. Nunca al audit log.
_SKIP_FIELDS: frozenset[str] = frozenset({
    "firma_base64", "sello_base64", "foto_base64",
    "contenido_base64", "firma", "firma_digital",
    "hashed_password", "password", "password_hash",
    "pdf_base64", "documento_base64",
    "tokens", "refresh_token", "access_token",
})


def _hash_phi(value: Any) -> str:
    """
    Devuelve un identificador estable y no-reversible del valor.

    Usado para probar que un campo cambió, sin filtrar el PHI al
    log. Si el valor es None, devuelve '__null__'.
    """
    if value is None:
        return "__null__"
    if isinstance(value, bool):
        v = "true" if value else "false"
    elif isinstance(value, (int, float)):
        v = str(value)
    elif hasattr(value, "isoformat"):
        v = value.isoformat()
    else:
        v = str(value)
    digest = hashlib.sha256(v.encode("utf-8", errors="replace")).hexdigest()
    return f"sha256:{digest[:12]}"


def _classify(field: str) -> str:
    """Devuelve 'verbatim' | 'hash' | 'skip' para un campo."""
    if field in _SKIP_FIELDS or field.endswith("_base64") or field.endswith("_token"):
        return "skip"
    if field in _VERBATIM_FIELDS:
        return "verbatim"
    # Default conservador: HASH (no exponer PHI por accidente)
    return "hash"


def _safe_value(field: str, value: Any) -> Any:
    """
    Devuelve una representacion segura del valor para el audit log,
    respetando la politica PHI.
    """
    policy = _classify(field)
    if policy == "skip":
        return None
    if policy == "hash":
        return _hash_phi(value)
    # verbatim: normalizar tipos
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        # Truncar strings muy largos para no inflar el log
        if isinstance(value, str):
            return value[:300]
        return value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)[:120]


def _snapshot(obj: Any) -> dict:
    """
    Devuelve dict de columnas del ORM respetando la política PHI.
    Aplica SKIP (omite), VERBATIM (valor crudo) y HASH (sha256[:12]).
    """
    try:
        cols = {c.name for c in obj.__table__.columns}
        out = {}
        for c in cols:
            if _classify(c) == "skip":
                continue
            v = getattr(obj, c, None)
            out[c] = _safe_value(c, v)
        return out
    except Exception as _exc:
        logger.debug("Error serializando valor de auditoría: %s", _exc)
        return {}


def _diff(before: dict, after: dict) -> dict:
    """Campos que cambiaron entre dos snapshots."""
    changed = {}
    for k in set(before) | set(after):
        if before.get(k) != after.get(k):
            changed[k] = [before.get(k), after.get(k)]
    return changed


def _label(obj: Any) -> str:
    """
    Etiqueta humana NO-PHI del objeto auditado.

    Antes filtraba nombres completos ("Andres Felipe Romero") al
    `summary` del audit log. Ahora usa solo el id corto + un hash
    opcional del nombre para correlacionar sin filtrar PHI.
    """
    if isinstance(obj, PatientORM):
        # No usar nombres — solo id corto
        pid = getattr(obj, "id", "") or ""
        return f"id={pid[:8]}"
    if isinstance(obj, EvaluationORM):
        eid = getattr(obj, "id", "") or ""
        return f"Evaluación {eid[:8]}"
    if isinstance(obj, ClinicalHistoryORM):
        pid = getattr(obj, "patient_id", "") or ""
        return f"HC paciente {pid[:8]}"
    if isinstance(obj, EvolTerapiaORM):
        eid = getattr(obj, "id", "") or ""
        return f"Evolución {eid[:8]}"
    if isinstance(obj, ConsentimientoORM):
        # `tipo` es catalog, no PHI
        return f"Consentimiento {getattr(obj, 'tipo', '')}"
    if isinstance(obj, InformeInconclusoORM):
        return f"Inconcluso {getattr(obj, 'motivo_id', '')}"
    return ""


def _queue_audit(session: Session, action: str, obj: Any, changes: dict | None = None):
    """Guarda un audit_log usando la misma sesión para sumarse al commit."""
    info = _WATCHED.get(type(obj))
    if not info:
        return
    entity_type, human = info
    entity_id = getattr(obj, "id", None)
    summary = f"{action.upper()} {human}: {_label(obj)}"
    entry = AuditLogORM(
        ts=datetime.now(UTC),
        actor_id=current_actor_id.get() or "system",
        actor_label=(current_actor_label.get() or "")[:120] or None,
        action=action,
        entity_type=entity_type,
        entity_id=(str(entity_id)[:36] if entity_id else None),
        summary=summary[:300],
        changes=(json.dumps(changes, default=str, ensure_ascii=False)[:20000]
                 if changes else None),
        ip=current_ip.get(),
    )
    session.add(entry)


def register_audit_listeners() -> None:
    """Registra los listeners contra el Session de SQLAlchemy.

    Idempotente: si ya estan registrados, no hace nada. Esto es importante
    para los tests que invocan esta funcion desde cada fixture sin
    acumular multiples listeners que disparen el audit N veces.
    """
    global _LISTENERS_REGISTERED
    if _LISTENERS_REGISTERED:
        return

    @event.listens_for(Session, "before_flush")
    def _before_flush(session: Session, flush_context, instances):  # noqa: ARG001
        # NUEVOS
        for obj in list(session.new):
            if type(obj) in _WATCHED:
                try:
                    _queue_audit(session, "create", obj, _snapshot(obj))
                except Exception as e:
                    _log.warning("audit create failed: %s", e)

        # MODIFICADOS — para cada columna modificada, clasificamos
        # con la politica PHI antes de registrar el diff.
        for obj in list(session.dirty):
            if type(obj) not in _WATCHED:
                continue
            try:
                hist = {}
                for attr in obj.__table__.columns:
                    col = attr.name
                    if _classify(col) == "skip":
                        continue
                    from sqlalchemy.orm.attributes import get_history
                    h = get_history(obj, col)
                    if h.has_changes():
                        old = h.deleted[0] if h.deleted else None
                        new = h.added[0] if h.added else getattr(obj, col, None)
                        # Aplicar política PHI también a los valores del diff
                        old_safe = _safe_value(col, old)
                        new_safe = _safe_value(col, new)
                        hist[col] = [old_safe, new_safe]
                if hist:
                    _queue_audit(session, "update", obj, hist)
            except Exception as e:
                _log.warning("audit update failed: %s", e)

        # ELIMINADOS
        for obj in list(session.deleted):
            if type(obj) in _WATCHED:
                try:
                    _queue_audit(session, "delete", obj, _snapshot(obj))
                except Exception as e:
                    _log.warning("audit delete failed: %s", e)

    _log.info("NeuroSoft audit listeners registrados (politica PHI v2)")
    _LISTENERS_REGISTERED = True


_LISTENERS_REGISTERED = False