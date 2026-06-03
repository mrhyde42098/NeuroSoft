"""
app/domain/clinical_engine/interpretation_engine.py
=====================================================
Motor de Interpretación Clínica Asistida.

Analiza los ResultadoPrueba calculados por el ClinicalEngine y genera:
  1. DomainProfile — resumen por dominio cognitivo con estadísticas
  2. Sugerencias de texto interpretativo por dominio (ayuda al clínico)
  3. Identificación de puntos fuertes y débiles
  4. Perfil Z para la gráfica del informe

NO genera diagnósticos ni reemplaza al clínico.
Provee datos estructurados que el profesional puede usar como base
para escribir sus propias observaciones.

Corresponde a la sección "Observaciones Clínicas NPs" del VBA,
pero con apoyo automático del sistema para acelerar la interpretación.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.entities.models import ResultadoPrueba

# ─────────────────────────────────────────────────────────────────
# MAPEO DE DOMINIOS COGNITIVOS → DESCRIPCIÓN PARA EL INFORME
# Cada dominio agrupa pruebas y tiene una descripción para el reporte
# ─────────────────────────────────────────────────────────────────

DOMAIN_DESCRIPTIONS = {
    "Atención": {
        "icono": "🎯",
        "descripcion_corta": "Capacidad de enfocar, mantener y distribuir recursos atencionales.",
        "pruebas_representativas": ["TMT-A", "CARAS-R", "Dígitos Directos", "Vigilancia"],
        "prompts_bajo": (
            "Los resultados sugieren dificultades en la capacidad de mantener la atención "
            "sostenida y/o selectiva. Se observa una velocidad de procesamiento reducida que "
            "puede interferir con el control de procesos y la evitación de errores por fatiga."
        ),
        "prompts_promedio": (
            "Los procesos atencionales se ubican dentro del rango esperado para la edad, "
            "con adecuada capacidad de registro y focalización en las tareas presentadas."
        ),
        "prompts_superior": (
            "Los resultados evidencian una capacidad atencional por encima de lo esperado, "
            "con eficiente control de la respuesta y velocidad de procesamiento."
        ),
    },
    "Memoria de Trabajo": {
        "icono": "💭",
        "descripcion_corta": "Capacidad de retener y manipular información de forma inmediata.",
        "pruebas_representativas": ["Dígitos Inversos", "Letras y Números", "Aritmética"],
        "prompts_bajo": (
            "Se identifican dificultades en la retención y manipulación simultánea de "
            "información verbal/auditiva. Esto puede afectar el seguimiento de instrucciones "
            "de varios pasos y el rendimiento en cálculo mental."
        ),
        "prompts_promedio": (
            "La memoria de trabajo se encuentra en rango promedio, con adecuada capacidad "
            "para retener y operar con información de manera inmediata."
        ),
        "prompts_superior": (
            "La memoria de trabajo evidencia un rendimiento superior, con alta eficiencia "
            "para la manipulación mental de información."
        ),
    },
    "Memoria Verbal": {
        "icono": "🧠",
        "descripcion_corta": "Codificación, almacenamiento y recuperación de información verbal.",
        "pruebas_representativas": ["CVLT", "Grober-Buschke", "ENI-2 Memoria"],
        "prompts_bajo": (
            "Los resultados indican una vulnerabilidad en los procesos de recuperación de "
            "información verbal. La evocación espontánea se ve afectada, con mayor dependencia "
            "de claves semánticas o reconocimiento."
        ),
        "prompts_promedio": (
            "La memoria verbal muestra un funcionamiento dentro del rango esperado, con "
            "adecuados procesos de codificación y recuperación."
        ),
        "prompts_superior": (
            "Excelente capacidad de aprendizaje y retención verbal, con evocación espontánea eficiente."
        ),
    },
    "Memoria Visuoespacial": {
        "icono": "👁️",
        "descripcion_corta": "Memoria para material visual complejo y orientación espacial.",
        "pruebas_representativas": ["FCRO Recobro", "Benton VRT"],
        "prompts_bajo": (
            "Se observan dificultades en la retención de información visuoespacial compleja. "
            "La copia puede ser adecuada, pero el recobro diferido muestra pérdida significativa "
            "de detalles."
        ),
        "prompts_promedio": (
            "La memoria visuoespacial se ubica en rango promedio, con adecuada retención "
            "de información visual tras un intervalo de tiempo."
        ),
        "prompts_superior": (
            "La memoria visuoespacial es un área de fortaleza, con alto rendimiento en "
            "la retención de material visual complejo."
        ),
    },
    "Lenguaje": {
        "icono": "🗣️",
        "descripcion_corta": "Procesamiento verbal expresivo y receptivo, denominación y fluidez.",
        "pruebas_representativas": ["Denominación", "Fluidez verbal", "Comprensión"],
        "prompts_bajo": (
            "Los resultados sugieren dificultades en algún componente del lenguaje. "
            "Se pueden observar limitaciones en el vocabulario activo, la fluidez verbal "
            "o la comprensión de instrucciones complejas."
        ),
        "prompts_promedio": (
            "El procesamiento lingüístico se ubica en el rango esperado, con adecuada "
            "expresión verbal, comprensión y acceso léxico."
        ),
        "prompts_superior": (
            "El lenguaje evidencia un rendimiento superior con alta fluidez verbal, "
            "rico vocabulario y excelente comprensión."
        ),
    },
    "Praxias y Gnosias": {
        "icono": "✍️",
        "descripcion_corta": "Planificación motora, coordinación visomotora y reconocimiento perceptual.",
        "pruebas_representativas": ["FCRO Copia", "Praxias constructivas", "Reconocimiento objetos"],
        "prompts_bajo": (
            "Los resultados sugieren dificultades en la planificación y ejecución de "
            "movimientos complejos (praxias) y/o en el reconocimiento e interpretación "
            "de información perceptual (gnosias)."
        ),
        "prompts_promedio": (
            "Las habilidades práxicas y gnósicas se ubican en rango promedio, con "
            "adecuada coordinación visomotora y reconocimiento perceptual."
        ),
        "prompts_superior": (
            "Las habilidades visoespaciales y constructivas son una fortaleza, con "
            "excelente planificación y ejecución motora."
        ),
    },
    "Funciones Ejecutivas": {
        "icono": "⚙️",
        "descripcion_corta": "Planificación, flexibilidad cognitiva, inhibición y monitoreo.",
        "pruebas_representativas": ["TMT-B", "WCST", "Stroop", "Torre de Londres"],
        "prompts_bajo": (
            "Se identifican dificultades en el control ejecutivo. Específicamente, "
            "la flexibilidad cognitiva, la inhibición de respuestas predominantes o "
            "la planificación de secuencias de pasos muestran rendimiento por debajo del promedio."
        ),
        "prompts_promedio": (
            "Las funciones ejecutivas se ubican en rango promedio, con adecuado control "
            "inhibitorio, flexibilidad y planificación."
        ),
        "prompts_superior": (
            "Las funciones ejecutivas son un área de fortaleza, con alto control ejecutivo "
            "y eficiente gestión de la interferencia."
        ),
    },
    "Comprensión Verbal (CI)": {
        "icono": "📚",
        "descripcion_corta": "Razonamiento verbal, vocabulario y comprensión de conceptos.",
        "pruebas_representativas": ["Vocabulario", "Semejanzas", "Comprensión WISC/WAIS"],
        "prompts_bajo": None,
        "prompts_promedio": None,
        "prompts_superior": None,
    },
    "Razonamiento Perceptual (CI)": {
        "icono": "🔷",
        "descripcion_corta": "Razonamiento no verbal, análisis visuoespacial y síntesis.",
        "pruebas_representativas": ["Diseño Cubos", "Matrices", "Conceptos Dibujos"],
        "prompts_bajo": None,
        "prompts_promedio": None,
        "prompts_superior": None,
    },
    "Velocidad de Procesamiento": {
        "icono": "⚡",
        "descripcion_corta": "Velocidad y eficiencia en el procesamiento de información simple.",
        "pruebas_representativas": ["Claves", "Búsqueda Símbolos", "Clave de Números"],
        "prompts_bajo": (
            "Se identifica una velocidad de procesamiento reducida, lo que puede "
            "impactar el rendimiento en tareas que requieren rapidez y automatización."
        ),
        "prompts_promedio": (
            "La velocidad de procesamiento se ubica en rango promedio para la edad."
        ),
        "prompts_superior": (
            "Alta velocidad de procesamiento, con eficiente ejecución de tareas automatizadas."
        ),
    },
    "Cociente Intelectual Total": {
        "icono": "🎓",
        "descripcion_corta": "Estimación del funcionamiento intelectual global.",
        "pruebas_representativas": ["WISC-IV CIT", "WAIS-III CIT"],
        "prompts_bajo": None,
        "prompts_promedio": None,
        "prompts_superior": None,
    },
    "Socioemocional": {
        "icono": "💛",
        "descripcion_corta": "Bienestar emocional, ansiedad, depresión y funcionamiento adaptativo.",
        "pruebas_representativas": ["CDI", "Spence", "Beck", "Yesavage"],
        "prompts_bajo": None,
        "prompts_promedio": None,
        "prompts_superior": None,
    },
    "Funcionalidad": {
        "icono": "🏃",
        "descripcion_corta": "Autonomía en actividades básicas e instrumentales de la vida diaria.",
        "pruebas_representativas": ["Vineland", "Lawton", "QSM", "Barthel"],
        "prompts_bajo": None,
        "prompts_promedio": None,
        "prompts_superior": None,
    },
}


# ─────────────────────────────────────────────────────────────────
# RANGOS DE CLASIFICACIÓN (para presentación en el informe)
# ─────────────────────────────────────────────────────────────────

# CI — clasificación completa (WISC-IV / WAIS-III)
CI_RANGES = [
    (130, 999,   "Muy Superior",       "#1565C0", "superior"),
    (120, 129,   "Superior",           "#1976D2", "superior"),
    (110, 119,   "Promedio Alto",      "#2196F3", "promedio"),
    (90,  109,   "Promedio",           "#4CAF50", "promedio"),
    (80,  89,    "Promedio Bajo",      "#FF9800", "limitrofe"),
    (70,  79,    "Limítrofe",          "#F44336", "limitrofe"),
    (55,  69,    "Discapacidad Leve",  "#B71C1C", "bajo"),
    (0,   54,    "Discapacidad Mod.",  "#7B1FA2", "bajo"),
]

# Escalares (WISC / WAIS subescalas)
ESCALAR_RANGES = [
    (16, 19, "Muy Superior",   "#1565C0", "superior"),
    (13, 15, "Superior",       "#1976D2", "superior"),
    (10, 12, "Promedio",       "#4CAF50", "promedio"),
    (8,   9, "Promedio Bajo",  "#FF9800", "limitrofe"),
    (7,   7, "Bajo Promedio",  "#FF5722", "limitrofe"),
    (5,   6, "Limítrofe",      "#F44336", "limitrofe"),
    (1,   4, "Bajo",           "#B71C1C", "bajo"),
]


def classify_ci(ci: float) -> dict:
    for mn, mx, label, color, level in CI_RANGES:
        if mn <= ci <= mx:
            return {"label": label, "color": color, "level": level}
    return {"label": "Sin dato", "color": "#9E9E9E", "level": "sin_dato"}


def classify_escalar(pe: float) -> dict:
    for mn, mx, label, color, level in ESCALAR_RANGES:
        if mn <= pe <= mx:
            return {"label": label, "color": color, "level": level}
    return {"label": "Sin dato", "color": "#9E9E9E", "level": "sin_dato"}


# ─────────────────────────────────────────────────────────────────
# PERFIL DE DOMINIO
# ─────────────────────────────────────────────────────────────────

@dataclass
class DomainProfile:
    """
    Resumen interpretativo de un dominio cognitivo.
    El frontend usa este objeto para pintar la gráfica Z
    y generar el template de texto por dominio.
    """
    dominio: str
    pruebas: list[ResultadoPrueba]
    z_promedio: float | None = None
    nivel_general: str = "Sin dato"  # bajo | limitrofe | promedio | superior
    color: str = "#9E9E9E"
    sugerencia_texto: str = ""       # Texto sugerido (clínico puede editar)
    puntos_debiles: list[str] = field(default_factory=list)
    puntos_fuertes: list[str] = field(default_factory=list)
    icono: str = "🧠"

    @property
    def tiene_datos(self) -> bool:
        return any(r.puntaje_escalar is not None for r in self.pruebas)


# ─────────────────────────────────────────────────────────────────
# MOTOR DE INTERPRETACIÓN
# ─────────────────────────────────────────────────────────────────

class InterpretationEngine:
    """
    Analiza los ResultadoPrueba y construye perfiles por dominio.

    Uso:
        engine = InterpretationEngine()
        profiles = engine.build_profiles(resultados)
        z_data = engine.build_z_chart_data(resultados)
    """

    def build_profiles(
        self, resultados: list[ResultadoPrueba]
    ) -> list[DomainProfile]:
        """
        Agrupa resultados por dominio y construye un DomainProfile por cada uno.
        Retorna los dominios ordenados: CI primero, luego cognitivos, luego escalas.
        """
        # Agrupar por dominio
        by_domain: dict[str, list[ResultadoPrueba]] = {}
        for r in resultados:
            if not r.fue_realizada:
                continue
            dom = r.dominio_cognitivo
            by_domain.setdefault(dom, []).append(r)

        profiles = []
        for dominio, pruebas in by_domain.items():
            profile = self._build_profile(dominio, pruebas)
            profiles.append(profile)

        # Ordenar: CI Total primero, luego el resto
        order = ["Cociente Intelectual Total", "Inteligencia General",
                 "Comprensión Verbal (CI)", "Razonamiento Perceptual (CI)",
                 "Memoria de Trabajo", "Velocidad de Procesamiento",
                 "Atención", "Memoria Verbal", "Memoria Visuoespacial",
                 "Lenguaje", "Praxias y Gnosias", "Funciones Ejecutivas",
                 "Socioemocional", "Funcionalidad"]
        def sort_key(p):
            try: return order.index(p.dominio)
            except ValueError: return 99
        return sorted(profiles, key=sort_key)

    def _build_profile(
        self, dominio: str, pruebas: list[ResultadoPrueba]
    ) -> DomainProfile:
        """Construye el perfil de un dominio a partir de sus pruebas."""
        desc = DOMAIN_DESCRIPTIONS.get(dominio, {})
        icono = desc.get("icono", "🧠")

        # Calcular Z promedio del dominio
        zs = [r.z_equivalente for r in pruebas if r.z_equivalente is not None]
        z_prom = round(sum(zs) / len(zs), 2) if zs else None

        # Nivel general
        nivel, color = self._z_to_level(z_prom)

        # Puntos fuertes/débiles dentro del dominio
        puntos_fuertes = [r.test_nombre for r in pruebas if r.interpretacion == "Superior"]
        puntos_debiles = [r.test_nombre for r in pruebas
                          if r.interpretacion in ("Bajo", "Limítrofe")]

        # Texto sugerido según nivel
        sugerencia = self._get_sugerencia(dominio, nivel, pruebas, z_prom)

        return DomainProfile(
            dominio=dominio,
            pruebas=pruebas,
            z_promedio=z_prom,
            nivel_general=nivel,
            color=color,
            sugerencia_texto=sugerencia,
            puntos_fuertes=puntos_fuertes,
            puntos_debiles=puntos_debiles,
            icono=icono,
        )

    def build_z_chart_data(
        self, resultados: list[ResultadoPrueba]
    ) -> list[dict]:
        """
        Construye los datos para la gráfica Z del informe.
        Compatible con el gráfico de barras horizontal del frontend.

        Retorna lista ordenada de:
            {nombre, z, interpretacion, dominio, tipo_metrica, color, puntaje_escalar, puntaje_bruto}
        """
        items = []
        for r in resultados:
            if not r.fue_realizada or r.z_equivalente is None:
                continue
            z = max(-3.5, min(3.5, r.z_equivalente))
            _, color = self._z_to_level(z)
            items.append({
                "test_id": r.test_id,
                "nombre": r.test_nombre,
                "dominio": r.dominio_cognitivo,
                "puntaje_bruto": r.puntaje_bruto,
                "puntaje_escalar": r.puntaje_escalar,
                "tipo_metrica": r.tipo_metrica,
                "z": z,
                "interpretacion": r.interpretacion,
                "color": color,
            })
        # Ordenar: primero por dominio, luego por Z
        return sorted(items, key=lambda x: (x["dominio"], x["z"]))

    def get_ci_summary(self, resultados: list[ResultadoPrueba]) -> dict | None:
        """
        Extrae el resumen de CI total para el encabezado del informe.
        Busca CIT del WISC o WAIS.
        """
        ci_ids = {"NiWISCTot", "AdWAISCIT", "NiWISCIndCapGen"}
        for r in resultados:
            if r.test_id in ci_ids and r.puntaje_escalar:
                ci = float(r.puntaje_escalar)
                classif = classify_ci(ci)
                return {
                    "test": r.test_nombre,
                    "ci": ci,
                    "clasificacion": classif["label"],
                    "color": classif["color"],
                    "level": classif["level"],
                    "indices": []  # Se populan con los índices individuales
                }
        return None

    # ── Helpers internos ────────────────────────────────────────

    @staticmethod
    def _z_to_level(z: float | None) -> tuple[str, str]:
        """Convierte Z a (nivel_texto, color_hex)."""
        if z is None:
            return "Sin dato", "#9E9E9E"
        if z <= -2.0:  return "Bajo",       "#C62828"
        if z <= -1.0:  return "Limítrofe",  "#E64A19"
        if z <= 1.0:   return "Promedio",   "#2E7D32"
        return "Superior", "#1565C0"

    @staticmethod
    def _get_sugerencia(
        dominio: str,
        nivel: str,
        pruebas: list[ResultadoPrueba],
        z_prom: float | None,
    ) -> str:
        """
        Genera texto interpretativo sugerido para el dominio.
        El clínico lo verá en el formulario de Observaciones Clínicas
        como punto de partida para redactar su interpretación.
        """
        desc = DOMAIN_DESCRIPTIONS.get(dominio, {})

        level_map = {
            "Bajo": "prompts_bajo",
            "Limítrofe": "prompts_bajo",
            "Promedio": "prompts_promedio",
            "Superior": "prompts_superior",
        }
        prompt_key = level_map.get(nivel, "prompts_promedio")
        base_text = desc.get(prompt_key, "")

        if not base_text:
            return ""

        # Enriquecer con nombres de pruebas específicas afectadas
        bajas = [r.test_nombre for r in pruebas if r.interpretacion in ("Bajo", "Limítrofe")]
        altas = [r.test_nombre for r in pruebas if r.interpretacion == "Superior"]

        additions = []
        if bajas and nivel in ("Bajo", "Limítrofe"):
            additions.append(f"Pruebas con rendimiento bajo: {', '.join(bajas)}.")
        if altas and nivel == "Superior":
            additions.append(f"Pruebas con rendimiento alto: {', '.join(altas)}.")

        full = base_text
        if additions:
            full = full.rstrip(".") + " " + " ".join(additions)

        return f"[SUGERENCIA — editar antes de guardar] {full}"
