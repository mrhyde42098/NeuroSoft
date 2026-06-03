"""
app/domain/clinical_engine/grober_buschke.py
=============================================
Motor de puntuación e interpretación del test Grober-Buschke (FCSRT).

El test Grober-Buschke / FCSRT (Free and Cued Selective Reminding Test) es el
estándar de oro para distinguir entre fallo de codificación (patrón amnésico,
sugerente de EA) y fallo recuperación (patrón disejecutivo, sugerente de
afectación frontal/subcortical).

Protocolo estándar:
    • 16 palabras agrupadas en 16 categorías semánticas únicas.
    • 3 ensayos de aprendizaje: recuerdo libre + recuerdo con clave semántica.
    • Recuerdo diferido (tras 20–30 min con tarea interferente): libre + clave.
    • Reconocimiento final con 16 palabras-diana + 16 distractores.

Este módulo es agnóstico a la lista específica: acepta la palabra-lista por
parámetro, de modo que pueda usarse con la versión institucional (16 palabras
propias, configurables desde el front) o variantes clínicas equivalentes.

Interpretación:
    • Total libre 3 ensayos (max 48)      → rendimiento general
    • Total libre+clave 3 ensayos (max 48)→ eficacia con asistencia
    • Beneficio clave = (clave) / (16 − libre)  → índice de asistencia efectiva
    • Reconocimiento (aciertos − falsos)   → integridad de la huella mnésica
    • Índice consistencia = palabras recordadas libremente en ≥ 2 ensayos
    • Intrusiones (palabras no incluidas en la lista)
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

# ─────────────────────────────────────────────────────────────
# Lista semilla: 16 palabras × 16 categorías (configurable)
# La versión institucional suele proponer una lista en español
# castellano-colombiano; mientras la lista definitiva no se cargue
# por config, se usa esta lista canónica adaptada del protocolo
# Grober-Buschke clásico.
# ─────────────────────────────────────────────────────────────
DEFAULT_WORD_LIST: list[dict] = [
    {"palabra": "uva",        "categoria": "fruta"},
    {"palabra": "oso",        "categoria": "animal_salvaje"},
    {"palabra": "martillo",   "categoria": "herramienta"},
    {"palabra": "camisa",     "categoria": "prenda"},
    {"palabra": "trompeta",   "categoria": "instrumento_musical"},
    {"palabra": "lechuga",    "categoria": "verdura"},
    {"palabra": "bicicleta",  "categoria": "vehiculo"},
    {"palabra": "silla",      "categoria": "mueble"},
    {"palabra": "rosa",       "categoria": "flor"},
    {"palabra": "tenedor",    "categoria": "utensilio_cocina"},
    {"palabra": "sardina",    "categoria": "pez"},
    {"palabra": "abeja",      "categoria": "insecto"},
    {"palabra": "cobre",      "categoria": "metal"},
    {"palabra": "medico",     "categoria": "profesion"},
    {"palabra": "rubi",       "categoria": "piedra_preciosa"},
    {"palabra": "basquetbol", "categoria": "deporte"},
]

NUM_ITEMS = 16
DEFAULT_NUM_TRIALS = 3


# ─────────────────────────────────────────────────────────────
# DTOs
# ─────────────────────────────────────────────────────────────
@dataclass
class GroberTrial:
    """Un ensayo de aprendizaje: palabras libres + palabras con clave."""
    libre: list[str] = field(default_factory=list)
    con_clave: list[str] = field(default_factory=list)
    intrusiones: list[str] = field(default_factory=list)


@dataclass
class GroberDiferido:
    """Recuerdo diferido (tras período de interferencia)."""
    libre: list[str] = field(default_factory=list)
    con_clave: list[str] = field(default_factory=list)
    intrusiones: list[str] = field(default_factory=list)


@dataclass
class GroberReconocimiento:
    """Reconocimiento final con distractores."""
    aciertos: int = 0
    falsos_positivos: int = 0
    total_dianas: int = NUM_ITEMS
    total_distractores: int = NUM_ITEMS


@dataclass
class GroberResult:
    # Totales brutos
    total_libre: int
    total_con_clave: int
    total_libre_mas_clave: int

    # Máximos teóricos (útiles para front)
    max_libre: int
    max_total: int

    # Derivados
    beneficio_clave: float            # rango 0.0–1.0
    indice_consistencia: int          # 0–16
    total_intrusiones: int

    # Diferido
    diferido_libre: int
    diferido_con_clave: int
    diferido_total: int
    diferido_intrusiones: int

    # Reconocimiento
    reconocimiento_aciertos: int
    reconocimiento_falsos: int
    indice_discriminabilidad: float   # aciertos/total − falsos/total  (−1…1)

    # Interpretación
    patron: str                       # "amnesico" | "disejecutivo" | "mixto" | "normal"
    interpretacion: str               # descripción clínica
    alertas: list[str]

    def as_dict(self) -> dict:
        return {
            "aprendizaje": {
                "total_libre":          self.total_libre,
                "total_con_clave":      self.total_con_clave,
                "total_libre_mas_clave":self.total_libre_mas_clave,
                "max_libre":            self.max_libre,
                "max_total":            self.max_total,
                "beneficio_clave":      round(self.beneficio_clave, 3),
                "indice_consistencia":  self.indice_consistencia,
                "intrusiones":          self.total_intrusiones,
            },
            "diferido": {
                "libre":        self.diferido_libre,
                "con_clave":    self.diferido_con_clave,
                "total":        self.diferido_total,
                "intrusiones":  self.diferido_intrusiones,
            },
            "reconocimiento": {
                "aciertos":                self.reconocimiento_aciertos,
                "falsos_positivos":        self.reconocimiento_falsos,
                "indice_discriminabilidad":round(self.indice_discriminabilidad, 3),
            },
            "interpretacion": {
                "patron":           self.patron,
                "descripcion":      self.interpretacion,
                "alertas":          self.alertas,
            },
        }


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def _norm(palabra: str) -> str:
    """Normaliza una palabra: lowercase, strip, sin tildes ni puntuación trivial."""
    import unicodedata
    s = (palabra or "").strip().lower()
    s = "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )
    return s.replace(".", "").replace(",", "").replace("-", "")


def _word_set(word_list: Sequence[dict]) -> set[str]:
    return {_norm(w["palabra"]) for w in word_list}


def _count_correct(said: Iterable[str], target_set: set[str]) -> tuple[int, list[str]]:
    """Cuenta coincidencias únicas y devuelve intrusiones detectadas."""
    seen: set[str] = set()
    intrusos: list[str] = []
    for w in said:
        nw = _norm(w)
        if not nw:
            continue
        if nw in target_set and nw not in seen:
            seen.add(nw)
        elif nw not in target_set:
            intrusos.append(w)
    return len(seen), intrusos


# ─────────────────────────────────────────────────────────────
# Motor principal
# ─────────────────────────────────────────────────────────────
def score_grober_buschke(
    trials: Sequence[GroberTrial],
    diferido: GroberDiferido | None = None,
    reconocimiento: GroberReconocimiento | None = None,
    word_list: Sequence[dict] | None = None,
) -> GroberResult:
    """
    Calcula el perfil completo de Grober-Buschke.

    trials: lista de ensayos de aprendizaje (típicamente 3).
    diferido: recobro diferido (opcional).
    reconocimiento: fase de reconocimiento (opcional pero recomendado).
    word_list: lista con las 16 palabras; si None usa DEFAULT_WORD_LIST.
    """
    wl = list(word_list) if word_list else list(DEFAULT_WORD_LIST)
    if len(wl) != NUM_ITEMS:
        raise ValueError(
            f"La lista debe contener exactamente {NUM_ITEMS} palabras; recibió {len(wl)}."
        )
    if not trials:
        raise ValueError("Se requiere al menos 1 ensayo de aprendizaje.")

    target = _word_set(wl)
    num_trials = len(trials)

    # ── Aprendizaje ──
    total_libre = 0
    total_con_clave = 0
    total_intrusiones = 0
    libres_por_ensayo: list[set[str]] = []

    for t in trials:
        n_libre, intr_libre = _count_correct(t.libre, target)
        # clave: se cuentan palabras RECUPERADAS con clave que no fueron libres
        libre_norm = {_norm(w) for w in t.libre if _norm(w) in target}
        n_clave = 0
        intr_clave: list[str] = []
        for w in t.con_clave:
            nw = _norm(w)
            if nw in target and nw not in libre_norm:
                n_clave += 1
                libre_norm.add(nw)
            elif nw not in target and nw:
                intr_clave.append(w)

        total_libre += n_libre
        total_con_clave += n_clave
        total_intrusiones += len(intr_libre) + len(intr_clave) + len(t.intrusiones)
        libres_por_ensayo.append({_norm(w) for w in t.libre if _norm(w) in target})

    total_libre_mas_clave = total_libre + total_con_clave
    max_libre = NUM_ITEMS * num_trials
    max_total = max_libre

    # ── Beneficio de clave: clave / (max_libre − libre) ──
    margen = max_libre - total_libre
    beneficio_clave = (total_con_clave / margen) if margen > 0 else 1.0

    # ── Índice de consistencia: palabras libres en ≥ 2 ensayos ──
    palabras_repetidas: set[str] = set()
    for w in target:
        count = sum(1 for ensayo in libres_por_ensayo if w in ensayo)
        if count >= 2:
            palabras_repetidas.add(w)
    indice_consistencia = len(palabras_repetidas)

    # ── Diferido ──
    diferido_libre = diferido_con_clave = diferido_intrusiones = 0
    if diferido:
        n_libre, intr_libre = _count_correct(diferido.libre, target)
        libre_norm = {_norm(w) for w in diferido.libre if _norm(w) in target}
        n_clave = 0
        intr_clave: list[str] = []
        for w in diferido.con_clave:
            nw = _norm(w)
            if nw in target and nw not in libre_norm:
                n_clave += 1
                libre_norm.add(nw)
            elif nw not in target and nw:
                intr_clave.append(w)

        diferido_libre = n_libre
        diferido_con_clave = n_clave
        diferido_intrusiones = len(intr_libre) + len(intr_clave) + len(diferido.intrusiones)

    diferido_total = diferido_libre + diferido_con_clave

    # ── Reconocimiento ──
    rec_aciertos = reconocimiento.aciertos if reconocimiento else 0
    rec_falsos   = reconocimiento.falsos_positivos if reconocimiento else 0
    total_dianas = reconocimiento.total_dianas if reconocimiento else NUM_ITEMS
    total_distr  = reconocimiento.total_distractores if reconocimiento else NUM_ITEMS

    if total_dianas > 0 and total_distr > 0:
        discriminabilidad = (rec_aciertos / total_dianas) - (rec_falsos / total_distr)
    else:
        discriminabilidad = 0.0

    # ── Interpretación de patrones ──
    patron, descripcion, alertas = _classify_pattern(
        total_libre=total_libre,
        total_libre_mas_clave=total_libre_mas_clave,
        max_total=max_total,
        beneficio_clave=beneficio_clave,
        diferido_libre=diferido_libre,
        diferido_total=diferido_total,
        rec_aciertos=rec_aciertos,
        rec_falsos=rec_falsos,
        total_dianas=total_dianas,
        total_intrusiones=total_intrusiones,
    )

    return GroberResult(
        total_libre=total_libre,
        total_con_clave=total_con_clave,
        total_libre_mas_clave=total_libre_mas_clave,
        max_libre=max_libre,
        max_total=max_total,
        beneficio_clave=beneficio_clave,
        indice_consistencia=indice_consistencia,
        total_intrusiones=total_intrusiones,
        diferido_libre=diferido_libre,
        diferido_con_clave=diferido_con_clave,
        diferido_total=diferido_total,
        diferido_intrusiones=diferido_intrusiones,
        reconocimiento_aciertos=rec_aciertos,
        reconocimiento_falsos=rec_falsos,
        indice_discriminabilidad=discriminabilidad,
        patron=patron,
        interpretacion=descripcion,
        alertas=alertas,
    )


# ─────────────────────────────────────────────────────────────
# Clasificador de patrón
# ─────────────────────────────────────────────────────────────
def _classify_pattern(
    *,
    total_libre: int,
    total_libre_mas_clave: int,
    max_total: int,
    beneficio_clave: float,
    diferido_libre: int,
    diferido_total: int,
    rec_aciertos: int,
    rec_falsos: int,
    total_dianas: int,
    total_intrusiones: int,
) -> tuple[str, str, list[str]]:
    """
    Reglas simplificadas (cuartiles aproximados, sin baremos — el baremado
    definitivo se hace con NEURONORMA o tablas locales):

        • Rendimiento libre bajo  (≤ 50 % de max)
        • Buen beneficio de clave (≥ 0.65)       → sugiere fallo de recuperación
        • Pobre beneficio de clave y mal reconocimiento → fallo de codificación
        • Diferido libre muy bajo pero diferido total alto → disejecutivo
        • Reconocimiento pobre con muchos falsos → amnésico con confabulación
    """
    alertas: list[str] = []
    ratio_libre = total_libre / max_total if max_total > 0 else 0.0
    ratio_total = total_libre_mas_clave / max_total if max_total > 0 else 0.0
    ratio_reconocimiento = rec_aciertos / total_dianas if total_dianas > 0 else 0.0

    bajo_libre = ratio_libre < 0.50
    buen_beneficio_clave = beneficio_clave >= 0.65
    mal_beneficio_clave = beneficio_clave < 0.40
    buen_reconocimiento = ratio_reconocimiento >= 0.90 and rec_falsos <= 2
    mal_reconocimiento = ratio_reconocimiento < 0.75 or rec_falsos > 4

    if total_intrusiones >= 5:
        alertas.append("Alto número de intrusiones — posible fallo inhibitorio o confabulación.")
    if rec_falsos > 4:
        alertas.append("Falsos positivos elevados en reconocimiento — compromiso de discriminación.")

    # Normal
    if not bajo_libre and ratio_total >= 0.85 and buen_reconocimiento:
        return (
            "normal",
            "Rendimiento de memoria verbal episódica dentro de límites de la normalidad. "
            "Codificación, recuperación y reconocimiento preservados.",
            alertas,
        )

    # Amnésico puro (codificación) — EA probable
    if bajo_libre and mal_beneficio_clave and mal_reconocimiento:
        return (
            "amnesico",
            "Patrón de compromiso mnésico con fallo de codificación: el recuerdo libre "
            "es bajo, la clave semántica no asiste eficazmente y el reconocimiento "
            "es deficitario. Sugiere compromiso medial temporal (perfil compatible con "
            "enfermedad de Alzheimer prodrómica / probable).",
            alertas,
        )

    # Disejecutivo — EP, vascular, frontal
    if bajo_libre and buen_beneficio_clave and ratio_reconocimiento >= 0.85:
        return (
            "disejecutivo",
            "Patrón de memoria disejecutiva: el recuerdo libre es bajo pero la clave "
            "semántica asiste de forma eficaz y el reconocimiento está preservado. "
            "Sugiere fallo en estrategias de recuperación con codificación indemne "
            "(perfil frontal/subcortical — compatible con EP, DCLv, depresión).",
            alertas,
        )

    # Mixto
    if bajo_libre:
        return (
            "mixto",
            "Patrón mixto de afectación mnésica con elementos de codificación y "
            "recuperación. El beneficio de clave es parcial y el reconocimiento "
            "muestra dificultades. Requiere integración con otros marcadores.",
            alertas,
        )

    # Limítrofe
    return (
        "limitrofe",
        "Rendimiento en el límite inferior del rango esperado. Memoria episódica "
        "parcialmente preservada con asistencia; se recomienda seguimiento.",
        alertas,
    )
