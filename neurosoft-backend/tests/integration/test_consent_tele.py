"""Consentimiento telepsicología obligatorio cuando aplica."""

from __future__ import annotations

import uuid
from datetime import date

import pytest


@pytest.mark.integration
def test_pendientes_incluye_tele_si_via_atencion(in_memory_db):
    from app.infrastructure.database.orm_models import PatientORM
    from app.presentation.api.v1.consentimientos import pendientes_paciente

    p = PatientORM(
        id=str(uuid.uuid4()),
        numero_documento=f"TEL{uuid.uuid4().hex[:6]}",
        tipo_documento="CC",
        primer_nombre="Tel",
        primer_apellido="Test",
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        escolaridad="Universitaria",
        lateralidad="Diestro",
        fecha_atencion=date.today(),
        via_atencion="telepsicologia",
        is_active=True,
    )
    in_memory_db.add(p)
    in_memory_db.commit()

    dto = pendientes_paciente(p.id, in_memory_db)
    assert "telepsicologia" in dto.pendientes
