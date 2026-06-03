"""
app/infrastructure/audit/monitor.py
====================================
Monitor continuo del Audit Log.

Detecta:
  - Baremos sospechosos (PD fuera de rango del baremo)
  - PD outliers estadísticos (z-score > 3)
  - Distribución anómala de diagnósticos
  - Evaluaciones sin firmar con >7 días
  - Volumen inusual de eventos (posible scraping)

Ejecutar:
  - Manualmente: `python -m app.infrastructure.audit.monitor`
  - Automáticamente: vía APScheduler job `audit_monitor_daily` (6 AM diario)
"""
from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from app.infrastructure.database.engine import session_scope
from app.infrastructure.database.orm_models import (
    AuditLogORM,
    EvaluationORM,
    ObservationORM,
    PatientORM,
)

logger = logging.getLogger("neurosoft.audit.monitor")

REPORTS_DIR = Path("data/audit_reports")


class AuditMonitor:
    """Monitor del audit log con detección de anomalías."""

    OUTLIER_ZSCORE_THRESHOLD = 3.0
    MIN_SAMPLE_FOR_OUTLIER = 10
    HIGH_DX_FREQUENCY_THRESHOLD = 0.5
    STALE_EVAL_DAYS = 7
    AUDIT_LOG_MAX_EVENTS_PER_DAY = 1000

    def __init__(self, db_session=None):
        """
        Args:
            db_session: Sesión SQLAlchemy opcional. Si no se pasa, se usa session_scope().
                        Útil para testing con in-memory DB.
        """
        self._external_db = db_session
        self.alerts: list[dict] = []

    def _get_db(self):
        """Context manager: usa la sesión externa si se pasó, sino session_scope()."""
        if self._external_db is not None:
            from contextlib import contextmanager
            @contextmanager
            def _ctx():
                try:
                    yield self._external_db
                finally:
                    pass
            return _ctx()
        return session_scope()

    def run_all_checks(self) -> dict[str, Any]:
        """Ejecuta todos los checks y retorna reporte completo."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "baremo_outliers": self.check_baremo_outliers(),
                "dx_distribution": self.check_dx_distribution(),
                "pd_outliers": self.check_pd_outliers(),
                "stale_evaluations": self.check_stale_evaluations(),
                "audit_log_volume": self.check_audit_log_volume(),
            },
            "alerts": list(self.alerts),
            "summary": self._summary(),
        }
        return report

    def check_baremo_outliers(self) -> dict[str, Any]:
        """Detecta PD que caen fuera del rango del baremo."""
        outliers = []
        with self._get_db() as db:
            evs = db.query(EvaluationORM).all()
            for ev in evs:
                resultados = json.loads(ev.resultados_json or "[]")
                for r in resultados:
                    metadata = r.get("metadata", {})
                    if metadata.get("out_of_baremo"):
                        outliers.append({
                            "evaluation_id": ev.id,
                            "patient_id": ev.patient_id,
                            "test_id": r.get("test_id"),
                            "pd": r.get("puntaje_bruto"),
                            "razon": metadata.get("error", "PD fuera del rango del baremo"),
                            "fecha": ev.fecha.isoformat() if ev.fecha else None,
                        })
        if outliers:
            self._add_alert(
                "MEDIUM", "BARE_OUTLIER",
                f"{len(outliers)} puntajes brutos fuera del rango del baremo detectados.",
                details=outliers[:10],
            )
        return {"n_outliers": len(outliers), "outliers": outliers[:20]}

    def check_dx_distribution(self) -> dict[str, Any]:
        """Detecta distribución anómala de diagnósticos."""
        cie10_counts: Counter = Counter()
        with self._get_db() as db:
            patients = db.query(PatientORM).all()
            for p in patients:
                if p.codigo_rips:
                    cie10_counts[p.codigo_rips.split(".")[0]] += 1
        total = sum(cie10_counts.values())
        top_5 = [
            {"dx": code, "count": cnt, "pct": round(cnt / total * 100, 1) if total else 0}
            for code, cnt in cie10_counts.most_common(5)
        ]
        # Alerta si un dx representa >50% del total
        if top_5 and top_5[0]["pct"] > self.HIGH_DX_FREQUENCY_THRESHOLD * 100:
            self._add_alert(
                "LOW", "DX_DISTRIBUTION",
                f"Diagnóstico {top_5[0]['dx']} representa {top_5[0]['pct']}% de la cohorte.",
            )
        return {"total_with_dx": total, "top_5": top_5}

    def check_pd_outliers(self) -> dict[str, Any]:
        """Detecta PD con z-score > 3 (outliers estadísticos)."""
        with self._get_db() as db:
            evs = db.query(EvaluationORM).filter(EvaluationORM.is_latest == True).all()
            by_test: dict[str, list] = defaultdict(list)
            for ev in evs:
                pd_dict = json.loads(ev.puntajes_brutos_json or "{}")
                for test_id, pd in pd_dict.items():
                    if pd != 9999:
                        by_test[test_id].append({
                            "pd": pd,
                            "evaluation_id": ev.id,
                        })
            outliers = []
            for test_id, samples in by_test.items():
                if len(samples) < self.MIN_SAMPLE_FOR_OUTLIER:
                    continue
                pds = [s["pd"] for s in samples]
                avg = mean(pds)
                sd = pstdev(pds) if len(pds) > 1 else 0
                if sd == 0:
                    continue
                for s in samples:
                    z = (s["pd"] - avg) / sd
                    if abs(z) > self.OUTLIER_ZSCORE_THRESHOLD:
                        outliers.append({
                            "test_id": test_id,
                            "pd": s["pd"],
                            "z_score": round(z, 2),
                            "evaluation_id": s["evaluation_id"],
                        })
        if outliers:
            self._add_alert(
                "LOW", "PD_OUTLIER",
                f"{len(outliers)} puntajes con z-score > 3 detectados.",
                details=outliers[:10],
            )
        return {"n_outliers": len(outliers), "outliers": outliers[:20]}

    def check_stale_evaluations(self) -> dict[str, Any]:
        """Detecta evaluaciones sin firmar con >7 días."""
        with self._get_db() as db:
            cutoff = datetime.utcnow() - timedelta(days=self.STALE_EVAL_DAYS)
            stale = db.query(EvaluationORM).filter(
                EvaluationORM.signed_at.is_(None),
                EvaluationORM.created_at < cutoff,
            ).all()
        if stale:
            self._add_alert(
                "MEDIUM", "STALE_EVAL",
                f"{len(stale)} evaluaciones sin firmar con >{self.STALE_EVAL_DAYS} días.",
                details=[
                    {"id": e.id, "patient_id": e.patient_id,
                     "fecha": e.fecha.isoformat() if e.fecha else None}
                    for e in stale[:10]
                ],
            )
        return {"n_stale": len(stale), "stale_ids": [e.id for e in stale[:20]]}

    def check_audit_log_volume(self) -> dict[str, Any]:
        """Monitorea volumen de audit log (alerta si >1000 eventos/día)."""
        with self._get_db() as db:
            last_24h = datetime.utcnow() - timedelta(hours=24)
            count = db.query(AuditLogORM).filter(
                AuditLogORM.ts >= last_24h,
            ).count()
        if count > self.AUDIT_LOG_MAX_EVENTS_PER_DAY:
            self._add_alert(
                "HIGH", "AUDIT_VOLUME",
                f"Volumen inusual: {count} eventos de audit en últimas 24h.",
            )
        return {"events_last_24h": count}

    def _add_alert(self, severity: str, alert_type: str, message: str, details: Any = None) -> None:
        self.alerts.append({
            "severity": severity,
            "type": alert_type,
            "message": message,
            "details": details,
        })

    def _summary(self) -> dict[str, Any]:
        sev_counts = Counter(a["severity"] for a in self.alerts)
        return {
            "total_alerts": len(self.alerts),
            "by_severity": dict(sev_counts),
        }


def save_report(report: dict) -> Path:
    """Guarda el reporte en data/audit_reports/."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = REPORTS_DIR / f"report_{timestamp}.json"
    path.write_text(
        json.dumps(report, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def main() -> None:
    """Punto de entrada CLI."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    logger.info("Iniciando monitor de audit log...")
    monitor = AuditMonitor()
    report = monitor.run_all_checks()
    path = save_report(report)
    logger.info("Reporte guardado en: %s", path)
    logger.info("Total alertas: %d (%s)", len(report["alerts"]), report["summary"]["by_severity"])
    # Print summary
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
