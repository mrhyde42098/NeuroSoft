"""
Límites de sanity-check para puntajes directos (PD).
Espejo del frontend ScoreInput.jsx — no reemplaza baremos.
"""
from __future__ import annotations

SENTINEL_NA = 9999

# test_id → [min, max_aprox_baremo]
SANITY_RANGES: dict[str, tuple[int, int]] = {
    "NiWiscDC": (0, 70), "NiWiscSem": (0, 44), "NiWiscVoc": (0, 68),
    "NiWiscLN": (0, 30), "NiWiscCl": (0, 120), "NiWiscMat": (0, 35),
    "NiWiscCom": (0, 42), "NiWiscAri": (0, 30), "NiWiscBusSim": (0, 120),
    "NiWiscRDD": (0, 30), "NiWiscConD": (0, 35),
    "AdWAISV": (0, 70), "AdSemWais": (0, 40), "AdWAISC": (0, 35),
    "AdWAISI": (0, 33), "AdWAISA": (0, 25), "AdWAISL": (0, 21),
    "AdSDWais": (0, 133), "AdMatr": (0, 26), "AdWAISFI": (0, 25),
    "AdWAISCC": (0, 90), "AdDDir": (0, 20),
    "ViTMTA": (0, 300), "ViTMTB": (0, 500), "AdTMTA": (0, 300), "AdTMTB": (0, 500),
    "ViRDD": (0, 12), "ViRDInv": (0, 12), "ViStP": (0, 120), "ViStC": (0, 100),
    "ViAni": (0, 40), "ViSem": (0, 30), "ViYesavage": (0, 15), "EscYesavage": (0, 15),
    "SDMT": (0, 110), "GBTotal": (0, 48), "REY15": (0, 15), "TOMM": (0, 50),
}


def validate_puntaje_bruto(test_id: str, value: float | int) -> str | None:
    """Retorna mensaje de error o None si OK."""
    if value == SENTINEL_NA:
        return None
    if value < 0:
        return f"{test_id}: PD no puede ser negativo"
    rng = SANITY_RANGES.get(test_id)
    if rng and value > rng[1] * 2:
        return f"{test_id}: PD {value} excede el doble del máx baremo (~{rng[1]})"
    return None
