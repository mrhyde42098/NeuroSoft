"""
app/application/use_cases/report_enrichment.py
===============================================
Orquesta los motores clínicos auxiliares para enriquecer el informe NPS
de una evaluación concreta.

Combina:
    • Catálogo RIPS institucional → población sugerida y dx probables por edad.
    • Reservorio de recomendaciones por grupo etario + cuadro clínico.
    • Batería alterna sugerida (si hay discapacidad registrada).
    • Detección automática de patrones cognitivos a partir de los índices.
    • Advertencias heredadas del motor de scoring.

La salida es JSON-safe; alimenta tanto el generador de PDF como el front.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


# ─────────────────────────────────────────────────────────────
# Edad → grupo etario (para el reservorio de recomendaciones)
# ─────────────────────────────────────────────────────────────
def _edad_anos(fecha_nacimiento: date | None, ref: date | None = None) -> int | None:
    if not fecha_nacimiento:
        return None
    ref = ref or date.today()
    anos = ref.year - fecha_nacimiento.year
    if (ref.month, ref.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        anos -= 1
    return max(0, anos)


def _grupo_reservorio(edad: int | None) -> str | None:
    if edad is None:
        return None
    if edad < 18:
        return "infantil"
    if edad < 50:
        return "adulto"
    return "adulto_mayor"


# ─────────────────────────────────────────────────────────────
# CIE-10 → clave del reservorio (mapeo canónico)
# ─────────────────────────────────────────────────────────────
CIE10_TO_CUADRO: dict[str, dict[str, str]] = {
    # Infantil
    "infantil": {
        "F900":  "tdah",
        "F901":  "tdah",
        "F840":  "dislexia",          # aprox — TEA sin clave dedicada → discapacidad_cognitiva/dislexia si aplica
        "F810":  "dislexia",
        "F811":  "dislexia",
        "F812":  "dislexia",
        "F819":  "dislexia",
        "F800":  "disfasia",
        "F801":  "disfasia",
        "F802":  "disfasia",
        "F809":  "disfasia",
        "F820":  "trastornos_espaciales_motores",
        "F700":  "discapacidad_cognitiva",
        "F710":  "discapacidad_cognitiva",
        "F720":  "discapacidad_cognitiva",
        "F730":  "discapacidad_cognitiva",
        "F799":  "discapacidad_cognitiva",
        "F930":  "ansiedad",
        "F931":  "ansiedad",
        "F932":  "ansiedad",
        "F910":  "conducta",
        "F913":  "conducta",
        "F318":  "tab_infantil",
        "F319":  "tab_infantil",
    },
    # Adulto
    "adulto": {
        "F320":  "depresion_ansiedad_tdah",
        "F321":  "depresion_ansiedad_tdah",
        "F322":  "depresion_ansiedad_tdah",
        "F329":  "depresion_ansiedad_tdah",
        "F410":  "depresion_ansiedad_tdah",
        "F411":  "depresion_ansiedad_tdah",
        "F900":  "depresion_ansiedad_tdah",
        "G20X":  "trastornos_motores_adulto",
        "G122":  "trastornos_motores_adulto",
        "G35X":  "trastornos_motores_adulto",
        "S069":  "tce",
        "I639":  "riesgo_vascular",
        "I10X":  "riesgo_vascular",
        "E119":  "riesgo_vascular",
        "F700":  "discapacidad_intelectual_adulto",
        "F710":  "discapacidad_intelectual_adulto",
        "F720":  "discapacidad_intelectual_adulto",
        "F730":  "discapacidad_intelectual_adulto",
    },
    # Adulto mayor
    "adulto_mayor": {
        "F067":  "dcl_amnesico",
        "F000":  "demencia_alzheimer",
        "F001":  "demencia_alzheimer",
        "F002":  "demencia_alzheimer",
        "F010":  "demencia_vascular",
        "F011":  "demencia_vascular",
        "F012":  "demencia_vascular",
        "F013":  "demencia_vascular",
        "F018":  "demencia_vascular",
        "F019":  "demencia_vascular",
        "G311":  "ftd",
        "F021":  "ftd",
        "F03X":  "generales",
    },
}


def _cuadro_por_cie10(grupo: str | None, cie10: str | None) -> str | None:
    if not grupo or not cie10:
        return None
    return CIE10_TO_CUADRO.get(grupo, {}).get(cie10.strip().upper())


# ─────────────────────────────────────────────────────────────
# Discapacidad registrada → condición para baterías alternas
# ─────────────────────────────────────────────────────────────
def _condicion_bateria(discapacidad: str | None) -> str | None:
    if not discapacidad:
        return None
    import unicodedata
    # Quita tildes para que "visión"/"vision" y "física"/"fisica" matcheen igual
    d_norm = "".join(
        c for c in unicodedata.normalize("NFD", discapacidad.lower().strip())
        if unicodedata.category(c) != "Mn"
    )
    if not d_norm or d_norm in ("n/a", "ninguna", "sin discapacidad"):
        return None

    audit = "auditiv" in d_norm or "sord" in d_norm or "hipoacu" in d_norm
    vis   = ("visual" in d_norm or "vision" in d_norm or "cegu" in d_norm
             or "cieg" in d_norm or "baja vision" in d_norm)

    if audit and vis:
        return "visual_auditiva"
    if audit:
        return "hipoacusia"
    if vis:
        return "discapacidad_visual"
    if "motor" in d_norm or "fisic" in d_norm or "hemipares" in d_norm:
        return "motora"
    if "analfabet" in d_norm or "sin escolaridad" in d_norm:
        return "analfabeta"
    return None


def _grupo_bateria(edad: int | None) -> str | None:
    """Batería alterna usa 3 grupos: nino / adulto / adulto_mayor."""
    if edad is None:
        return None
    if edad < 18:
        return "nino"
    if edad < 60:
        return "adulto"
    return "adulto_mayor"


# ─────────────────────────────────────────────────────────────
# Motor de detección de patrones cognitivos (índices WISC/WAIS)
# ─────────────────────────────────────────────────────────────
def _extraer_indice(resultados: list, nombres: list) -> int | None:
    """Busca un índice CI en la lista de resultados por nombre o test_id."""
    for r in resultados:
        nombre_p = (r.get("nombre_prueba") or "").lower()
        test_id  = (r.get("test_id") or "").lower()
        for n in nombres:
            if n.lower() in nombre_p or n.lower() in test_id:
                val = r.get("puntaje_escalar")
                if val and val != 9999:
                    return int(val)
    return None


def detectar_patrones_cognitivos(
    resultados: list,
    edad: int | None,
) -> list[dict]:
    """
    Analiza los resultados de evaluación para detectar patrones clínicos.
    Devuelve lista de patrones con: tipo, nivel, notas, sugerencias.
    """
    if not resultados:
        return []

    ICV = _extraer_indice(resultados, ["IndComVer", "ICV", "ComVer", "WAISICV"])
    IRP = _extraer_indice(resultados, ["IndRazPer", "IRP", "RazPer", "IndComPer", "ICP"])
    IMT = _extraer_indice(resultados, ["IndMemTra", "IMT", "MemTra", "WAISMT"])
    IVP = _extraer_indice(resultados, ["IndVelPro", "IVP", "VelPro", "WAISIVP"])
    CIT = _extraer_indice(resultados, ["WISCTot", "WAISTot", "CIT"])

    patrones: list[dict] = []
    disponibles = [v for v in [ICV, IRP, IMT, IVP] if v is not None]

    if len(disponibles) < 2:
        return patrones

    # 1. TDAH — brecha cristalizado vs ejecutivo
    if all(v is not None for v in [ICV, IRP, IMT, IVP]):
        ejec = (IMT + IVP) / 2
        crist = (ICV + IRP) / 2
        brecha = crist - ejec
        if ejec < 90 and crist >= 90 and brecha >= 15:
            patrones.append({
                "tipo": "TDAH / Déficit atencional-ejecutivo",
                "nivel": "alto" if brecha >= 25 else "moderado",
                "indices": {"ICV": ICV, "IRP": IRP, "IMT": IMT, "IVP": IVP},
                "brecha": round(brecha, 1),
                "notas": [
                    f"Cristalizado (ICV+IRP)/2={round(crist,1)} vs Ejecutivo (IMT+IVP)/2={round(ejec,1)}",
                    f"Brecha de {round(brecha,1)} pts — significativa clínicamente (umbral ≥15 pts).",
                ],
                "sugerencia": "Completar con SNAP-IV (padres/maestros) o ASRS (adultos). Historia de síntomas en múltiples entornos.",
            })

    # 2. TCL / CDHS — IVP selectivo muy bajo
    if all(v is not None for v in [ICV, IRP, IMT, IVP]):
        media_otros = (ICV + IRP + IMT) / 3
        dif = media_otros - IVP
        if IVP < 85 and dif >= 20 and ICV >= 90:
            patrones.append({
                "tipo": "Tempo Cognitivo Lento / CDHS",
                "nivel": "alto" if dif >= 30 else "moderado",
                "indices": {"ICV": ICV, "IRP": IRP, "IMT": IMT, "IVP": IVP},
                "diferencia_ivp": round(dif, 1),
                "notas": [
                    f"IVP={IVP} vs media otros índices={round(media_otros,1)} (dif={round(dif,1)} pts).",
                    "ICV preservado: lenguaje intacto — apoya enlentecimiento selectivo.",
                    "Patrón compatible con Barkley (2012): CDHS/CDS.",
                ],
                "sugerencia": "Evaluar síntomas de ensoñación, pasividad, lentitud. Diferenciar de ansiedad y trastorno del sueño.",
            })

    # 3. Discapacidad Intelectual
    if CIT is not None and CIT < 70:
        patrones.append({
            "tipo": "Posible Discapacidad Intelectual",
            "nivel": "alto" if CIT < 55 else "moderado",
            "indices": {"CIT": CIT},
            "notas": [
                f"CI Total = {CIT} — por debajo del umbral de DI (DSM-5: ~65-75).",
                "Requiere segunda prueba de inteligencia + evaluación de conducta adaptativa.",
            ],
            "sugerencia": "Aplicar Vineland-3 o ABAS-3 para conducta adaptativa. No diagnosticar solo por CI.",
        })

    # 4. DCL / Demencia — adulto mayor con múltiples índices bajos
    if edad is not None and edad >= 55:
        afectados = len([v for v in disponibles if v < 85])
        if afectados >= 2:
            patrones.append({
                "tipo": "Deterioro Cognitivo Leve (DCL) — multi-dominio" if afectados >= 3
                        else "Deterioro cognitivo leve — verificar",
                "nivel": "alto" if afectados >= 3 else "moderado",
                "indices": {k: v for k, v in
                            zip(["ICV","IRP","IMT","IVP"], [ICV,IRP,IMT,IVP]) if v is not None},
                "notas": [
                    f"Edad {edad} años — zona de riesgo para DCL/demencia.",
                    f"{afectados} de {len(disponibles)} índices < 85.",
                    "Descartar: depresión, hipotiroidismo, déficit B12/folato, medicación.",
                ],
                "sugerencia": "GDS-15 + FAQ + MoCA si no aplicado. Neuroimagen y laboratorios. Seguimiento 6-12 meses.",
            })

    # 5. Secuela neurológica — velocidad + ejecutivo sin DI
    if (IVP is not None and IVP < 85 and IMT is not None and IMT < 85
            and CIT is not None and CIT >= 70
            and (edad is None or edad < 55)):
        maximo_cristalizado = max(v for v in [ICV, IRP] if v is not None) if any(
            v is not None for v in [ICV, IRP]) else None
        if maximo_cristalizado and maximo_cristalizado - IVP >= 20:
            patrones.append({
                "tipo": "Posible secuela neurológica (TCE / ACV / tóxico)",
                "nivel": "moderado",
                "indices": {"IVP": IVP, "IMT": IMT},
                "notas": [
                    f"IVP={IVP} + IMT={IMT} afectados con cristalizado relativamente preservado.",
                    "Patrón compatible con TCE, secuela vascular o exposición tóxica.",
                ],
                "sugerencia": "Evaluar antecedentes. Pruebas complementarias: PASAT, SDMT, TMT-B. Neuroimagen.",
            })

    return patrones


# ─────────────────────────────────────────────────────────────
# Mapeo TCL/CDHS y CIE-10 extendido
# ─────────────────────────────────────────────────────────────
CIE10_TCL_MAP = {
    # TCL / CDHS no tiene código CIE-10 propio — se mapea a TDAH
    "F90.0": "tdah", "F90.1": "tdah", "F90.8": "tempo_cognitivo_lento",
    # Demencia con síntomas neuropsiquiátricos
    "F06.7": "dcl_amnesico", "F00.0": "demencia_alzheimer",
    "F01.0": "demencia_vascular", "F02.0": "ftd",
    # TCE
    "S06.9": "tce", "S06.3": "tce",
}

# ─────────────────────────────────────────────────────────────
# DTO de salida
# ─────────────────────────────────────────────────────────────
@dataclass
class EnrichmentResult:
    patient_id:          str
    eval_id:             str
    edad:                int | None
    grupo_etario:        str | None
    cie10:               str | None
    cuadro_detectado:    str | None
    recomendaciones:     list[str]         = field(default_factory=list)
    bateria_sugerida:    dict | None    = None
    advertencias:        list[str]         = field(default_factory=list)
    notas:               list[str]         = field(default_factory=list)
    patrones_cognitivos: list[dict]        = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "patient_id":         self.patient_id,
            "eval_id":            self.eval_id,
            "edad":               self.edad,
            "grupo_etario":       self.grupo_etario,
            "cie10":              self.cie10,
            "cuadro_detectado":   self.cuadro_detectado,
            "recomendaciones":    self.recomendaciones,
            "bateria_sugerida":   self.bateria_sugerida,
            "advertencias":       self.advertencias,
            "notas":              self.notas,
            "patrones_cognitivos": self.patrones_cognitivos,
        }


# ─────────────────────────────────────────────────────────────
# Motor principal
# ─────────────────────────────────────────────────────────────
def build_report_enrichment(
    *,
    eval_id: str,
    patient_id: str,
    fecha_nacimiento: date | None,
    codigo_cie10: str | None,
    discapacidad: str | None = None,
    advertencias: list[str] | None = None,
    resultados_pruebas: list[dict] | None = None,
) -> EnrichmentResult:
    """
    Construye el bloque de enriquecimiento a partir de los campos
    mínimos de paciente + evaluación (no toca la base de datos).

    Args:
        resultados_pruebas: Lista de resultados [{nombre_prueba, test_id,
                            puntaje_escalar, ...}] — usada para detección
                            de patrones cognitivos automática.
    """
    advertencias = list(advertencias or [])
    notas: list[str] = []

    edad = _edad_anos(fecha_nacimiento)
    grupo = _grupo_reservorio(edad)
    cuadro = _cuadro_por_cie10(grupo, codigo_cie10)

    # ── Patrones cognitivos automáticos ──
    patrones: list[dict] = []
    if resultados_pruebas:
        try:
            patrones = detectar_patrones_cognitivos(resultados_pruebas, edad)
            if patrones:
                tipos = [p["tipo"] for p in patrones]
                notas.append(
                    f"Detección automática de patrones cognitivos: {'; '.join(tipos)}. "
                    "Validar con historia clínica y juicio clínico."
                )
                # Si no hay cuadro CIE-10 mapeado, intentar derivar desde el patrón
                if cuadro is None and patrones:
                    primer_tipo = patrones[0]["tipo"].lower()
                    if "tdah" in primer_tipo:
                        cuadro = cuadro or ("depresion_ansiedad_tdah" if grupo == "adulto" else "tdah")
                    elif "tempo" in primer_tipo or "cdhs" in primer_tipo:
                        cuadro = cuadro or "tdah"  # más cercano en el reservorio
                    elif "deterioro" in primer_tipo or "dcl" in primer_tipo:
                        cuadro = cuadro or "dcl_amnesico"
                    elif "discapacidad" in primer_tipo:
                        cuadro = cuadro or (
                            "discapacidad_cognitiva" if grupo == "infantil"
                            else "discapacidad_intelectual_adulto"
                        )
        except Exception as e:
            advertencias.append(f"Error en detección de patrones cognitivos: {e}")

    # ── Recomendaciones ──
    recs: list[str] = []
    if grupo and cuadro:
        try:
            from app.presentation.api.v1.clinical_extras import _load_reservorio
            data = _load_reservorio()
            grupo_data = data["grupos"].get(grupo, {})
            cuadro_data = grupo_data.get("cuadros", {}).get(cuadro, {})
            recs = list(cuadro_data.get("recomendaciones", []))
            if recs:
                from app.core.branding import clinical_brand
                notas.append(
                    f"Recomendaciones extraídas del reservorio {clinical_brand()} "
                    f"({grupo} / {cuadro_data.get('label', cuadro)})."
                )
        except Exception as e:
            advertencias.append(f"No se pudo cargar el reservorio: {e}")
    elif grupo:
        notas.append(
            "No se encontró cuadro clínico mapeado para el CIE-10 registrado; "
            "se omiten recomendaciones automáticas."
        )

    # ── Batería alterna ──
    bat_sugerida: dict | None = None
    cond = _condicion_bateria(discapacidad)
    grupo_bat = _grupo_bateria(edad)
    if cond and grupo_bat:
        try:
            from app.presentation.api.v1.clinical_extras import _load_baterias_catalog
            cat = _load_baterias_catalog()
            cond_data = cat["conditions"].get(cond)
            if cond_data and grupo_bat in cond_data.get("batteries", {}):
                bat_sugerida = {
                    "condicion":       cond,
                    "condicion_label": cond_data["label"],
                    "grupo":           grupo_bat,
                    "general_notes":   cond_data.get("general_notes", []),
                    "battery":         cond_data["batteries"][grupo_bat],
                }
                from app.core.branding import clinical_brand
                notas.append(
                    f"Se sugiere batería alterna {clinical_brand()} para {cond_data['label']} "
                    f"({grupo_bat})."
                )
        except Exception as e:
            advertencias.append(f"No se pudo cargar baterías alternas: {e}")

    return EnrichmentResult(
        patient_id=patient_id,
        eval_id=eval_id,
        edad=edad,
        grupo_etario=grupo,
        cie10=codigo_cie10,
        cuadro_detectado=cuadro,
        recomendaciones=recs,
        bateria_sugerida=bat_sugerida,
        advertencias=advertencias,
        notas=notas,
        patrones_cognitivos=patrones,
    )
