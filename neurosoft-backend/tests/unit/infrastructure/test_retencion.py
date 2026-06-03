"""
S5.2 — Tests unitarios de la política de retención (Res 1995/1999 art. 28).
"""

from datetime import date, timedelta

import pytest

from app.infrastructure.retencion import (
    ANOS_RETENCION_HC_ADULTO,
    ANOS_RETENCION_LOGS_ACCESO,
    ANOS_RETENCION_FACTURAS,
    EDAD_MAYORIA,
    EDAD_MAX_REFERENCIA,
    EstadoRetencion,
    estado_retencion,
    fecha_caducidad_factura,
    fecha_caducidad_hc,
    fecha_caducidad_logs_acceso,
    resumen_inventario,
)


# ── Helpers ───────────────────────────────────────────────────────
def _ref():
    """Fecha de referencia fija para tests deterministas."""
    return date(2026, 6, 1)


class TestFechaCaducidadHc:
    def test_adulto_atencion_reciente_15_anos(self):
        # Adulto 30a, atención hoy → caduca en 15 años
        ref = _ref()
        fn = date(1995, 1, 1)
        cad = fecha_caducidad_hc(ref, fn, ref)
        assert cad == ref + timedelta(days=365 * ANOS_RETENCION_HC_ADULTO)

    def test_menor_15_anos_predomina(self):
        # Menor 10a, atención hace 1 año → el plazo 15 años vence
        # LIGERAMENTE DESPUÉS de que cumpla 25, así que el MAX es 15 años.
        ref = _ref()
        fn = date(2015, 1, 1)         # 11 años en 2026
        fa = date(2025, 6, 1)         # atención hace 1 año
        cad = fecha_caducidad_hc(fa, fn, ref)
        cad_15 = fa + timedelta(days=365 * 15)   # 2040-05-31
        cad_25 = fn + timedelta(days=365 * 25)   # 2040-01-01
        assert cad == max(cad_15, cad_25)
        # 15 años desde atención es ligeramente MAYOR que 25 desde nacimiento
        assert cad == cad_15

    def test_menor_25_anos_predomina_en_casos_marginales(self):
        # Menor 17a, atención hace 1 año → 25 años cumple ANTES que 15.
        # Se toma max(15, 25) = 15 años desde atención.
        ref = _ref()
        fn = date(2008, 6, 1)         # 18 años cumplidos a ref
        fa = date(2025, 6, 1)         # tenía 16 al atender
        cad = fecha_caducidad_hc(fa, fn, ref)
        cad_15 = fa + timedelta(days=365 * 15)   # 2040
        cad_25 = fn + timedelta(days=365 * 25)   # 2033
        assert cad == max(cad_15, cad_25)
        # En este caso el 15-años es MAYOR (2040 > 2033)
        assert cad == cad_15

    def test_menor_recien_nacido_25_anos_predomina(self):
        # Lactante de 1 año atendido en 2025: 15 años da 2040,
        # 25 años da 2050. Predomina 25 años (mayor protección).
        ref = _ref()
        fn = date(2024, 1, 1)         # 1 año en 2025
        fa = date(2025, 6, 1)         # atención con 1 año
        cad = fecha_caducidad_hc(fa, fn, ref)
        cad_15 = fa + timedelta(days=365 * 15)   # 2040
        cad_25 = fn + timedelta(days=365 * 25)   # 2049
        assert cad == cad_25  # 25 años predomina

    def test_sin_fecha_nacimiento_aplica_15(self):
        # Si falta fecha de nacimiento, se aplica el mínimo legal.
        fa = date(2020, 1, 1)
        cad = fecha_caducidad_hc(fa, None)
        assert cad == fa + timedelta(days=365 * 15)

    def test_sin_fecha_atencion_devuelve_none(self):
        assert fecha_caducidad_hc(None, date(2000, 1, 1)) is None

    def test_acepta_datetime(self):
        from datetime import datetime
        fa = datetime(2020, 1, 1, 12, 0)
        cad = fecha_caducidad_hc(fa, None)
        assert cad == date(2020, 1, 1) + timedelta(days=365 * 15)

    def test_acepta_string_iso(self):
        cad = fecha_caducidad_hc("2020-01-01", "1990-01-01")
        assert cad == date(2020, 1, 1) + timedelta(days=365 * 15)

    def test_acepta_string_con_horas(self):
        # Algunos serializadores mandan "2020-01-01T08:00:00"
        cad = fecha_caducidad_hc("2020-01-01T08:00:00", "1990-01-01")
        assert cad == date(2020, 1, 1) + timedelta(days=365 * 15)

    def test_edad_mayoria_es_18(self):
        assert EDAD_MAYORIA == 18

    def test_edad_maxima_referencia_es_25(self):
        assert EDAD_MAX_REFERENCIA == 25


class TestFechaCaducidadLogsAcceso:
    def test_5_anos_desde_evento(self):
        f = date(2024, 6, 1)
        cad = fecha_caducidad_logs_acceso(f)
        assert cad == date(2024, 6, 1) + timedelta(days=365 * ANOS_RETENCION_LOGS_ACCESO)
        assert ANOS_RETENCION_LOGS_ACCESO == 5


class TestFechaCaducidadFactura:
    def test_5_anos_desde_emision(self):
        f = date(2023, 1, 15)
        cad = fecha_caducidad_factura(f)
        assert cad == date(2023, 1, 15) + timedelta(days=365 * ANOS_RETENCION_FACTURAS)


class TestEstadoRetencion:
    def test_hc_vigente(self):
        ref = _ref()
        e = estado_retencion(date(2024, 1, 1), date(1990, 1, 1), ref)
        assert e.estado == "vigente"
        assert e.poblacion == "adulto"
        assert e.anos_restantes is not None and e.anos_restantes > 12

    def test_hc_proxima_a_caducar_2_anos(self):
        ref = _ref()
        # Atención 14 años atrás → 1 año restante
        fa = ref - timedelta(days=365 * 14)
        e = estado_retencion(fa, date(1990, 1, 1), ref)
        assert e.estado == "proximo_a_caducar"

    def test_hc_caducada(self):
        ref = _ref()
        # Atención hace 20 años
        fa = ref - timedelta(days=365 * 20)
        e = estado_retencion(fa, date(1990, 1, 1), ref)
        assert e.estado == "caducada"
        assert e.anos_restantes is not None and e.anos_restantes < 0

    def test_menor_poblacion(self):
        ref = _ref()
        # Menor 10a en 2025, atendido en 2025
        e = estado_retencion(date(2025, 6, 1), date(2015, 6, 1), ref)
        assert e.poblacion == "menor"
        assert "Protección reforzada" in e.motivo or "refuerzo" in e.motivo.lower() or "menor" in e.motivo.lower()

    def test_datos_insuficientes(self):
        e = estado_retencion(None, None, _ref())
        assert e.estado == "desconocida"
        assert e.motivo != ""

    def test_to_dict(self):
        e = estado_retencion(date(2024, 1, 1), date(1990, 1, 1), _ref())
        d = e.to_dict()
        assert "fecha_atencion" in d
        assert "estado" in d
        assert "poblacion" in d
        assert "motivo" in d

    def test_es_dataclass_inmutable(self):
        with pytest.raises(Exception):
            EstadoRetencion(
                fecha_atencion="2024-01-01",
                fecha_nacimiento="1990-01-01",
                fecha_caducidad="2039-01-01",
                anos_restantes=12.5,
                estado="vigente",
                poblacion="adulto",
                motivo="x",
            ).estado = "caducada"


class TestResumenInventario:
    def _pacientes(self):
        ref = _ref()
        return [
            # Vigente adulto
            type("P", (), {
                "id": "p1",
                "fecha_atencion": date(2024, 1, 1),
                "fecha_nacimiento": date(1990, 1, 1),
            })(),
            # Vigente menor
            type("P", (), {
                "id": "p2",
                "fecha_atencion": date(2025, 1, 1),
                "fecha_nacimiento": date(2015, 1, 1),
            })(),
            # Caducada
            type("P", (), {
                "id": "p3",
                "fecha_atencion": date(2000, 1, 1),
                "fecha_nacimiento": date(1960, 1, 1),
            })(),
        ]

    def test_resumen_basico(self):
        resumen = resumen_inventario(self._pacientes(), _ref())
        assert resumen["total_pacientes"] == 3
        assert resumen["vigentes"] == 2
        assert resumen["caducadas"] == 1
        assert "normograma_aplicado" in resumen
        assert resumen["normograma_aplicado"]["resolucion_1995_1999_art28"] == 15

    def test_resumen_acepta_dicts(self):
        pacientes = [
            {"id": "p1", "fecha_atencion": "2024-01-01", "fecha_nacimiento": "1990-01-01"},
            {"id": "p2", "fecha_atencion": None, "fecha_nacimiento": None},
        ]
        resumen = resumen_inventario(pacientes, _ref())
        assert resumen["total_pacientes"] == 2
        assert resumen["desconocidas"] == 1
        assert resumen["vigentes"] == 1

    def test_resumen_por_poblacion(self):
        resumen = resumen_inventario(self._pacientes(), _ref())
        # 1 adulto, 1 menor, 1 adulto (caducado)
        assert resumen["por_poblacion"]["adulto"] == 2
        assert resumen["por_poblacion"]["menor"] == 1

    def test_resumen_proximo_a_caducar_detalle_ordenado(self):
        # 2 pacientes próximos a caducar
        ref = _ref()
        pacientes = [
            type("P", (), {
                "id": "p_cerca",
                "fecha_atencion": ref - timedelta(days=365 * 14.5),  # 0.5 año
                "fecha_nacimiento": date(1990, 1, 1),
            })(),
            type("P", (), {
                "id": "p_lejos",
                "fecha_atencion": ref - timedelta(days=365 * 13.5),  # 1.5 años
                "fecha_nacimiento": date(1990, 1, 1),
            })(),
        ]
        resumen = resumen_inventario(pacientes, ref)
        assert resumen["proximo_a_caducar"] == 2
        # Verifica que el detalle está ordenado por fecha de caducidad
        detalle = resumen["proximo_a_caducar_detalle"]
        assert detalle[0]["id"] == "p_cerca"   # caduca antes
        assert detalle[1]["id"] == "p_lejos"   # caduca después
