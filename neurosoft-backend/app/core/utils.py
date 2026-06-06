"""
app/core/utils.py
=================
Funciones utilitarias determinísticas del sistema.

Determinísticas significa: dado el mismo input, siempre producen
el mismo output. Sin efectos secundarios, sin I/O, sin estado.

Contiene:
    - AgeCalculator: cálculo exacto de edad cronológica
    - BaremoKeyBuilder: construcción de llaves de búsqueda en baremos
    - ClinicalInterpreter: conversión de puntajes a clasificaciones
    - EscolaridadMapper: mapeo de niveles educativos a claves de baremo
"""

from __future__ import annotations

import calendar
import logging
import math
from dataclasses import dataclass
from datetime import date, datetime

logger = logging.getLogger(__name__)

# ============================================================
# AGE CALCULATOR
# ============================================================


@dataclass(frozen=True)
class CronologicalAge:
    """
    Edad cronológica exacta. Inmutable por diseño (frozen=True).

    La inmutabilidad garantiza que nadie modifica la edad
    durante el ciclo de vida de un request.
    """

    years: int
    months: int
    days: int
    total_months: int  # years * 12 + months
    birth_date: date
    reference_date: date

    @property
    def decimal_years(self) -> float:
        """Edad en años con decimales. Ej: 8 años 6 meses → 8.5"""
        return round(self.years + self.months / 12.0, 4)

    @property
    def display(self) -> str:
        """Representación legible para el informe. Ej: '10 años, 3 meses'"""
        return f"{self.years} años, {self.months} meses"

    def __str__(self) -> str:
        return f"{self.years} años, {self.months} meses, {self.days} días"


class AgeCalculator:
    """
    Calculadora de edad cronológica exacta.

    Corrige el bug del VBA original que usaba DateDiff("yyyy", ...)
    sin verificar si el cumpleaños ya había ocurrido ese año.

    Todos los métodos son estáticos. No instanciar.
    """

    @staticmethod
    def calculate(
        birth_date: date | str,
        reference_date: date | None = None,
    ) -> CronologicalAge:
        """
        Calcula la edad exacta entre birth_date y reference_date.

        Args:
            birth_date: Fecha de nacimiento. Acepta date o strings:
                        'YYYY-MM-DD', 'DD/MM/YYYY', 'MM/DD/YYYY'
            reference_date: Fecha de evaluación (default: hoy).

        Returns:
            CronologicalAge con años, meses, días y helpers.

        Raises:
            ValueError: Fecha inválida o fecha futura.
        """
        fn = AgeCalculator._parse(birth_date)
        ref = reference_date or date.today()

        if fn > ref:
            raise ValueError(f"La fecha de nacimiento {fn} es posterior a {ref}.")

        # Años completos
        years = ref.year - fn.year
        try:
            cumple = fn.replace(year=ref.year)
        except ValueError:
            cumple = date(ref.year, 3, 1)  # 29-Feb en año no bisiesto

        if ref < cumple:
            years -= 1

        # Meses adicionales
        try:
            inicio = fn.replace(year=ref.year - (0 if ref >= cumple else 1))
        except ValueError:
            inicio = date(ref.year - (0 if ref >= cumple else 1), 3, 1)

        months = (ref.year - inicio.year) * 12 + (ref.month - inicio.month)
        if ref.day < fn.day:
            months -= 1
        if months < 0:
            months = 11

        # Días adicionales
        yr = inicio.year + (inicio.month + months - 1) // 12
        mo = (inicio.month + months - 1) % 12 + 1
        last_day = calendar.monthrange(yr, mo)[1]
        try:
            mes_inicio = date(yr, mo, min(fn.day, last_day))
        except ValueError:
            mes_inicio = date(yr, mo, last_day)

        days = max(0, (ref - mes_inicio).days)

        return CronologicalAge(
            years=years,
            months=months,
            days=days,
            total_months=years * 12 + months,
            birth_date=fn,
            reference_date=ref,
        )

    @staticmethod
    def _parse(d: date | str) -> date:
        if isinstance(d, datetime):
            return d.date()
        if isinstance(d, date):
            return d
        if isinstance(d, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(d, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"Formato de fecha no reconocido: '{d}'")
        raise TypeError(f"Tipo no soportado: {type(d)}")


# ============================================================
# BAREMO KEY BUILDER
# ============================================================

# Rangos etarios REALES del JSON colombiano (extraídos por ingeniería inversa)
_WAIS_RANGES = [
    (16, 19, "1619"),
    (20, 24, "2024"),
    (25, 34, "2534"),
    (35, 54, "3554"),
    (55, 69, "5569"),
    (70, 99, "7000"),
]
_AM_RANGES = [
    (50, 56, "5056"),
    (57, 59, "5759"),
    (60, 62, "6062"),
    (63, 65, "6365"),
    (66, 68, "6668"),
    (69, 71, "6971"),
    (72, 74, "7274"),
    (75, 77, "7577"),
    (78, 80, "7880"),
    (81, 99, "8190"),
]
_MONTH_BRACKETS = [(0, 3, "03"), (4, 7, "47"), (8, 11, "811")]


class BaremoKeyBuilder:
    """
    Construye las llaves de búsqueda para los distintos formatos de baremo.

    El formato de llave varía según el tipo de prueba:
        Formato A  → {años}{pd}                 ENI-2, EAD, Spence
        Formato B  → {años}{bracket_mes}{pd}    WISC-IV, K-ABC
        Formato M  → {total_meses}{pd}          NiComp, NiDR (lectura)
        Formato W  → {rango_wais}{pd}           WAIS-III adulto joven
        Formato AM → {rango_am}{pd}             pruebas geriátricas
    """

    @classmethod
    def build_candidates(cls, years: int, months: int, pd: int) -> list[str]:
        """
        Genera todas las llaves candidatas ordenadas de más a menos específica.
        El motor prueba cada una hasta encontrar la primera que exista.
        """
        pd_s = str(pd)
        total_m = years * 12 + months
        keys: list[str] = []

        # B: WISC bracket mensual (más específico)
        bm = next((c for mn, mx, c in _MONTH_BRACKETS if mn <= months <= mx), None)
        if bm:
            keys.append(f"{years}{bm}{pd_s}")

        # A: solo año
        keys.append(f"{years}{pd_s}")

        # M: meses totales (NiComp, NiDR, K-ABC)
        keys.append(f"{total_m}{pd_s}")

        # W: rango WAIS
        wk = next((f"{c}{pd_s}" for mn, mx, c in _WAIS_RANGES if mn <= years <= mx), None)
        if wk:
            keys.append(wk)

        # AM: rango adulto mayor (multi-range + 5056 single-range fallback)
        ak = next((f"{c}{pd_s}" for mn, mx, c in _AM_RANGES if mn <= years <= mx), None)
        if ak:
            keys.append(ak)
        if years >= 50:
            fallback = f"5056{pd_s}"
            if fallback not in keys:
                keys.append(fallback)

        # Fallback final: PD directo como string
        keys.append(pd_s)

        return keys

    @classmethod
    def find_in_baremo(cls, baremo: dict, years: int, months: int, pd: int) -> tuple[str, object] | None:
        """Busca el PD en el baremo y retorna (llave_usada, valor) o None."""
        for k in cls.build_candidates(years, months, pd):
            if k in baremo:
                return k, baremo[k]
        return None

    @classmethod
    def max_age_covered_by_am_baremo(cls, baremo: dict) -> int:
        """
        Retorna la edad máxima (años) cubierta por el baremo de adulto mayor.

        Útil para detectar cuándo un paciente tiene más años que el máximo
        disponible en el baremo y mostrar 'Sin norma disponible' en lugar
        de usar el fallback 5056 (que daría valores incorrectos).

        Retorna 0 si el baremo no usa rangos AM.
        """
        max_age = 0
        for mn, mx, code in _AM_RANGES:
            if any(str(k).startswith(code) for k in baremo):
                max_age = mx
        return max_age

    @classmethod
    def patient_in_am_baremo_range(cls, baremo: dict, years: int) -> bool:
        """
        Retorna True si el paciente (en años) está dentro del rango cubierto
        por el baremo de adulto mayor. False = sin norma disponible.
        """
        max_covered = cls.max_age_covered_by_am_baremo(baremo)
        if max_covered == 0:
            return True  # No usa rangos AM, asumir OK
        min_covered = 999
        for mn, mx, code in _AM_RANGES:
            if any(str(k).startswith(code) for k in baremo):
                min_covered = min(min_covered, mn)
                break
        return min_covered <= years <= max_covered

    @classmethod
    def wais_key(cls, years: int, pd: int) -> str | None:
        rango = next((c for mn, mx, c in _WAIS_RANGES if mn <= years <= mx), None)
        return f"{rango}{pd}" if rango else None

    @classmethod
    def am_key(cls, years: int, pd: int) -> str | None:
        rango = next((c for mn, mx, c in _AM_RANGES if mn <= years <= mx), None)
        if rango:
            return f"{rango}{pd}"
        return f"5056{pd}" if years >= 50 else None

    @classmethod
    def mrem_key(cls, years: int, escolaridad: str) -> str | None:
        """
        Clave para ViMRemRec (Memoria Remota y Reciente).
        Formato: {rango_decada}{esc_neuronorma}
        5069=50-69a | 7079=70-79a | 8000=80+a
        """
        if years < 50:
            return None
        rango = "5069" if years <= 69 else ("7079" if years <= 79 else "8000")
        esc = _EDU_CODE_NEURONORMA_AM.get(escolaridad, "S")
        return f"{rango}{esc}"

    @classmethod
    def escolaridad_key(cls, years: int, edu_code: str) -> str:
        """Clave para baremos tipo escolaridad_pc50. Ej: 28U, 35S"""
        return f"{years}{edu_code}"


# ============================================================
# CLINICAL INTERPRETER
# ============================================================

# Tabla de cortes extraída del nodo _meta de BD_NEURO_MAESTRA.json
_CUTOFFS: dict[str, list[tuple]] = {
    "escalar": [(0, 4, "Bajo"), (5, 6, "Limítrofe"), (7, 12, "Promedio"), (13, 19, "Superior")],
    "ci": [(0, 69, "Bajo"), (70, 79, "Limítrofe"), (80, 119, "Promedio"), (120, 999, "Superior")],
    "puntaje_t": [(0, 29, "Bajo"), (30, 39, "Limítrofe"), (40, 59, "Promedio"), (60, 999, "Superior")],
    "z_score": [(-99, -2.01, "Bajo"), (-2.0, -1.01, "Limítrofe"), (-1.0, 0.99, "Promedio"), (1.0, 99, "Superior")],
    "percentil": [(0, 10, "Bajo"), (11, 24, "Limítrofe"), (25, 75, "Promedio"), (76, 100, "Superior")],
}


class ClinicalInterpreter:
    """
    Convierte puntajes numéricos a clasificaciones cualitativas.
    Fuente: nodo _meta de BD_NEURO_MAESTRA.json.
    """

    @classmethod
    def interpret(cls, score: float, metric_type: str) -> str:
        """
        Args:
            score:       Puntaje estandarizado (escalar, CI, T, Z, percentil).
            metric_type: Tipo de métrica del baremo.

        Returns:
            "Bajo" | "Limítrofe" | "Promedio" | "Superior" | "Sin dato"
        """
        if score is None or (isinstance(score, float) and math.isnan(score)):
            return "Sin dato"

        cutoffs = _CUTOFFS.get(metric_type, _CUTOFFS["escalar"])
        for mn, mx, label in cutoffs:
            if mn <= score <= mx:
                return label
        return "Sin dato"

    @classmethod
    def to_z_equivalent(cls, score: float, metric_type: str) -> float | None:
        """Normaliza cualquier puntaje a Z equivalente (para el gráfico de perfil)."""
        if score is None:
            return None
        try:
            v = float(score)
            if metric_type == "z_score":
                return round(max(-4, min(4, v)), 2)
            if metric_type == "escalar":
                return round((v - 10) / 3, 2)
            if metric_type == "ci":
                return round((v - 100) / 15, 2)
            if metric_type == "puntaje_t":
                return round((v - 50) / 10, 2)
            if metric_type == "percentil":
                if v <= 0:
                    return -4.0
                if v >= 100:
                    return 4.0
                p = v / 100.0
                t = math.sqrt(-2 * math.log(min(p, 1 - p)))
                c = [2.515517, 0.802853, 0.010328]
                d_c = [1.432788, 0.189269, 0.001308]
                z = t - (c[0] + c[1] * t + c[2] * t**2) / (1 + d_c[0] * t + d_c[1] * t**2 + d_c[2] * t**3)
                return round(-z if p < 0.5 else z, 2)
        except (TypeError, ValueError, ZeroDivisionError):
            pass
        return None


# ============================================================
# ESCOLARIDAD MAPPER
# ============================================================

# Niveles de escolaridad → código de baremo para adulto joven
_EDU_CODE_MAP: dict[str, str] = {
    # Códigos usados por ViTMTA, ViStP, ViRDD, etc. (baremos con rangos numéricos AM)
    # B = sin escolaridad formal o muy baja
    "Analfabeta": "B",
    "Primaria Incompleta": "B",
    "Primaria Completa": "S",
    "Secundaria Incompleta": "S",
    "Secundaria Completa": "S",
    "Técnico": "S",
    "Técnico/Tecnólogo": "T",
    "Universitario incompleto": "U",
    "Universitaria": "U",
    "Profesional": "U",
    "Postgrado": "P",
}

# Neuronorma Colombia AM: ViDeno, ViSem usan P/S/U (no B/T/P)
# P = Primaria (0-11 años escolaridad)
# S = Secundaria (12-15 años)
# U = Universitaria (16+ años)
_EDU_CODE_NEURONORMA_AM: dict[str, str] = {
    "Analfabeta": "P",  # Baremo agrupa bajo escolaridad → P
    "Primaria Incompleta": "P",
    "Primaria Completa": "P",
    "Secundaria Incompleta": "S",
    "Secundaria Completa": "S",
    "Técnico": "S",
    "Técnico/Tecnólogo": "S",
    "Universitario incompleto": "U",
    "Universitaria": "U",
    "Profesional": "U",
    "Postgrado": "U",
}


class EscolaridadMapper:
    """
    Mapea niveles educativos a códigos de baremo.

    Dos convenciones según el instrumento:
      - to_code():           B/S/T/U/P  — WISC, ENI, K-ABC, baremos generales
      - to_neuronorma_am():  P/S/U      — ViDeno, ViSem (Neuronorma Colombia AM)
    """

    @classmethod
    def to_code(cls, nivel: str) -> str:
        if nivel not in _EDU_CODE_MAP:
            logger.warning("Escolaridad no reconocida: '%s', usando fallback 'S' (Secundaria)", nivel)
        return _EDU_CODE_MAP.get(nivel, "S")

    @classmethod
    def to_neuronorma_am(cls, nivel: str) -> str:
        if nivel not in _EDU_CODE_NEURONORMA_AM:
            logger.warning("Escolaridad Neuronorma AM no reconocida: '%s', usando fallback 'S'", nivel)
        return _EDU_CODE_NEURONORMA_AM.get(nivel, "S")

    @classmethod
    def get_all_levels(cls) -> list[str]:
        return list(_EDU_CODE_MAP.keys())
