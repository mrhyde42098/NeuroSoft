"""
app/presentation/api/router.py
================================
Agregador central de todas las rutas v1.

Las rutas se incluyen agrupadas por bloque funcional para que el
OpenAPI (Swagger /docs) salga ordenado por el flujo clínico:

  🔐  Autenticación
  👥  Pacientes / HC / Consentimientos
  🧪  Evaluación / Scoring / Observaciones / Reactivos / Estímulos
  📊  Reportes / Documentos / RIPS
  🏥  Agenda
  ♻️   Rehabilitación
  🤝  Telemedicina / Compartir
  🧠  Asistente IA
  🛡️   Auditoría / Admin
  🔧  Configuración del sistema
"""
from fastapi import APIRouter

from app.presentation.api.v1.admin_import import admin_router
from app.presentation.api.v1.advanced import advanced_router
from app.presentation.api.v1.ai import ai_router

# ── Agenda ───────────────────────────────────────────────────
from app.presentation.api.v1.appointments import agenda_router

# ── Auditoría / Admin ────────────────────────────────────────
from app.presentation.api.v1.audit import audit_router

# ── Autenticación ─────────────────────────────────────────────
from app.presentation.api.v1.auth import auth_router
from app.presentation.api.v1.clinical_extras import (
    baterias_router,
    dcl_router,
    memoria_router,
    recs_router,
    rips_catalog_router,
    wisc_router,
)
from app.presentation.api.v1.cie11 import cie11_router
from app.presentation.api.v1.clinical_history import (
    backup_router,
    cie10_router,
    config_router,
    docs_router,
    evol_router,
    guide_router,
    hc_router,
)
from app.presentation.api.v1.cups import cups_router
from app.presentation.api.v1.companions import companions_router  # §M-7
from app.presentation.api.v1.reservorio import router as reservorio_router  # Sprint D
from app.presentation.api.v1.consentimientos import consentimientos_router
from app.presentation.api.v1.documents import (
    backup_router_new,
    evol_extra_router,
    rips_router,
)
from app.presentation.api.v1.emails import (
    email_logs_router,
    email_send_router,
    email_tpl_router,
    smtp_config_router,  # §QW-2/3
)
from app.presentation.api.v1.errors import errors_router  # §crash-reports
from app.presentation.api.v1.estimulos import estimulos_router
from app.presentation.api.v1.evaluations import evaluations_router
from app.presentation.api.v1.inconclusos import inconclusos_router

# 🛡️ Licencia (§BLINDAJE-N1)
from app.presentation.api.v1.license import license_router

# ── Pacientes / HC ────────────────────────────────────────────
from app.presentation.api.v1.patients import router as patients_router

# 📚 Referencias bibliográficas (§F2)
from app.presentation.api.v1.referencias import referencias_router

# ── Rehabilitación 🆕 ─────────────────────────────────────────
from app.presentation.api.v1.rehab import rehab_public_router, rehab_router

# ── Reportes / Documentos ────────────────────────────────────
from app.presentation.api.v1.reports import reports_router

# ── Evaluación / Scoring ─────────────────────────────────────
from app.presentation.api.v1.scores import observations_router, scores_router

# ── Telemedicina / IA / Mensajería ───────────────────────────
from app.presentation.api.v1.shared import shared_public_router, shared_router

# ── Psicología Clínica 💚 (módulo expansión — terapia/sesiones SOAP) ──
from app.presentation.api.v1.therapy import therapy_router
from app.presentation.api.v1.update import update_router  # §update-system

api_v1_router = APIRouter(prefix="/api/v1")

# 🔐 Autenticación
api_v1_router.include_router(auth_router)

# 👥 Pacientes / HC / Consentimientos
api_v1_router.include_router(patients_router)
api_v1_router.include_router(hc_router)
api_v1_router.include_router(evol_router)
api_v1_router.include_router(consentimientos_router)
api_v1_router.include_router(guide_router)
api_v1_router.include_router(cie10_router)
api_v1_router.include_router(cie11_router)
api_v1_router.include_router(cups_router)
api_v1_router.include_router(rips_catalog_router)

# 🧪 Evaluación / Scoring / Reactivos / Observaciones / Estímulos
api_v1_router.include_router(scores_router)
api_v1_router.include_router(observations_router)
api_v1_router.include_router(evaluations_router)
api_v1_router.include_router(estimulos_router)
api_v1_router.include_router(advanced_router)
api_v1_router.include_router(inconclusos_router)
api_v1_router.include_router(wisc_router)
api_v1_router.include_router(baterias_router)
api_v1_router.include_router(memoria_router)
api_v1_router.include_router(dcl_router)
api_v1_router.include_router(recs_router)
# ── Baremos / fuentes normativas (Sprint 9) ─────────────────
from app.presentation.api.v1.baremos_info import baremos_info_router

api_v1_router.include_router(baremos_info_router)
# ── KPIs administrativos (Sprint 11) ─────────────────────────
from app.presentation.api.v1.admin_kpis import admin_kpis_router

api_v1_router.include_router(admin_kpis_router)
# ── Retención de HC (Frente 5) ───────────────────────────────
from app.presentation.api.v1.retencion import router as retencion_router

api_v1_router.include_router(retencion_router)
# ── Notificaciones telerehab (Sprint 10) ─────────────────────
from app.presentation.api.v1.notifications import notifications_router

api_v1_router.include_router(notifications_router)

# 🛡️ Licencia (§BLINDAJE-N1)
api_v1_router.include_router(license_router)

# 📚 Referencias bibliográficas (§F2)
api_v1_router.include_router(referencias_router)

# 📊 Reportes / Documentos / RIPS / Backups
api_v1_router.include_router(reports_router)
api_v1_router.include_router(rips_router)
api_v1_router.include_router(docs_router)
api_v1_router.include_router(backup_router)
api_v1_router.include_router(backup_router_new)
api_v1_router.include_router(evol_extra_router)

# 🏥 Agenda
api_v1_router.include_router(agenda_router)

# ♻️ Rehabilitación
api_v1_router.include_router(rehab_router)
api_v1_router.include_router(rehab_public_router)

# 💚 Psicología Clínica (terapia / sesiones SOAP)
api_v1_router.include_router(therapy_router)

# 🤝 Telemedicina / Compartir
api_v1_router.include_router(shared_router)
api_v1_router.include_router(shared_public_router)

# 🧠 Asistente IA
api_v1_router.include_router(ai_router)

# ✉️ Mensajería
api_v1_router.include_router(email_send_router)
api_v1_router.include_router(email_logs_router)
api_v1_router.include_router(smtp_config_router)   # §QW-2 config SMTP
api_v1_router.include_router(email_tpl_router)     # §QW-3 plantillas email
api_v1_router.include_router(companions_router)    # §M-7 acompañantes
api_v1_router.include_router(reservorio_router)   # Banco recomendaciones (Sprint D)

api_v1_router.include_router(audit_router)
api_v1_router.include_router(admin_router)

# 🔧 Configuración del sistema
api_v1_router.include_router(config_router)
api_v1_router.include_router(errors_router)      # §crash-reports
api_v1_router.include_router(update_router)     # §update-system
