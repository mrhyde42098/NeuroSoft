# ═══════════════════════════════════════════════════════════════════════
# app/infrastructure/retencion.py — Política de retención de HC
# ───────────────────────────────────────────────────────────────────────
# S5.2 (Frente 5): Cumplimiento de Resolución 1995 de 1999, art. 28.
#
#   • HC adultos (≥18 años al momento de la atención): 15 años desde
#     la ÚLTIMA atención.
#   • HC menores (<18 años al momento de la atención): hasta que el
#     menor cumpla 25 años de edad, o 15 años desde la última atención
#     (lo que sea MAYOR, para garantizar protección hasta la mayoría
#     de edad + periodo adicional).
#   • Consentimientos informados: mismo plazo que la HC asociada.
#   • Bitácora de acceso: 5 años desde su generación.
#   • Facturas electrónicas: 5 años (art. 46 Ley 962/2005 + Estatuto
#     Tributario, art. 654).
#
# NO implementa borrado automático — es solo un módulo de CÁLCULO.
# Las acciones de disposición final las decide el responsable del
# tratamiento con base en este módulo.
#
# El módulo expone:
#   - fecha_caducidad(fecha_atencion, fecha_nacimiento) → date | None
#   - estado_retencion(fecha_atencion, fecha_nacimiento, fecha_actual)
#   - resumen_inventario(patients, fecha_actual) → dict con estadísticas
#
# Autor: NeuroSoft — 2026
# ═══════════════════════════════════════════════════════════════════════
"""
Política de retención de Historia Clínica.

Normograma aplicado:
- Resolución 1995 de 1999, art. 28: «[...] la historia clínica debe
  conservarse por un período mínimo de quince (15) años contados a
  partir de la fecha de la última atención [...]».
- Código de la Infancia y la Adolescencia (Ley 1098/2006) — protección
  reforzada a menores de edad.
- Ley 962 de 2005, art. 28: «[...] las historias clínicas se
  conservarán por un período mínimo de quince (15) años [...]».
- Estatuto Tributario, art. 654: conservación de soportes contables
  y facturas por 5 años.
- Ley 1581 de 2012, art. 11: «[...] los datos personales se
  suprimirán una vez cumplida la finalidad del tratamiento [...]».
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from typing import Iterable, List, Optional, Dict, Any


# ── Constantes ────────────────────────────────────────────────────────
ANOS_RETENCION_HC_ADULTO = 15          # Resolución 1995/1999 art. 28
EDAD_MAYORIA = 18                      # Código Civil Colombiano
ANOS_PROTECCION_POST_MAYORIA = 10      # Protección reforzada al menor
ANOS_RETENCION_LOGS_ACCESO = 5
ANOS_RETENCION_FACTURAS = 5
EDAD_MAX_REFERENCIA = 25               # Edad tope del cómputo (si se computa por edad)


@dataclass(frozen=True)
class EstadoRetencion:
    """Estado de retención de una HC individual."""

    fecha_atencion: Optional[str]   # ISO-8601 (YYYY-MM-DD)
    fecha_nacimiento: Optional[str]  # ISO-YYYY-MM-DD
    fecha_caducidad: Optional[str]  # ISO-YYYY-MM-DD
    anos_restantes: Optional[float]
    estado: str                     # "vigente" | "proximo_a_caducar" | "caducada"
    poblacion: str                  # "adulto" | "menor" | "desconocida"
    motivo: str                     # Razón legal que sustenta la decisión

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Helpers internos ─────────────────────────────────────────────────
def _parse_date(value: Any) -> Optional[date]:
    """Acepta date, datetime, o string ISO. Devuelve date o None."""
    if value is None:
        return None
    # datetime es subclase de date — chequear primero
    if isinstance(value, datetime):
        try:
            return value.date()
        except Exception:
            return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        s = value.strip()[:10]  # YYYY-MM-DD o parte inicial
        try:
            return date.fromisoformat(s)
        except ValueError:
            return None
    return None


def _edad_en_anos(fecha_nac: date, fecha_ref: date) -> Optional[int]:
    if fecha_nac is None or fecha_ref is None:
        return None
    delta = fecha_ref - fecha_nac
    return int(delta.days // 365.25)


# ── API pública ──────────────────────────────────────────────────────
def fecha_caducidad_hc(
    fecha_atencion: Any,
    fecha_nacimiento: Any,
    fecha_actual: Optional[date] = None,
) -> Optional[date]:
    """
    Calcula la fecha de caducidad de una Historia Clínica según la
    Resolución 1995/1999, art. 28.

    Regla de cálculo:
      - Si al momento de la atención el paciente era MAYOR de 18 años:
        fecha_atencion + 15 años (mínimo legal).
      - Si era MENOR de 18 años:
        max(fecha_atencion + 15 años,
            fecha_nacimiento + 25 años)  # protección reforzada.

    Returns:
        date o None si los datos son insuficientes.
    """
    fa = _parse_date(fecha_atencion)
    fn = _parse_date(fecha_nacimiento)
    if fa is None:
        return None
    if fn is None:
        # Sin fecha de nacimiento, se aplica el mínimo legal sin
        # protección reforzada (15 años).
        return fa + timedelta(days=365 * ANOS_RETENCION_HC_ADULTO)

    edad_en_atencion = _edad_en_anos(fn, fa) or 0
    if edad_en_atencion >= EDAD_MAYORIA:
        return fa + timedelta(days=365 * ANOS_RETENCION_HC_ADULTO)
    # Menor: 15 años o hasta cumplir 25, lo que sea mayor.
    cad_por_15 = fa + timedelta(days=365 * ANOS_RETENCION_HC_ADULTO)
    cad_por_25 = fn + timedelta(days=365 * EDAD_MAX_REFERENCIA)
    return max(cad_por_15, cad_por_25)


def fecha_caducidad_logs_acceso(fecha_evento: Any) -> Optional[date]:
    """
    Calcula la fecha de caducidad de un evento de la bitácora de
    acceso (Resolución 1995/1999 + Ley 1581/2012 + circular SIC).
    Retención: 5 años desde la fecha del evento.
    """
    f = _parse_date(fecha_evento)
    if f is None:
        return None
    return f + timedelta(days=365 * ANOS_RETENCION_LOGS_ACCESO)


def fecha_caducidad_factura(fecha_emision: Any) -> Optional[date]:
    """Retención de facturas: 5 años (Estatuto Tributario art. 654)."""
    f = _parse_date(fecha_emision)
    if f is None:
        return None
    return f + timedelta(days=365 * ANOS_RETENCION_FACTURAS)


def estado_retencion(
    fecha_atencion: Any,
    fecha_nacimiento: Any,
    fecha_actual: Optional[date] = None,
) -> EstadoRetencion:
    """
    Calcula el estado completo de retención de una HC.
    """
    fa = _parse_date(fecha_atencion)
    fn = _parse_date(fecha_nacimiento)
    ref = fecha_actual or date.today()

    cad = fecha_caducidad_hc(fa, fn, ref)

    if fa is None or cad is None:
        return EstadoRetencion(
            fecha_atencion=str(fa) if fa else None,
            fecha_nacimiento=str(fn) if fn else None,
            fecha_caducidad=None,
            anos_restantes=None,
            estado="desconocida",
            poblacion="desconocida",
            motivo="Datos insuficientes para calcular retención",
        )

    dias_restantes = (cad - ref).days
    anos_restantes = round(dias_restantes / 365.25, 2)

    if dias_restantes < 0:
        estado = "caducada"
    elif dias_restantes < 365 * 2:  # < 2 años
        estado = "proximo_a_caducar"
    else:
        estado = "vigente"

    edad_en_atencion = _edad_en_anos(fn, fa) if fn else None
    poblacion = (
        "menor" if (edad_en_atencion is not None and edad_en_atencion < EDAD_MAYORIA)
        else "adulto"
    )
    if poblacion == "menor":
        motivo = (
            f"Menor al momento de la atención ({edad_en_atencion} años). "
            f"Protección reforzada: 15 años desde atención o 25 años cumplidos, "
            f"lo que sea MAYOR (Res. 1995/1999 art. 28 + Ley 1098/2006)."
        )
    else:
        motivo = (
            f"Adulto al momento de la atención. Retención legal: 15 años "
            f"desde la última atención (Res. 1995/1999 art. 28)."
        )

    return EstadoRetencion(
        fecha_atencion=str(fa),
        fecha_nacimiento=str(fn) if fn else None,
        fecha_caducidad=str(cad),
        anos_restantes=anos_restantes,
        estado=estado,
        poblacion=poblacion,
        motivo=motivo,
    )


def resumen_inventario(
    patients: Iterable[Any],
    fecha_actual: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Dado un iterable de objetos (o dicts) con atributos:
      - fecha_atencion / fecha_nacimiento
    devuelve estadísticas agregadas del inventario.
    """
    ref = fecha_actual or date.today()
    estados: List[str] = []
    por_poblacion: Dict[str, int] = {"adulto": 0, "menor": 0, "desconocida": 0}
    caducadas: List[Dict[str, Any]] = []
    proximas: List[Dict[str, Any]] = []

    for p in patients:
        if isinstance(p, dict):
            fa = p.get("fecha_atencion")
            fn = p.get("fecha_nacimiento")
            pid = p.get("id") or p.get("numero_documento")
        else:
            fa = getattr(p, "fecha_atencion", None)
            fn = getattr(p, "fecha_nacimiento", None)
            pid = getattr(p, "id", None) or getattr(p, "numero_documento", None)

        e = estado_retencion(fa, fn, ref)
        estados.append(e.estado)
        por_poblacion[e.poblacion] = por_poblacion.get(e.poblacion, 0) + 1
        if e.estado == "caducada":
            caducadas.append({
                "id": pid,
                "fecha_atencion": e.fecha_atencion,
                "fecha_caducidad": e.fecha_caducidad,
            })
        elif e.estado == "proximo_a_caducar":
            proximas.append({
                "id": pid,
                "fecha_atencion": e.fecha_atencion,
                "fecha_caducidad": e.fecha_caducidad,
                "anos_restantes": e.anos_restantes,
            })

    total = len(estados)
    return {
        "fecha_referencia": str(ref),
        "total_pacientes": total,
        "vigentes": estados.count("vigente"),
        "proximo_a_caducar": estados.count("proximo_a_caducar"),
        "caducadas": estados.count("caducada"),
        "desconocidas": estados.count("desconocida"),
        "por_poblacion": por_poblacion,
        "normograma_aplicado": {
            "resolucion_1995_1999_art28": ANOS_RETENCION_HC_ADULTO,
            "proteccion_menor_anos": ANOS_PROTECCION_POST_MAYORIA,
            "edad_referencia_menor": EDAD_MAX_REFERENCIA,
            "logs_acceso_anos": ANOS_RETENCION_LOGS_ACCESO,
            "facturas_anos": ANOS_RETENCION_FACTURAS,
        },
        "caducadas_detalle": caducadas,
        "proximo_a_caducar_detalle": sorted(
            proximas, key=lambda x: x.get("fecha_caducidad") or ""
        ),
    }


__all__ = [
    "ANOS_RETENCION_HC_ADULTO",
    "EDAD_MAYORIA",
    "ANOS_PROTECCION_POST_MAYORIA",
    "ANOS_RETENCION_LOGS_ACCESO",
    "ANOS_RETENCION_FACTURAS",
    "EDAD_MAX_REFERENCIA",
    "EstadoRetencion",
    "fecha_caducidad_hc",
    "fecha_caducidad_logs_acceso",
    "fecha_caducidad_factura",
    "estado_retencion",
    "resumen_inventario",
]
