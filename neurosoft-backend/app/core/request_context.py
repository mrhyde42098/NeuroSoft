"""
app/core/request_context.py
=============================
ContextVars compartidas para propagar metadata de un request a través
de toda la pila (logs, auditoría, listeners ORM) sin tener que
inyectarlas explícitamente en cada llamada.

Las ContextVars son seguras frente a concurrencia con asyncio: cada
task tiene su propio valor; no se "filtran" entre requests paralelos.

`current_request_id` es seteada por el middleware HTTP `request_id_middleware`
(definido en app/main.py) en cada request, y leída por:
  - El filtro de logging (`PIIRedactor`) para añadir `rid=` a cada línea.
  - El servicio de auditoría (`record_event`) cuando no se le pasó la
    Request explícitamente.
"""

from __future__ import annotations

from contextvars import ContextVar

# ID único por request (UUID4 hex, o el valor del header `X-Request-ID`
# enviado por el cliente). String vacío "" si todavía no fue inicializado.
current_request_id: ContextVar[str] = ContextVar(
    "neurosoft_request_id",
    default="",
)
