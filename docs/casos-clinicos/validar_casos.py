"""
validar_casos.py
================
Ejecuta el motor de scoring REAL contra los 15 casos clínicos colombianos.
Genera un reporte con escalares reales para que CASOS_GROUND_TRUTH.md
se reescriba con valores validados (no aspiracionales).

Uso:
    cd D:\\NeuroSoftApp\\neurosoft-backend
    venv\\Scripts\\python ..\\docs\\casos-clinicos\\validar_casos.py

Salida:
    docs/casos-clinicos/RESULTADOS_VALIDACION.json (machine-readable)
    + impresión legible por consola
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Asegurar que el backend esté en el path
BACKEND = Path(__file__).resolve().parents[2] / "neurosoft-backend"
sys.path.insert(0, str(BACKEND))

from datetime import date as _date

from app.core.config import settings
from app.domain.clinical_engine.baremos_loader import BaremosLoader
from app.domain.clinical_engine.engine import ClinicalEngine, PatientContext

# Cargar baremos una sola vez
loader = BaremosLoader.load(settings.baremo_path)
engine = ClinicalEngine(loader)

# ─── Los 15 casos ──────────────────────────────────────────────────────
CASOS = [
    {
        "id": 3, "nombre": "Sebastián Castillo Gómez",
        "perfil": "TDAH combinado infantil",
        "fecha_nacimiento": "2017-01-15", "fecha_evaluacion": "2025-05-10",
        "sexo": "M", "escolaridad": "Primaria",
        "puntajes": {
            "NiWiscDC": 30, "NiWiscSem": 18, "NiWiscRDD": 11, "NiWiscCl": 22,
            "NiWiscVoc": 30, "NiWiscLN": 11, "NiWiscMat": 17, "NiWiscCom": 18,
            "NiWiscBusSim": 10, "NiWiscAri": 14,
        },
    },
    {
        "id": 4, "nombre": "Valentina Ospina Marín",
        "perfil": "Dislexia evolutiva",
        "fecha_nacimiento": "2014-10-22", "fecha_evaluacion": "2025-05-19",
        "sexo": "F", "escolaridad": "Primaria",
        "puntajes": {
            "NiWiscDC": 32, "NiWiscSem": 24, "NiWiscVoc": 35, "NiWiscConD": 17,
            "NiWiscCl": 50, "NiWiscMat": 21, "NiWiscBusSim": 30,
            "NiPrec": 8, "NiLVS": 2, "NiCopTxt": 14,
        },
    },
    {
        "id": 5, "nombre": "Mateo Quintero Salazar",
        "perfil": "TEA nivel 1",
        "fecha_nacimiento": "2019-03-08", "fecha_evaluacion": "2025-05-12",
        "sexo": "M", "escolaridad": "Primaria",
        "puntajes": {
            # Perfil cognitivo alto en TEA nivel 1 (CI promedio-alto, déficit en cognición social)
            "NiWiscDC": 24, "NiWiscVoc": 28, "NiWiscSem": 16, "NiWiscMat": 18,
            "NiWiscCl": 22,
            # NiRecEmo: bajar PD para mostrar déficit de cognición social
            "NiRecEmo": 2,
        },
    },
    {
        "id": 6, "nombre": "Isabella Mendoza Ariza",
        "perfil": "Discapacidad intelectual leve",
        "fecha_nacimiento": "2011-09-25", "fecha_evaluacion": "2025-05-20",
        "sexo": "F", "escolaridad": "Primaria",
        "puntajes": {
            "NiWiscDC": 20, "NiWiscSem": 11, "NiWiscRDD": 9, "NiWiscConD": 9,
            "NiWiscCl": 35, "NiWiscVoc": 18, "NiWiscLN": 8, "NiWiscMat": 11,
            "NiWiscCom": 11, "NiWiscBusSim": 12,
        },
    },
    {
        "id": 7, "nombre": "Daniel Jaramillo Vásquez",
        "perfil": "TEPT infantil",
        "fecha_nacimiento": "2015-12-05", "fecha_evaluacion": "2025-05-15",
        "sexo": "M", "escolaridad": "Primaria",
        "puntajes": {
            "NiWiscDC": 24, "NiWiscSem": 16, "NiWiscRDD": 10, "NiWiscCl": 35,
            "NiWiscVoc": 23, "NiWiscLN": 9, "NiWiscMat": 15, "NiWiscCom": 14,
            # NiSt_Edades: el "PD" del baremo es escalar 0-52 según edad.
            # Para edad 9 valores válidos son [41,29,20] — uso 20 (bajo, TEPT).
            "NiSt_Edades": 20,
        },
    },
    # NOTA importante (post-validación 2026-05-19): AdTMTA/AdTMTB/FluidP NO tienen
    # baremo para adulto joven (rango aplicable: 50+). Para casos 8-12 (adultos
    # jóvenes) se sustituyen por AdTMT_AB (z_score), que es la prueba TMT real
    # para adulto joven en el catálogo.
    {
        "id": 8, "nombre": "Carolina Pineda Restrepo",
        "perfil": "Depresión mayor con queja cognitiva",
        "fecha_nacimiento": "2001-05-12", "fecha_evaluacion": "2025-05-15",
        "sexo": "F", "escolaridad": "Universitaria",
        "puntajes": {
            "AdWAISV": 48, "AdSemWais": 21, "AdSDWais": 70, "AdDDir": 9,
            "AdMatr": 21, "AdWAISFI": 19,
            "AdTMT_AB": 90,  # tiempo TMT (z_score)
            "AdBeck": 32,
        },
    },
    {
        "id": 9, "nombre": "Juan Pablo Velandia Rojas",
        "perfil": "Secuelas cognitivas TCE moderado",
        "fecha_nacimiento": "1993-12-10", "fecha_evaluacion": "2025-05-18",
        "sexo": "M", "escolaridad": "Secundaria",
        "puntajes": {
            "AdWAISV": 42, "AdSemWais": 19, "AdSDWais": 50, "AdDDir": 9,
            "AdMatr": 17, "AdWAISCC": 28,
            "AdTMT_AB": 130,  # tiempo lentificado por TCE
            "AdStroop_Corr": 28,
        },
    },
    {
        "id": 10, "nombre": "Camila Herrera Gómez",
        "perfil": "Ansiedad generalizada",
        "fecha_nacimiento": "2002-06-18", "fecha_evaluacion": "2025-05-18",
        "sexo": "F", "escolaridad": "Universitaria",
        "puntajes": {
            "AdWAISV": 48, "AdSemWais": 24, "AdSDWais": 75, "AdDDir": 11,
            "AdMatr": 21,
            "AdTMT_AB": 75,
            "AdStroop_Corr": 42,
            "EscSTAI": 55,
        },
    },
    {
        "id": 11, "nombre": "Andrés Mauricio Torres",
        "perfil": "TDAH adulto",
        "fecha_nacimiento": "1996-10-22", "fecha_evaluacion": "2025-05-18",
        "sexo": "M", "escolaridad": "Universitaria",
        "puntajes": {
            "AdWAISV": 50, "AdSemWais": 25, "AdSDWais": 65, "AdDDir": 9,
            "AdMatr": 21,
            "AdTMT_AB": 110,  # TMT lentificado en TDAH
            "AdStroop_Corr": 30,
            "EscASRS": 42,
        },
    },
    {
        "id": 12, "nombre": "Diana Camila Suárez Pérez",
        "perfil": "Duelo complicado + depresión mayor",
        "fecha_nacimiento": "1990-02-15", "fecha_evaluacion": "2025-05-19",
        "sexo": "F", "escolaridad": "Universitaria",
        "puntajes": {
            "AdWAISV": 48, "AdSemWais": 22, "AdSDWais": 65, "AdDDir": 9,
            "AdMatr": 19,
            "AdTMT_AB": 100,
            "AdBeck": 28,
        },
    },
    {
        "id": 13, "nombre": "Hernando Restrepo Villegas",
        "perfil": "Deterioro Cognitivo Leve amnésico",
        "fecha_nacimiento": "1953-01-08", "fecha_evaluacion": "2025-05-15",
        "sexo": "M", "escolaridad": "Universitaria",
        "puntajes": {
            "ViRDD": 6, "ViRDInv": 4, "ViTMTA": 60, "ViTMTB": 145, "ViStP": 95,
            "ViGroberRLT": 18, "ViGroberML_Tot": 8,
            # ViGroberMC_Tot rango máximo 16 — bajado de 28 a 14 para que esté dentro de baremo
            "ViGroberMC_Tot": 14,
            "ViAni": 16, "ViYesavage": 2,
        },
    },
    {
        "id": 14, "nombre": "Rosa Inés Cárdenas Mejía",
        "perfil": "Enfermedad de Alzheimer leve",
        "fecha_nacimiento": "1948-08-05", "fecha_evaluacion": "2025-05-12",
        "sexo": "F", "escolaridad": "Primaria",
        "puntajes": {
            "ViRDD": 3, "ViRDInv": 2, "ViTMTA": 280, "ViStP": 60,
            "ViGroberRLT": 4, "ViGroberML_Tot": 1, "ViGroberMC_Tot": 8,
            "ViAni": 8, "FluidP": 4, "Denom48": 28, "ViYesavage": 4,
        },
    },
    {
        "id": 15, "nombre": "Luis Eduardo Pérez Quintero",
        "perfil": "Pseudodemencia depresiva",
        "fecha_nacimiento": "1957-04-18", "fecha_evaluacion": "2025-05-18",
        "sexo": "M", "escolaridad": "Secundaria",
        "puntajes": {
            "ViRDD": 5, "ViRDInv": 3, "ViTMTA": 110, "ViStP": 75,
            "ViGroberRLT": 22, "ViGroberML_Tot": 9,
            # ViGroberMC_Tot rango máx 16 — bajado de 32 a 14
            "ViGroberMC_Tot": 14,
            "ViAni": 14, "ViYesavage": 11,
        },
    },
    {
        "id": 16, "nombre": "Magdalena Sánchez Tobón",
        "perfil": "Parkinson con deterioro cognitivo",
        "fecha_nacimiento": "1954-07-02", "fecha_evaluacion": "2025-05-19",
        "sexo": "F", "escolaridad": "Primaria Incompleta",
        "puntajes": {
            # ViTMTA rango máx 265 para banda 6971 — bajado a 260 (con +2 ajuste = 262)
            "ViRDD": 4, "ViRDInv": 2, "ViTMTA": 260, "ViTMTB": 600, "ViStP": 50,
            "ViGroberRLT": 15, "ViGroberML_Tot": 5,
            # ViGroberMC_Tot rango máx 16 — bajado de 28 a 12
            "ViGroberMC_Tot": 12,
            "ViAni": 9, "FluidP": 6, "ViYesavage": 4,
        },
    },
    {
        "id": 17, "nombre": "José Antonio Bermúdez Caro",
        "perfil": "Control normal (envejecimiento típico)",
        "fecha_nacimiento": "1960-02-10", "fecha_evaluacion": "2025-05-12",
        "sexo": "M", "escolaridad": "Universitaria",
        "puntajes": {
            "ViRDD": 7, "ViRDInv": 5, "ViTMTA": 45, "ViTMTB": 110, "ViStP": 110,
            "ViGroberRLT": 30, "ViGroberML_Tot": 14,
            # ViGroberMC_Tot rango máx 16 — bajado de 36 a 16 (control normal alto)
            "ViGroberMC_Tot": 16,
            "ViAni": 22, "FluidP": 18, "ViYesavage": 1,
        },
    },
]


def run_caso(caso: dict) -> dict:
    """Ejecuta el motor real sobre un caso y devuelve el resultado."""
    fn = _date.fromisoformat(caso["fecha_nacimiento"])
    fe = _date.fromisoformat(caso["fecha_evaluacion"])
    ctx = PatientContext.from_demographics(
        birth_date=fn,
        evaluation_date=fe,
        sexo=caso["sexo"],
        escolaridad=caso["escolaridad"],
    )
    result = engine.score(
        paciente_id=f"caso_{caso['id']}",
        puntajes=caso["puntajes"],
        patient_context=ctx,
    )
    out_pruebas = []
    for r in result.resultados:
        out_pruebas.append({
            "test_id": r.test_id,
            "test_nombre": r.test_nombre,
            "pd": r.puntaje_bruto,
            "escalar_real": r.puntaje_escalar,
            "tipo_metrica": r.tipo_metrica,
            "interpretacion": r.interpretacion,
            "z_equivalente": r.z_equivalente,
            "llave_usada": r.llave_baremo_usada,
            "metadata": dict(r.metadata) if r.metadata else {},
        })
    return {
        "caso_id": caso["id"],
        "nombre": caso["nombre"],
        "perfil_objetivo": caso["perfil"],
        "edad_calculada": ctx.age.display,
        "poblacion": ctx.poblacion,
        "puntajes_input": caso["puntajes"],
        "resultados": out_pruebas,
        "puntos_fuertes": result.puntos_fuertes,
        "puntos_debiles": result.puntos_debiles,
        "advertencias": result.advertencias,
    }


def main():
    # Fuerza UTF-8 en stdout para Windows (cp1252 rompe con ✓ ❌ ⚠).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(f"Cargados {loader.total_pruebas} pruebas en baremo")
    print(f"Validando {len(CASOS)} casos…\n")

    salida = []
    for caso in CASOS:
        try:
            r = run_caso(caso)
            salida.append(r)
            print(f"━━━ Caso {r['caso_id']:>2}: {r['nombre']} ({r['perfil_objetivo']}) ━━━")
            print(f"     Edad: {r['edad_calculada']} · Población: {r['poblacion']}")
            print(f"     {'Test':<18} {'PD':>6} {'Escalar':>8} {'Interpr.':<15} {'Llave':<14}")
            for p in r["resultados"]:
                esc = p['escalar_real']
                esc_str = f"{esc:.1f}" if isinstance(esc, (int, float)) else str(esc)
                interp = (p['interpretacion'] or "—")[:15]
                llave = (p['llave_usada'] or "—")[:14]
                print(f"     {p['test_id']:<18} {p['pd']:>6.0f} {esc_str:>8} {interp:<15} {llave:<14}")
            if r["advertencias"]:
                print(f"     ⚠ Advertencias: {r['advertencias']}")
            print()
        except Exception as e:
            print(f"❌ Caso {caso['id']} falló: {type(e).__name__}: {e}")
            salida.append({"caso_id": caso["id"], "error": str(e)})

    out_path = Path(__file__).parent / "RESULTADOS_VALIDACION.json"
    out_path.write_text(
        json.dumps(salida, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n✓ JSON detallado en: {out_path}")


if __name__ == "__main__":
    main()
