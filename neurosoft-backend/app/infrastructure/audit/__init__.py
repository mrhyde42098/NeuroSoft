"""Módulo de auditoría — Resolución 1995 de 1999."""
from .audit_service import audit_action, record_event  # noqa: F401
from .listeners import (  # noqa: F401
    current_actor_id,
    current_actor_label,
    current_ip,
    register_audit_listeners,
)
