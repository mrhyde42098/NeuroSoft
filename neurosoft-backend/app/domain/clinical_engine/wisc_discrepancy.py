"""
app/domain/clinical_engine/wisc_discrepancy.py
==============================================
Detector de discrepancias entre los cuatro índices WISC-IV (ICV, IRP, IMT, IVP)
y estimador de CIT por Forma Corta (Sattler, 2010).

Regla clínica: una diferencia ≥ 23 puntos (equivalente a 1.5 DE) entre dos
índices se considera DISCREPANCIA SIGNIFICATIVA — el CIT pierde valor
interpretativo como medida unitaria, y se recomienda reportar ICG o ICC
como alternativa.

Referencias:
  - Flanagan & Kaufman, 2009. Essentials of WISC-IV Assessment.
  - Sattler, 2010. Assessment of Children: Cognitive Foundations, 5th ed.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

# Umbral operativo: 23 puntos ≈ 1.5 DE en escala WISC (media 100, DE 15)
DISCREPANCY_THRESHOLD_POINTS: int = 23
DISCREPANCY_THRESHOLD_SD: float = 1.5

INDEX_LABELS = {
    "ICV": "Índice de Comprensión Verbal",
    "IRP": "Índice de Razonamiento Perceptivo",
    "IMT": "Índice de Memoria de Trabajo",
    "IVP": "Índice de Velocidad de Procesamiento",
}


@dataclass
class IndexPairDiff:
    a: str
    b: str
    diff: int
    significant: bool


@dataclass
class DiscrepancyResult:
    indices: dict                        # {"ICV": v, "IRP": v, "IMT": v, "IVP": v}
    max_diff: int
    pairs: list[IndexPairDiff]
    has_discrepancy: bool
    cit_reliable: bool
    recommended_alternative: str | None   # "ICG" | "ICC" | None
    recommendation_reason: str
    icg_recommended: bool
    icc_recommended: bool
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "indices": self.indices,
            "max_diff": self.max_diff,
            "threshold_points": DISCREPANCY_THRESHOLD_POINTS,
            "threshold_sd": DISCREPANCY_THRESHOLD_SD,
            "pairs": [
                {"a": p.a, "b": p.b, "diff": p.diff, "significant": p.significant}
                for p in self.pairs
            ],
            "has_discrepancy": self.has_discrepancy,
            "cit_reliable": self.cit_reliable,
            "recommended_alternative": self.recommended_alternative,
            "icg_recommended": self.icg_recommended,
            "icc_recommended": self.icc_recommended,
            "recommendation_reason": self.recommendation_reason,
            "notes": self.notes,
        }


def detect_discrepancy(
    icv: float | None,
    irp: float | None,
    imt: float | None,
    ivp: float | None,
) -> DiscrepancyResult:
    """
    Analiza los 4 índices WISC-IV y decide si existe discrepancia significativa.

    Lógica:
      - Si la diferencia máxima entre cualquier par de índices es ≥ 23 pts,
        hay discrepancia.
      - Si ICV e IRP son comparables entre sí (diff < 23) pero discrepan con
        IMT o IVP → recomendar ICG (Índice de Capacidad General, sólo ICV+IRP).
      - Si ICV+IRP también discrepan entre sí → recomendar ICC (Índice de
        Competencia Cognitiva, ICV+IRP+IMT) sólo si IMT se parece más a
        ICV/IRP que IVP. En caso contrario, análisis unitario por índice.
    """
    idx = {"ICV": icv, "IRP": irp, "IMT": imt, "IVP": ivp}
    vals = {k: v for k, v in idx.items() if v is not None}
    if len(vals) < 2:
        return DiscrepancyResult(
            indices=idx,
            max_diff=0,
            pairs=[],
            has_discrepancy=False,
            cit_reliable=True,
            recommended_alternative=None,
            icg_recommended=False,
            icc_recommended=False,
            recommendation_reason="Datos insuficientes: se requieren al menos 2 índices.",
            notes=["Ingrese al menos ICV e IRP para análisis completo."],
        )

    keys = list(vals.keys())
    pairs: list[IndexPairDiff] = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            d = int(abs(vals[a] - vals[b]))
            pairs.append(IndexPairDiff(
                a=a, b=b, diff=d,
                significant=d >= DISCREPANCY_THRESHOLD_POINTS,
            ))

    max_diff = max(p.diff for p in pairs) if pairs else 0
    has_disc = max_diff >= DISCREPANCY_THRESHOLD_POINTS

    recommended: str | None = None
    reason: str = ""
    notes: list[str] = []
    icg_ok = False
    icc_ok = False

    if not has_disc:
        reason = (
            "Los índices son comparables entre sí "
            f"(diferencia máx. = {max_diff} pts, umbral = {DISCREPANCY_THRESHOLD_POINTS}). "
            "El CIT es interpretable como medida unitaria."
        )
    else:
        # Evaluar si ICV+IRP son comparables (ICG viable)
        d_icv_irp: int | None = None
        if icv is not None and irp is not None:
            d_icv_irp = int(abs(icv - irp))
        # Evaluar ICV+IRP+IMT (ICC viable)
        d_with_imt: list[int] = []
        if imt is not None and icv is not None:
            d_with_imt.append(int(abs(icv - imt)))
        if imt is not None and irp is not None:
            d_with_imt.append(int(abs(irp - imt)))

        if d_icv_irp is not None and d_icv_irp < DISCREPANCY_THRESHOLD_POINTS:
            recommended = "ICG"
            icg_ok = True
            reason = (
                f"ICV e IRP son comparables (diff={d_icv_irp}). Hay discrepancia "
                "que involucra a IMT y/o IVP, por lo que el CIT no es "
                "interpretable como medida unitaria. Reporte el ICG (Índice de "
                "Capacidad General) calculado con ICV + IRP como estimación "
                "de capacidad intelectual."
            )
            # Si además IMT es similar a ICV/IRP, ICC también es viable
            if d_with_imt and all(d < DISCREPANCY_THRESHOLD_POINTS for d in d_with_imt):
                icc_ok = True
                notes.append(
                    "El ICC (Índice de Competencia Cognitiva, ICV+IRP+IMT) "
                    "también es una alternativa válida para este perfil."
                )
        else:
            recommended = None
            reason = (
                "Hay discrepancia significativa incluyendo a ICV y/o IRP. "
                "Ni CIT, ni ICG, ni ICC son interpretables como medida unitaria. "
                "Se requiere análisis individualizado de cada índice y de las "
                "funciones cognitivas evaluadas por cada uno."
            )
            notes.append(
                "Reporte el desempeño por índice por separado y evite una "
                "puntuación global única."
            )

    return DiscrepancyResult(
        indices=idx,
        max_diff=max_diff,
        pairs=pairs,
        has_discrepancy=has_disc,
        cit_reliable=not has_disc,
        recommended_alternative=recommended,
        icg_recommended=icg_ok,
        icc_recommended=icc_ok,
        recommendation_reason=reason,
        notes=notes,
    )


# ─────────────────────────────────────────────────────────────
# Forma Corta Sattler 2010 — CIT estimado
# ─────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _load_forma_corta_table() -> dict:
    path = Path(__file__).resolve().parents[1] / "data" / "wisc_iv_forma_corta_cit.json"
    return json.loads(path.read_text(encoding="utf-8"))


def estimate_cit_forma_corta(suma_escalares: int, forma: int = 1) -> dict:
    """
    Estima el CIT para Forma Corta WISC-IV según Sattler (2010).

    Args:
        suma_escalares: suma de las 4 puntuaciones escalares (rango 4–76).
        forma: 1 = DC+CD+MT+FI, 2 = VB+SE+CM+PC.

    Returns:
        dict con { suma, forma, cit_estimado, interpretacion }.
    """
    if forma not in (1, 2):
        raise ValueError(f"forma debe ser 1 o 2, recibido: {forma}")
    data = _load_forma_corta_table()
    lo, hi = data["min_suma"], data["max_suma"]
    s = int(suma_escalares)
    if s < lo or s > hi:
        raise ValueError(
            f"suma_escalares fuera de rango: {s}. Válido: [{lo}, {hi}]."
        )
    row = data["table"][str(s)]
    cit = row[f"forma{forma}"]

    # Clasificación clínica estándar (Wechsler)
    if   cit >= 130: interpret = "Muy Superior"
    elif cit >= 120: interpret = "Superior"
    elif cit >= 110: interpret = "Medio Alto"
    elif cit >= 90:  interpret = "Medio"
    elif cit >= 80:  interpret = "Medio Bajo"
    elif cit >= 70:  interpret = "Limítrofe"
    else:            interpret = "Extremadamente Bajo"

    return {
        "suma_escalares": s,
        "forma": forma,
        "cit_estimado": int(cit),
        "interpretacion": interpret,
        "source": data.get("source", "Sattler, 2010"),
    }


__all__ = [
    "DISCREPANCY_THRESHOLD_POINTS",
    "DISCREPANCY_THRESHOLD_SD",
    "INDEX_LABELS",
    "IndexPairDiff",
    "DiscrepancyResult",
    "detect_discrepancy",
    "estimate_cit_forma_corta",
]
