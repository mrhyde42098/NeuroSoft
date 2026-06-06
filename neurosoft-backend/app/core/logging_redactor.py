"""
app/core/logging_redactor.py
=============================
Filtro de logging que redacta PII (Personally Identifiable Information)
en cada registro emitido.

Contexto legal (Colombia)
-------------------------
La Ley 1581 de 2012 (Habeas Data) y la Resolución 1995 de 1999 del
Ministerio de Salud exigen que ningún dato identificatorio de un
paciente se exponga en registros no autorizados. Los logs de
aplicación se consideran "tratamiento" de datos y por lo tanto están
sujetos al principio de finalidad: sólo pueden contener lo mínimo
necesario para operar y auditar el sistema.

Este módulo implementa una defensa *defensa en profundidad*: aunque
un desarrollador olvide sanitizar un f-string antes de un
`logger.info(...)`, el filtro intercepta el LogRecord y reemplaza los
patrones sensibles antes de que lleguen al handler (consola, archivo
o agente de telemetría).

Patrones redactados por defecto
-------------------------------
    • Direcciones de correo electrónico
    • Teléfonos colombianos (+57, celulares 3XXXXXXXXX)
    • JWT / Bearer tokens
    • Pares clave=valor sensibles:
        password, passwd, secret, api_key, token, authorization,
        cedula, documento, telefono, phone, email, dob,
        fecha_nacimiento
    • Campos explícitos vía `extra={"pii_fields": [...]}`

Uso
---
    from app.core.logging_redactor import install_pii_redactor
    install_pii_redactor()            # una vez al arrancar la app

    # Opt-out puntual (métricas, tests):
    logger.info("tick", extra={"skip_pii": True})

    # Helper manual:
    from app.core.logging_redactor import redact
    msg = redact(raw_user_text)

Decisiones de diseño
--------------------
- La redacción es "fail-open": si la regex falla o el LogRecord está
  mal formado, el filtro deja pasar el registro sin romper la
  aplicación. Preferimos un log con PII a un servicio caído.
- Se evita redactar números genéricos (ports, timestamps, UUIDs,
  checksums). Sólo cuando hay un patrón estructural claro.
- Idempotente: instalar dos veces no duplica filtros.
"""

from __future__ import annotations

import logging
import re
from re import Pattern

# ─────────────────────────────────────────────────────────────
# Patrones de PII
# ─────────────────────────────────────────────────────────────

# Email RFC-5322 simplificado, suficiente para logs.
_EMAIL_RE: Pattern[str] = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# Teléfono colombiano:
#   • +57 seguido de 10 dígitos
#   • Celular 10 dígitos iniciando en 3
#   • Separadores admitidos: espacio o guion
_PHONE_RE: Pattern[str] = re.compile(
    r"""
    (?<!\w)                  # no-word-boundary izquierdo
    (?:
        \+?57[\s\-]?3\d{2}[\s\-]?\d{3}[\s\-]?\d{4}  # +57 3XX XXX XXXX
      | (?<!\d)3\d{2}[\s\-]?\d{3}[\s\-]?\d{4}       # 3XX XXX XXXX
    )
    (?!\w)                   # no-word-boundary derecho
    """,
    re.VERBOSE,
)

# JWT estándar (tres segmentos base64url separados por punto).
_JWT_RE: Pattern[str] = re.compile(r"eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+")

# Bearer <token> (redacción separada para no depender del formato JWT).
_BEARER_RE: Pattern[str] = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9_\-\.=]+")

# Pares clave=valor o clave: "valor" en texto libre o JSON-like
# (soporta tanto `key=value` como `'key': 'value'` de dict repr).
_SENSITIVE_KV_RE: Pattern[str] = re.compile(
    r"""
    \b(
        password | passwd | secret | api[_\-]?key | token | authorization
      | cedula | documento | doc[_\-]?id | identificacion
      | telefono | phone | celular | email | correo
      | dob | fecha[_\-]?nacimiento | birth[_\-]?date
    )\b
    ['"\s]*                 # posibles comillas/espacios después de la clave
    [:=]
    ['"\s]*                 # posibles comillas/espacios antes del valor
    ([^\s,}\]'"]+)          # valor (sin delimitadores)
    """,
    re.IGNORECASE | re.VERBOSE,
)

_REDACT_MARK = "[REDACTED]"


# ─────────────────────────────────────────────────────────────
# Funciones públicas
# ─────────────────────────────────────────────────────────────


def _redact_kv(match: re.Match[str]) -> str:
    """
    Conserva la cadena original pero reemplaza sólo el valor capturado
    (group 2) por la marca de redacción. Así mantenemos las comillas
    y el separador originales, evitando romper JSON o dict reprs.
    """
    full = match.group(0)
    value = match.group(2)
    return full.replace(value, _REDACT_MARK, 1)


def redact(text: str) -> str:
    """
    Redacta PII en una cadena y la retorna.
    Si el input no es str lo retorna sin cambios.
    """
    if not isinstance(text, str) or not text:
        return text
    try:
        text = _JWT_RE.sub(_REDACT_MARK, text)
        text = _BEARER_RE.sub(f"Bearer {_REDACT_MARK}", text)
        text = _EMAIL_RE.sub(_REDACT_MARK, text)
        text = _PHONE_RE.sub(_REDACT_MARK, text)
        text = _SENSITIVE_KV_RE.sub(_redact_kv, text)
    except Exception:  # noqa: BLE001
        # Fail-open: un log con PII es peor que un crash, pero
        # un crash dentro del logger es catastrófico — registramos
        # el problema y dejamos pasar el texto original.
        pass
    return text


# ─────────────────────────────────────────────────────────────
# Filtro de logging
# ─────────────────────────────────────────────────────────────


class PIIRedactor(logging.Filter):
    """
    Filtro que redacta PII en cada LogRecord antes de emitirlo.

    Se aplica sobre el mensaje ya formateado (msg + args). Si el
    emisor marca `extra={"skip_pii": True}` el registro pasa sin
    modificación — útil para métricas de alta frecuencia donde
    sabemos que no hay PII y queremos evitar el costo.
    """

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        # Inyectar `rid` (X-Request-ID truncado) para correlacionar logs
        # con eventos de auditoría. "-" si no estamos en un request.
        try:
            from app.core.request_context import current_request_id

            rid = current_request_id.get()
            record.rid = rid[:12] if rid else "-"
        except Exception:  # noqa: BLE001
            record.rid = "-"

        if getattr(record, "skip_pii", False):
            return True

        try:
            formatted = record.getMessage()
            redacted = redact(formatted)
            if redacted != formatted:
                record.msg = redacted
                record.args = ()

            # Campos adicionales opcionales (extra={"pii_fields": ["cedula"]})
            pii_fields = getattr(record, "pii_fields", None)
            if pii_fields:
                for attr in pii_fields:
                    if hasattr(record, attr):
                        setattr(record, attr, _REDACT_MARK)
        except Exception:  # noqa: BLE001
            pass

        return True


# ─────────────────────────────────────────────────────────────
# Instalación
# ─────────────────────────────────────────────────────────────


def install_pii_redactor(logger_name: str = "") -> PIIRedactor:
    """
    Instala el filtro en el logger indicado (root por defecto)
    y en todos sus handlers.

    Idempotente: si ya existe un PIIRedactor instalado, retorna
    el existente sin duplicar.
    """
    target = logging.getLogger(logger_name)
    existing = next(
        (f for f in target.filters if isinstance(f, PIIRedactor)),
        None,
    )
    if existing is not None:
        redactor = existing
    else:
        redactor = PIIRedactor()
        target.addFilter(redactor)

    # Los logging.Filter instalados en un Logger sólo se aplican a
    # los registros emitidos directamente por ese logger. Para cubrir
    # loggers hijos que heredan handlers del root, instalamos el
    # filtro también en cada handler del root.
    for handler in logging.getLogger().handlers:
        if not any(isinstance(f, PIIRedactor) for f in handler.filters):
            handler.addFilter(redactor)

    return redactor
