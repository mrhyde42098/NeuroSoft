"""
tests/unit/audit/test_monitor.py
=================================
Tests del monitor continuo del audit log.
"""
from __future__ import annotations

import json
import uuid
from datetime import UTC, date, datetime, timedelta

import pytest


def _make_patient(db, doc="MON001"):
    from app.infrastructure.database.orm_models import PatientORM
    orm = PatientORM(
        id=str(uuid.uuid4()),
        numero_documento=doc,
        tipo_documento="CC",
        primer_nombre="Monitor",
        primer_apellido="Test",
        fecha_nacimiento=date(2010, 1, 1),
        sexo="H",
        escolaridad="Primaria",
        fecha_atencion=date.today(),
        is_active=True,
        created_at=datetime.now(UTC),
    )
    db.add(orm)
    db.flush()
    return orm


def _make_eval_with_outlier(db, patient_id):
    """Crea una evaluación con un PD fuera del baremo."""
    from app.infrastructure.database.orm_models import EvaluationORM
    ev = EvaluationORM(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        protocolo="Test",
        fecha=date.today(),
        puntajes_brutos_json='{"NiWiscDC": 999}',
        resultados_json=json.dumps([{
            "test_id": "NiWiscDC",
            "test_nombre": "Test",
            "puntaje_bruto": 999,
            "puntaje_escalar": None,
            "tipo_metrica": "escalar",
            "interpretacion": "Sin baremo",
            "dominio_cognitivo": "Test",
            "metadata": {"out_of_baremo": True, "error": "PD=999 fuera del rango del baremo"},
        }]),
        poblacion="infantil",
        edad_display="10a",
        pruebas_realizadas=1,
        pruebas_sin_dato=0,
        is_latest=True,
        created_at=datetime.now(UTC),
    )
    db.add(ev)
    db.flush()
    return ev


def _make_stale_eval(db, patient_id, days_old=10):
    from app.infrastructure.database.orm_models import EvaluationORM
    ev = EvaluationORM(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        protocolo="Test",
        fecha=date.today() - timedelta(days=days_old),
        puntajes_brutos_json='{}',
        resultados_json='[]',
        poblacion="infantil",
        edad_display="10a",
        pruebas_realizadas=0,
        pruebas_sin_dato=0,
        is_latest=True,
        created_at=datetime.now(UTC) - timedelta(days=days_old),
    )
    db.add(ev)
    db.flush()
    return ev


@pytest.mark.unit
class TestAuditMonitor:
    def test_monitor_se_inicializa_sin_alertas(self):
        from app.infrastructure.audit.monitor import AuditMonitor
        m = AuditMonitor()
        assert m.alerts == []

    def test_check_baremo_outliers_detecta(self, in_memory_db):
        from app.infrastructure.audit.monitor import AuditMonitor
        p = _make_patient(in_memory_db, "MOUT01")
        _make_eval_with_outlier(in_memory_db, p.id)
        in_memory_db.commit()
        m = AuditMonitor(db_session=in_memory_db)
        result = m.check_baremo_outliers()
        assert result["n_outliers"] == 1
        assert len(m.alerts) == 1
        assert m.alerts[0]["type"] == "BARE_OUTLIER"

    def test_check_stale_evaluations_detecta(self, in_memory_db):
        from app.infrastructure.audit.monitor import AuditMonitor
        p = _make_patient(in_memory_db, "MST01")
        _make_stale_eval(in_memory_db, p.id, days_old=15)
        in_memory_db.commit()
        m = AuditMonitor(db_session=in_memory_db)
        result = m.check_stale_evaluations()
        assert result["n_stale"] == 1
        assert any(a["type"] == "STALE_EVAL" for a in m.alerts)

    def test_check_audit_log_volume_normal(self, in_memory_db):
        from app.infrastructure.audit.monitor import AuditMonitor
        m = AuditMonitor(db_session=in_memory_db)
        result = m.check_audit_log_volume()
        assert "events_last_24h" in result
        # Si no hay muchos eventos, no debe alertar
        assert not any(a["type"] == "AUDIT_VOLUME" for a in m.alerts)

    def test_run_all_checks_retorna_reporte_completo(self, in_memory_db):
        from app.infrastructure.audit.monitor import AuditMonitor
        p = _make_patient(in_memory_db, "MRUN01")
        _make_eval_with_outlier(in_memory_db, p.id)
        in_memory_db.commit()
        m = AuditMonitor(db_session=in_memory_db)
        report = m.run_all_checks()
        assert "timestamp" in report
        assert "checks" in report
        assert "alerts" in report
        assert "summary" in report
        # Debe haber al menos 1 alerta (outlier)
        assert report["summary"]["total_alerts"] >= 1

    def test_summary_por_severidad(self):
        from app.infrastructure.audit.monitor import AuditMonitor
        m = AuditMonitor()
        m._add_alert("HIGH", "TEST", "msg1")
        m._add_alert("HIGH", "TEST", "msg2")
        m._add_alert("LOW", "TEST", "msg3")
        summary = m._summary()
        assert summary["total_alerts"] == 3
        assert summary["by_severity"]["HIGH"] == 2
        assert summary["by_severity"]["LOW"] == 1
