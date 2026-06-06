"""
Mantenimiento de estímulos en datos de usuario.
Los recortes masivos de PDFs de capacitación no deben bloquear el arranque.
"""
from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy import or_

logger = logging.getLogger(__name__)


def _pdf_capacitacion_sql_filters():
    from app.infrastructure.database.orm_models import EstimuloORM

    return or_(
        EstimuloORM.test_id.contains("Stim_p"),
        EstimuloORM.test_id.startswith("NiWiscStim"),
        EstimuloORM.test_id.startswith("AdStim"),
        EstimuloORM.test_id.startswith("EstímuloStim"),
    )


def deactivate_pdf_capacitacion_stimuli(db) -> int:
    """Desactiva recortes PDF sin cargar contenido_base64 (evita colgar el .exe)."""
    from app.infrastructure.database.orm_models import EstimuloORM

    filt = _pdf_capacitacion_sql_filters()
    n = (
        db.query(EstimuloORM)
        .filter(EstimuloORM.activo.is_(True))
        .filter(filt)
        .update({EstimuloORM.activo: False}, synchronize_session=False)
    )
    if n:
        db.commit()
        logger.info("Estímulos: desactivados %d recortes PDF", n)
    return n


def bootstrap_stimuli(user_data_dir: Path, db) -> None:
    try:
        deactivate_pdf_capacitacion_stimuli(db)
    except Exception as e:
        logger.warning("Bootstrap estímulos falló: %s", e)
        try:
            db.rollback()
        except Exception:
            pass
