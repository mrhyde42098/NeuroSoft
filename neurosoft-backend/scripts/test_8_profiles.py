"""
scripts/test_8_profiles.py
==========================
Prueba exhaustiva con 8 perfiles clinicos distintos.
Valida que el motor de baremos no falle y que los puntajes escalares
esten en rangos clinicamente coherentes.
"""

from __future__ import annotations

import json
import sys
import traceback
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

# Path setup
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.domain.clinical_engine.baremos_loader import BaremosLoader
from app.domain.clinical_engine.engine import ClinicalEngine, PatientContext

BAREMOS_PATH = ROOT / "data" / "BD_NEURO_MAESTRA.json"

# ─────────────────────────────────────────────────────────────
# DEFINICION DE PERFILES
# Basados en inspeccion real de los baremos del JSON
# ─────────────────────────────────────────────────────────────

@dataclass
class TestProfile:
    nombre: str
    birth_date: date
    eval_date: date
    sexo: str
    escolaridad: str
    protocolo: str
    puntajes: Dict[str, float]
    descripcion: str
    expected_range: Dict[str, tuple] = field(default_factory=dict)


# Perfil 1: Nino 8 anos, Cognitivo Promedio (WISC-IV)
# Escalares ~8-12 segun baremo 803
perfil_1 = TestProfile(
    nombre="Nino 8a Promedio",
    birth_date=date(2018, 1, 15),
    eval_date=date(2026, 5, 15),
    sexo="H",
    escolaridad="Primaria Incompleta",
    protocolo="WISC-IV",
    descripcion="Perfil cognitivo promedio, escalares ~8-12",
    puntajes={
        "NiWiscDC": 21,   # Esc~10
        "NiWiscSem": 16,  # Esc~11
        "NiWiscVoc": 20,  # Esc~8
        "NiWiscLN": 14,   # Esc~10
        "NiWiscCl": 25,   # Esc~8
        "NiWiscMat": 16,  # Esc~10
        "NiWiscCom": 16,  # Esc~10
        "NiWiscAri": 14,  # Esc~7
        "NiWiscBusSim": 20,  # Esc~12
        "NiWiscRDD": 14,  # Esc~11
        "NiWiscConD": 16, # Esc~11
    },
    expected_range={
        "NiWiscDC": (7, 13), "NiWiscSem": (7, 13), "NiWiscVoc": (6, 13),
        "NiWiscLN": (7, 13), "NiWiscCl": (6, 13), "NiWiscMat": (7, 13),
        "NiWiscCom": (7, 13), "NiWiscAri": (6, 13), "NiWiscBusSim": (8, 14),
        "NiWiscRDD": (8, 14), "NiWiscConD": (8, 14),
    }
)

# Perfil 2: Nino 12 anos, Perfil TDAH (WISC-IV)
# Memoria de Trabajo baja, Velocidad de Proceso baja, CI promedio
# Escalares bajos segun baremo 1203
perfil_2 = TestProfile(
    nombre="Nino 12a TDAH",
    birth_date=date(2014, 3, 10),
    eval_date=date(2026, 5, 15),
    sexo="H",
    escolaridad="Primaria",
    protocolo="WISC-IV",
    descripcion="TDAH: MT y VP bajas, resto promedio",
    puntajes={
        "NiWiscDC": 35,   # Esc~9
        "NiWiscSem": 24,  # Esc~11
        "NiWiscVoc": 26,  # Esc~7
        "NiWiscLN": 8,    # Bajo - Esc~2
        "NiWiscCl": 28,   # Bajo - Esc~3
        "NiWiscMat": 24,  # Esc~10
        "NiWiscCom": 26,  # Esc~11
        "NiWiscAri": 10,  # Bajo - Esc~3
        "NiWiscBusSim": 18,  # Bajo - Esc~6
        "NiWiscRDD": 12,  # Esc~9
        "NiWiscConD": 24, # Esc~14
    },
    expected_range={
        "NiWiscLN": (1, 4), "NiWiscCl": (1, 5), "NiWiscAri": (1, 5),
        "NiWiscBusSim": (4, 8), "NiWiscDC": (7, 12), "NiWiscSem": (8, 14),
    }
)

# Perfil 3: Adolescente 16 anos, CI mixto (WISC-IV)
# A los 16 los baremos son muy exigentes; escalares variados
perfil_3 = TestProfile(
    nombre="Adolescente 16a Mixto",
    birth_date=date(2009, 7, 20),
    eval_date=date(2026, 5, 15),
    sexo="M",
    escolaridad="Secundaria",
    protocolo="WISC-IV",
    descripcion="CI mixto con VP baja y verbal alta",
    puntajes={
        "NiWiscDC": 40,   # Esc~7
        "NiWiscSem": 30,  # Esc~12
        "NiWiscVoc": 38,  # Esc~10
        "NiWiscLN": 20,   # Esc~13
        "NiWiscCl": 50,   # Esc~5 (baja)
        "NiWiscMat": 26,  # Esc~11
        "NiWiscCom": 32,  # Esc~13
        "NiWiscAri": 16,  # Esc~8
        "NiWiscBusSim": 55,  # Esc~14
        "NiWiscRDD": 22,  # Esc~15
        "NiWiscConD": 28, # Esc~16
    },
    expected_range={
        "NiWiscDC": (5, 10), "NiWiscSem": (10, 15), "NiWiscCl": (3, 8),
        "NiWiscLN": (10, 16), "NiWiscBusSim": (15, 19),
    }
)

# Perfil 4: Adulto joven 28 anos, Promedio (WAIS-III)
# Rango 2534: PDs medios dan escalares 8-12
perfil_4 = TestProfile(
    nombre="Adulto 28a Promedio",
    birth_date=date(1998, 1, 15),
    eval_date=date(2026, 5, 15),
    sexo="H",
    escolaridad="Profesional",
    protocolo="WAIS-III",
    descripcion="Perfil cognitivo promedio adulto joven",
    puntajes={
        "AdWAISV": 55,    # Esc~11
        "AdSemWais": 22,  # Esc~11
        "AdWAISC": 24,    # Esc~12
        "AdWAISI": 16,    # Esc~10
        "AdWAISA": 14,    # Esc~11
        "AdWAISL": 10,    # Esc~10
        "AdSDWais": 75,   # Esc~9
        "AdMatr": 15,     # Esc~7
        "AdWAISFI": 16,   # Esc~7
        "AdWAISCC": 26,   # Esc~6
        "AdDDir": 10,     # Esc~7
    },
    expected_range={
        "AdWAISV": (10, 15), "AdSemWais": (8, 13), "AdWAISC": (8, 14),
        "AdSDWais": (7, 12), "AdMatr": (6, 11), "AdDDir": (4, 8),
    }
)

# Perfil 5: Adulto joven 42 anos, Deterioro leve (WAIS-III)
# Rango 3554: PDs bajos dan escalares 4-8
perfil_5 = TestProfile(
    nombre="Adulto 42a Deterioro",
    birth_date=date(1984, 3, 10),
    eval_date=date(2026, 5, 15),
    sexo="M",
    escolaridad="Secundaria",
    protocolo="WAIS-III",
    descripcion="Deterioro leve, memoria y atencion bajas",
    puntajes={
        "AdWAISV": 45,    # Esc~9
        "AdSemWais": 16,  # Esc~9
        "AdWAISC": 18,    # Esc~9
        "AdWAISI": 12,    # Esc~8
        "AdWAISA": 10,    # Esc~9
        "AdWAISL": 6,     # Bajo - Esc~7
        "AdSDWais": 55,   # Esc~7
        "AdMatr": 10,     # Esc~6
        "AdWAISFI": 12,   # Esc~6
        "AdWAISCC": 20,   # Esc~5
        "AdDDir": 6,      # Limite - Esc~5
    },
    expected_range={
        "AdWAISL": (5, 9), "AdSDWais": (5, 9), "AdMatr": (4, 8),
        "AdDDir": (4, 7), "AdWAISCC": (3, 7),
    }
)

# Perfil 6: Adulto mayor 65 anos, Normal (Neuronorma AM)
# Rango 6365: valores tipicos
perfil_6 = TestProfile(
    nombre="AM 65a Normal",
    birth_date=date(1961, 3, 20),
    eval_date=date(2026, 5, 15),
    sexo="H",
    escolaridad="Secundaria",
    protocolo="Adulto Mayor",
    descripcion="Adulto mayor con funcion cognitiva normal para edad",
    puntajes={
        "ViTMTA": 80,     # Esc~7
        "ViTMTB": 180,    # Esc~7
        "ViRDD": 8,       # Esc~16
        "ViRDInv": 5,     # Esc~15
        "ViStP": 45,      # Esc~3
        "ViStC": 30,      # Esc~3
        "ViAni": 18,      # Esc~10
        "ViSem": 22,      # Esc~22 (ci? check)
        "ViYesavage": 3,  # Esc~3
    },
    expected_range={
        "ViTMTA": (5, 10), "ViTMTB": (5, 10), "ViRDD": (13, 19),
        "ViRDInv": (12, 18), "ViStP": (2, 6), "ViAni": (7, 13),
    }
)

# Perfil 7: Adulto mayor 78 anos, Deterioro moderado (Neuronorma AM)
# Rango 7880
perfil_7 = TestProfile(
    nombre="AM 78a Deterioro",
    birth_date=date(1948, 1, 10),
    eval_date=date(2026, 5, 15),
    sexo="M",
    escolaridad="Primaria Completa",
    protocolo="Adulto Mayor",
    descripcion="Deterioro cognitivo moderado, edad avanzada",
    puntajes={
        "ViTMTA": 121,    # Esc~8
        "ViTMTB": 281,    # Esc~9
        "ViRDD": 4,       # Esc~10
        "ViRDInv": 2,     # Esc~8
        "ViStP": 26,      # Esc~3
        "ViStC": 16,      # Esc~3
        "ViAni": 11,      # Esc~10
        "ViSem": 14,      # Esc~14
        "ViYesavage": 8,  # Esc~8
    },
    expected_range={
        "ViTMTA": (6, 11), "ViTMTB": (7, 12), "ViRDD": (7, 13),
        "ViRDInv": (5, 11), "ViStP": (2, 6), "ViAni": (7, 13),
    }
)

# Perfil 8: Adulto mayor 82 anos, Analfabeta (Neuronorma AM)
# Rango 8190: con ajuste escolaridad (+N al PD)
perfil_8 = TestProfile(
    nombre="AM 82a Analfabeta",
    birth_date=date(1944, 2, 5),
    eval_date=date(2026, 5, 15),
    sexo="H",
    escolaridad="Analfabeta",
    protocolo="Adulto Mayor",
    descripcion="Adulto mayor analfabeta, requiere ajuste escolaridad",
    puntajes={
        "ViTMTA": 150,    # Esc~8 (con ajuste PD aumenta)
        "ViTMTB": 300,    # Esc~8
        "ViRDD": 3,       # Esc~6 -> con ajuste +2 = PD 5 -> Esc~13
        "ViRDInv": 1,     # Esc~8 -> con ajuste +2 = PD 3 -> Esc~12
        "ViStP": 20,      # Esc~4
        "ViStC": 10,      # Esc~4
        "ViAni": 10,      # Esc~9
        "ViSem": 10,      # Esc~10
        "ViYesavage": 5,  # Esc~5
    },
    expected_range={
        "ViTMTA": (6, 11), "ViTMTB": (6, 11), "ViRDD": (10, 16),
        "ViRDInv": (8, 14), "ViStP": (2, 7), "ViAni": (6, 12),
    }
)

PERFILES = [perfil_1, perfil_2, perfil_3, perfil_4, perfil_5, perfil_6, perfil_7, perfil_8]


# ─────────────────────────────────────────────────────────────
# VALIDADORES
# ─────────────────────────────────────────────────────────────

class ValidationError:
    def __init__(self, perfil: str, test_id: str, msg: str, detalle: Any = None):
        self.perfil = perfil
        self.test_id = test_id
        self.msg = msg
        self.detalle = detalle


def validar_rango_escalar(r, perfil: TestProfile) -> Optional[ValidationError]:
    """Verifica que el escalar este dentro del rango esperado."""
    if r.test_id not in perfil.expected_range:
        return None
    min_e, max_e = perfil.expected_range[r.test_id]
    escalar = r.puntaje_escalar
    if escalar is None:
        return ValidationError(perfil.nombre, r.test_id,
                               f"Escalar es None (PD={r.puntaje_bruto}, llave={r.llave_baremo_usada})")
    if not (min_e <= escalar <= max_e):
        return ValidationError(perfil.nombre, r.test_id,
                               f"Escalar {escalar} fuera de rango esperado [{min_e}, {max_e}]",
                               {"escalar": escalar, "pd": r.puntaje_bruto,
                                "llave": r.llave_baremo_usada, "interp": r.interpretacion})
    return None


def validar_consistencia_interpretacion(r) -> Optional[ValidationError]:
    """Verifica que interpretacion coincida con escalar."""
    escalar = r.puntaje_escalar
    interp = r.interpretacion
    if escalar is None:
        return None
    if r.tipo_metrica == "escalar":
        if escalar <= 4 and interp != "Bajo":
            return ValidationError("", r.test_id, f"Inconsistencia: escalar={escalar} -> interp={interp}")
        if 5 <= escalar <= 6 and interp != "Limítrofe":
            return ValidationError("", r.test_id, f"Inconsistencia: escalar={escalar} -> interp={interp}")
        if 7 <= escalar <= 12 and interp != "Promedio":
            return ValidationError("", r.test_id, f"Inconsistencia: escalar={escalar} -> interp={interp}")
        if escalar >= 13 and interp != "Superior":
            return ValidationError("", r.test_id, f"Inconsistencia: escalar={escalar} -> interp={interp}")
    return None


# ─────────────────────────────────────────────────────────────
# EJECUCION PRINCIPAL
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("NEUROSOFT - VALIDACION EXHAUSTIVA: 8 PERFILES CLINICOS")
    print("=" * 70)

    if not BAREMOS_PATH.exists():
        print(f"ERROR: No se encontro {BAREMOS_PATH}")
        sys.exit(1)

    loader = BaremosLoader.load(BAREMOS_PATH)
    engine = ClinicalEngine(loader=loader)

    errores: List[ValidationError] = []
    warnings: List[ValidationError] = []
    resultados_por_perfil: Dict[str, Any] = {}

    for perfil in PERFILES:
        print(f"\n{'-' * 70}")
        print(f"PERFIL: {perfil.nombre}")
        print(f"  Edad: {(perfil.eval_date - perfil.birth_date).days // 365.25:.1f}a")
        print(f"  Sexo: {perfil.sexo}, Escolaridad: {perfil.escolaridad}")
        print(f"  Protocolo: {perfil.protocolo}")
        print(f"  Descripcion: {perfil.descripcion}")
        print(f"  Pruebas: {len(perfil.puntajes)}")

        ctx = PatientContext.from_demographics(
            birth_date=perfil.birth_date,
            evaluation_date=perfil.eval_date,
            sexo=perfil.sexo,
            escolaridad=perfil.escolaridad,
        )

        try:
            result = engine.score(
                paciente_id=f"test-{perfil.nombre.replace(' ', '_').lower()}",
                puntajes=perfil.puntajes,
                patient_context=ctx,
                protocolo=perfil.protocolo,
            )
        except Exception as exc:
            print(f"  [X] EXCEPCION en engine.score(): {exc}")
            traceback.print_exc()
            errores.append(ValidationError(perfil.nombre, "ENGINE",
                                           f"Excepcion: {exc}", str(exc)))
            continue

        print(f"  [OK] Engine OK - {result.pruebas_realizadas} realizadas, "
              f"{result.pruebas_sin_dato} sin dato, {len(result.advertencias)} advertencias")

        if result.advertencias:
            for adv in result.advertencias:
                print(f"     [WARN] {adv}")
                warnings.append(ValidationError(perfil.nombre, "ADV", adv))

        perfil_resultados = []
        for r in result.resultados:
            line = (f"     {r.test_id:20s} PD={r.puntaje_bruto:6.1f}  "
                    f"Esc={r.puntaje_escalar!s:>6s}  {r.interpretacion:12s}  "
                    f"({r.dominio_cognitivo})")
            print(line)
            perfil_resultados.append({
                "test_id": r.test_id, "nombre": r.test_nombre,
                "pd": r.puntaje_bruto, "escalar": r.puntaje_escalar,
                "interpretacion": r.interpretacion, "dominio": r.dominio_cognitivo,
                "llave": r.llave_baremo_usada, "metadata": r.metadata,
            })

            err = validar_rango_escalar(r, perfil)
            if err:
                errores.append(err)
                print(f"     [X] ERROR: {err.msg}")

            err2 = validar_consistencia_interpretacion(r)
            if err2:
                errores.append(err2)
                print(f"     [X] ERROR: {err2.msg}")

        # Verificar indices CI si es WISC-IV o WAIS-III
        if perfil.protocolo in ("WISC-IV", "WAIS-III"):
            indices = [r for r in result.resultados if r.test_id.startswith(("NiWISCInd", "NiWISCTot", "AdWAISIC", "AdWASIE"))]
            if indices:
                print(f"     [STAT] Indices CI:")
                for idx in indices:
                    print(f"         {idx.test_id}: {idx.puntaje_escalar} ({idx.interpretacion})")

        resultados_por_perfil[perfil.nombre] = {
            "poblacion": result.poblacion,
            "edad_display": result.edad_display,
            "pruebas_realizadas": result.pruebas_realizadas,
            "advertencias": result.advertencias,
            "resultados": perfil_resultados,
        }

    # ─────────────────────────────────────────────────────────
    # RESUMEN
    # ─────────────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print("RESUMEN DE VALIDACION")
    print(f"{'=' * 70}")
    print(f"Perfiles probados: {len(PERFILES)}")
    print(f"Errores criticos: {len([e for e in errores if 'Excepcion' in e.msg])}")
    print(f"Errores de validacion: {len([e for e in errores if 'Excepcion' not in e.msg])}")
    print(f"Advertencias del engine: {len(warnings)}")

    if errores:
        print(f"\n{'-' * 70}")
        print("DETALLE DE ERRORES:")
        for e in errores:
            print(f"  • [{e.perfil}] {e.test_id}: {e.msg}")
            if e.detalle:
                print(f"    Detalle: {e.detalle}")
    else:
        print("\n[OK] No se encontraron errores de validacion.")

    # Guardar reporte JSON
    report_path = ROOT / "scripts" / "test_8_profiles_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "resumen": {
                "perfiles": len(PERFILES),
                "errores": len(errores),
                "advertencias": len(warnings),
            },
            "errores": [{"perfil": e.perfil, "test": e.test_id, "msg": e.msg,
                         "detalle": e.detalle} for e in errores],
            "advertencias": [{"perfil": e.perfil, "msg": e.msg} for e in warnings],
            "resultados": resultados_por_perfil,
        }, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n[FILE] Reporte guardado en: {report_path}")

    return len(errores)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
