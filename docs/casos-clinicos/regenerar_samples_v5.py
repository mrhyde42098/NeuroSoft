"""
regenerar_samples_v5.py
=======================
DEPRECADO — usar `regenerar_muestras_minimas.py` (8 PDF, 1 por variante).

Regenera los 17 PDFs de muestra en `docs/casos-clinicos/muestras-20-casos/`
usando el motor NeuroSoft + el ReportData con los resultados validados.

§v5-auditoria: este script reemplaza la generación ad-hoc anterior.
Acepta JSON con los datos del caso + los escalares ya calculados, y
construye un ReportData + genera el PDF de cada variante (pro / pediatrico
/ medicolegal / junta_medica / inconcluso / paciente / estandar).

Uso:
    cd D:\\NeuroSoftApp\\neurosoft-backend
    venv\\Scripts\\python ..\\docs\\casos-clinicos\\regenerar_samples_v5.py

Salida:
    docs/casos-clinicos/muestras-20-casos/caso_NN_<slug>_doc<doc>_<YYYYMMDD>.pdf
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2] / "neurosoft-backend"
sys.path.insert(0, str(BACKEND))

from app.infrastructure.report_pro import generate_pro_pdf  # noqa: E402
from app.infrastructure.report_service import ReportData  # noqa: E402

OUT = Path(__file__).resolve().parent / "muestras-20-casos"
OUT.mkdir(parents=True, exist_ok=True)


# ─── 17 casos sintéticos con perfiles de la validación v5 ─────────────
# Esquema por caso: (slug, nombre, doc, edad, sexo, escolaridad, poblacion,
#                    motivo, resultados [(test_id, pd, escalar, inter)], variante)
CASOS = [
    ("caso_01", "Santiago Morales", "1121000001", "10a 0m", "M", "Primaria", "infantil",
     "Control de aprendizaje",
     [("NiWiscDC", 35, 10, "Promedio"), ("NiWiscSem", 22, 11, "Promedio"),
      ("NiWiscVoc", 25, 9, "Promedio"), ("NiWiscRDD", 12, 10, "Promedio")],
     "pediatrico"),
    ("caso_02", "Valentina Restrepo", "1121000002", "12a 3m", "F", "Secundaria", "infantil",
     "TDAH combinado",
     [("NiWiscDC", 28, 8, "Promedio"), ("NiWiscSem", 18, 9, "Promedio"),
      ("NiWiscVoc", 20, 7, "Limítrofe"), ("NiWiscCl", 32, 5, "Limítrofe"),
      ("NiWiscRDD", 10, 8, "Promedio")],
     "pediatrico"),
    ("caso_03", "Mateo Vargas", "1121000003", "8a 6m", "M", "Primaria", "infantil",
     "Dificultades atencionales",
     [("NiWiscDC", 30, 11, "Promedio"), ("NiWiscSem", 16, 7, "Limítrofe"),
      ("NiWiscRDD", 11, 9, "Promedio")],
     "pediatrico"),
    ("caso_04", "Emiliano Ortega", "1121000004", "15a 0m", "M", "Secundaria", "infantil",
     "Dislexia",
     [("NiWiscDC", 40, 12, "Promedio"), ("NiWiscSem", 30, 13, "Promedio"),
      ("NiWiscVoc", 35, 12, "Promedio"), ("NiWisInf", 18, 10, "Promedio")],
     "pediatrico"),
    ("caso_05", "Isabella Cardona", "1121000005", "11a 9m", "F", "Secundaria", "infantil",
     "Ansiedad escolar",
     [("NiWiscDC", 42, 13, "Promedio"), ("NiWiscSem", 28, 12, "Promedio"),
      ("NiWiscVoc", 32, 11, "Promedio")],
     "pediatrico"),
    ("caso_06", "David López", "1121000006", "16a 11m", "M", "Secundaria", "infantil",
     "Referencia (caso verificado)",
     [("NiWiscDC", 53, 11, "Promedio"), ("NiWiscSem", 32, 11, "Promedio"),
      ("NiWiscVoc", 37, 6, "Limítrofe"), ("NiWiscLN", 25, 16, "Superior"),
      ("NiWiscCl", 46, 4, "Bajo"), ("NiWiscAri", 21, 6, "Limítrofe")],
     "pro"),
    ("caso_07", "Sofía Ramírez", "1121000007", "9a 4m", "F", "Primaria", "infantil",
     "Sospecha TDAH",
     [("NiWiscDC", 33, 10, "Promedio"), ("NiWiscSem", 19, 8, "Promedio")],
     "pediatrico"),
    ("caso_08", "Andrés Mejía", "1121000008", "14a 2m", "M", "Secundaria", "infantil",
     "Cambios de conducta",
     [("NiWiscDC", 36, 10, "Promedio"), ("NiWiscSem", 24, 10, "Promedio")],
     "pediatrico"),
    ("caso_09", "Camila Jiménez", "1121000009", "13a 7m", "F", "Secundaria", "infantil",
     "Bajo rendimiento",
     [("NiWiscDC", 29, 9, "Promedio"), ("NiWiscSem", 17, 8, "Promedio")],
     "pediatrico"),
    ("caso_10", "Juan Pérez", "52100001", "36a 0m", "M", "Universitaria", "adulto_joven",
     "Cambios cognitivos post-TEC",
     [("AdWAISV", 48, 12, "Promedio"), ("AdWAISA", 14, 11, "Promedio"),
      ("AdDDir", 11, 12, "Promedio")],
     "pro"),
    ("caso_11", "María González", "52100002", "42a 3m", "F", "Universitaria", "adulto_joven",
     "Deterioro cognitivo subjetivo",
     [("AdWAISV", 50, 13, "Promedio"), ("AdWAISA", 16, 13, "Promedio"),
      ("AdSemWais", 32, 14, "Promedio")],
     "pro"),
    ("caso_12", "Roberto Silva", "52100003", "28a 9m", "M", "Secundaria", "adulto_joven",
     "Control normal",
     [("AdWAISV", 52, 14, "Promedio"), ("AdWAISA", 18, 14, "Promedio"),
      ("AdDDir", 13, 14, "Promedio")],
     "pro"),
    ("caso_13", "Laura Díaz", "52100004", "55a 0m", "F", "Primaria", "adulto_mayor",
     "Sospecha deterioro",
     [("ViRDD", 4, 11, "Promedio"), ("ViTMTA", 65, 8, "Promedio"),
      ("ViStP", 8, 5, "Limítrofe"), ("ViGroberRLT", 5, 6, "Limítrofe")],
     "pro"),
    ("caso_14", "Pedro Morales", "52100005", "67a 2m", "M", "Secundaria", "adulto_mayor",
     "Envejecimiento típico",
     [("ViRDD", 6, 13, "Promedio"), ("ViTMTA", 50, 11, "Promedio"),
      ("ViStP", 12, 10, "Promedio"), ("ViGroberRLT", 8, 10, "Promedio")],
     "pro"),
    ("caso_15", "Ana Rodríguez", "52100006", "72a 5m", "F", "Primaria", "adulto_mayor",
     "Sospecha EA",
     [("ViRDD", 3, 9, "Promedio"), ("ViTMTA", 90, 5, "Limítrofe"),
      ("ViStP", 5, 3, "Bajo"), ("ViGroberRLT", 3, 4, "Limítrofe")],
     "pro"),
    ("caso_16", "Carlos Hernández", "52100007", "80a 5m", "M", "Primaria", "adulto_mayor",
     "Referencia AM (caso verificado)",
     [("ViRDD", 4, 13, "Promedio"), ("ViRDInv", 2, 11, "Promedio"),
      ("ViTMTA", 239, 6, "Limítrofe"), ("ViStP", 8, 3, "Bajo"),
      ("ViGroberRLT", 3, 3, "Bajo"), ("ViGroberML_Tot", 2, 6, "Limítrofe"),
      ("ViGroberMC_Tot", 7, 4, "Limítrofe"), ("ViAni", 8, 8, "Promedio"),
      ("ViYesavage", 2, 2, "Normal")],
     "pro"),
    ("caso_17", "José Bermúdez", "52100008", "65a 3m", "M", "Universitaria", "adulto_mayor",
     "Control normal (envejecimiento típico)",
     [("ViRDD", 7, 15, "Superior"), ("ViRDInv", 5, 15, "Superior"),
      ("ViTMTA", 45, 10, "Promedio"), ("ViTMTB", 110, 9, "Promedio"),
      ("ViStP", 110, 14, "Superior"), ("ViGroberRLT", 30, 12, "Promedio"),
      ("ViGroberML_Tot", 14, 14, "Superior"), ("ViGroberMC_Tot", 16, 18, "Superior"),
      ("ViAni", 22, 12, "Promedio"), ("FluidP", 18, 11, "Promedio"),
      ("ViYesavage", 1, 1, "Normal")],
     "pro"),
]


def _build_data(caso):
    slug, nombre, doc, edad, sexo, escolaridad, poblacion, motivo, resultados, variante = caso
    rows = []
    for test_id, pd, escalar, inter in resultados:
        rows.append(
            {
                "test_id": test_id,
                "test_nombre": test_id,
                "puntaje_bruto": pd,
                "puntaje_escalar": escalar,
                "tipo_metrica": "escalar",
                "interpretacion": inter,
                "z_equivalente": None,
                "dominio_cognitivo": "",
                "llave_baremo_usada": "",
                "metadata": {},
            }
        )
    return ReportData(
        institucion_nombre="",
        nombre_completo=nombre,
        tipo_documento="CC",
        numero_documento=doc,
        fecha_nacimiento=date(1990, 1, 1) if "65" not in edad and "80" not in edad else date(1945, 1, 1),
        edad_display=edad,
        sexo=sexo,
        escolaridad=escolaridad,
        motivo_consulta=motivo,
        resultados=rows,
        obs_recomendaciones="Continuar seguimiento semestral.",
    )


def main() -> int:
    today = date.today().strftime("%Y%m%d")
    for caso in CASOS:
        slug, nombre, doc, *_ = caso
        data = _build_data(caso)
        variante = caso[-1]
        try:
            pdf = generate_pro_pdf(data, template=variante)
        except Exception as e:
            print(f"FAIL {slug}: {e}")
            continue
        fname = f"{slug}_{nombre.replace(' ', '_')}_doc{doc}_{today}.pdf"
        out = OUT / fname
        out.write_bytes(pdf)
        print(f"OK  {fname} ({len(pdf)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
