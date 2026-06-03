"""
app/domain/clinical_engine/test_guide.py
==========================================
Guía de Administración de Pruebas.

Define para CADA prueba neuropsicológica:
  - El orden de administración dentro del protocolo
  - El tiempo límite (si aplica) con cronómetro
  - Las instrucciones clave para el profesional
  - Qué dominio cognitivo evalúa
  - El rango de PD válido (min/max)
  - Tipo de respuesta (tiempo, aciertos, suma, etc.)
  - Tips clínicos NeuroSoft

Esta información alimenta el Panel de Administración de Pruebas
del frontend — la pantalla donde el profesional va prueba por prueba.

Los protocolos mapean exactamente los 19 protocolos del sistema VBA.
"""

from __future__ import annotations

from dataclasses import dataclass

# ─────────────────────────────────────────────────────────────────
# Dominios cognitivos evaluados por cada prueba
# ─────────────────────────────────────────────────────────────────

DOMINIOS = {
    "ATENCION":          "Atención",
    "MEMORIA_TRABAJO":   "Memoria de Trabajo",
    "MEMORIA_VERBAL":    "Memoria Verbal",
    "MEMORIA_VISUAL":    "Memoria Visuoespacial",
    "LENGUAJE":          "Lenguaje",
    "PRAXIAS":           "Praxias y Gnosias",
    "FE":                "Funciones Ejecutivas",
    "CI_VERBAL":         "Comprensión Verbal (CI)",
    "CI_PERCEPTUAL":     "Razonamiento Perceptual (CI)",
    "CI_TOTAL":          "Cociente Intelectual Total",
    "VELOCIDAD":         "Velocidad de Procesamiento",
    "SOCIOEMOCIONAL":    "Socioemocional",
    "FUNCIONALIDAD":     "Funcionalidad",
    "DESARROLLO":        "Desarrollo",
}


@dataclass
class TestInfo:
    """
    Metadatos completos de una prueba neuropsicológica para la guía.
    """
    test_id: str                          # Ej: "NiWiscDC"
    nombre_display: str                   # Ej: "Diseño con Cubos"
    nombre_prueba_completa: str           # Ej: "WISC-IV — Diseño con Cubos"
    dominio: str                          # Clave de DOMINIOS
    orden_protocolo: int = 99             # Orden sugerido de administración

    # Administración
    tiempo_limite_seg: int | None = None  # None = sin límite
    tiempo_instruccion_seg: int = 30         # Tiempo sugerido para instrucciones
    max_pd: int | None = None             # Puntaje directo máximo
    min_pd: int = 0
    tipo_respuesta: str = "aciertos"        # aciertos | tiempo | suma | escala

    # Guía para el profesional
    instruccion_corta: str = ""             # Instrucción que se lee al paciente
    tips_clinicos: str = ""                 # Tips NeuroSoft para el profesional
    materiales: str = ""                    # Materiales necesarios
    criterios_discontinuacion: str = ""     # Cuándo detener la prueba

    # Agrupación
    protocolo_principal: str = ""          # "WISC-IV" | "ENI-2" | "WAIS-III" | etc.
    es_opcional: bool = False


# ─────────────────────────────────────────────────────────────────
# WISC-IV — Niños (6-16 años)
# Orden estándar de administración del WISC-IV (manual Pearson)
# ─────────────────────────────────────────────────────────────────

WISC_IV_TESTS: list[TestInfo] = [
    TestInfo(
        test_id="NiWiscDC",
        nombre_display="Diseño con Cubos",
        nombre_prueba_completa="WISC-IV — Diseño con Cubos",
        dominio="CI_PERCEPTUAL",
        orden_protocolo=1,
        tiempo_limite_seg=120,          # 2 min por ítem difícil
        max_pd=68,
        tipo_respuesta="tiempo",
        instruccion_corta=(
            "«Voy a mostrarte unos cubos de colores. "
            "Quiero que los pongas igual que el dibujo de la tarjeta. "
            "Trabaja tan rápido como puedas.»"
        ),
        tips_clinicos=(
            "Observe si el niño descompone el modelo visualmente antes de construir. "
            "Registre si gira los cubos o usa ensayo/error. "
            "Puntaje = combinación de precisión + tiempo. "
            "Edad 6-7: ítems 1-5 (modelos en 3D). Edad 8+: ítems 1-9."
        ),
        materiales="9 cubos bicolores, tarjetas de estímulo (bloque A)",
        criterios_discontinuacion="3 fracasos consecutivos",
        protocolo_principal="WISC-IV",
    ),
    TestInfo(
        test_id="NiWiscSem",
        nombre_display="Semejanzas",
        nombre_prueba_completa="WISC-IV — Semejanzas",
        dominio="CI_VERBAL",
        orden_protocolo=2,
        tiempo_limite_seg=None,
        max_pd=33,
        tipo_respuesta="aciertos",
        instruccion_corta=(
            "«Voy a decirte dos cosas. Tú dime en qué se parecen. "
            "Por ejemplo, ¿en qué se parecen un plátano y una manzana?»"
        ),
        tips_clinicos=(
            "Evalúa abstracción verbal y razonamiento conceptual. "
            "Respuestas funcionales (0-1 pt) vs. conceptuales (2 pt). "
            "No dar ayuda ni retroalimentación después de los ítems de muestra."
        ),
        materiales="Cuadernillo de respuesta",
        criterios_discontinuacion="3 fracasos consecutivos (0 puntos)",
        protocolo_principal="WISC-IV",
    ),
    TestInfo(
        test_id="NiWiscRDD",
        nombre_display="Retención de Dígitos",
        nombre_prueba_completa="WISC-IV — Retención de Dígitos",
        dominio="MEMORIA_TRABAJO",
        orden_protocolo=3,
        max_pd=16,
        tipo_respuesta="aciertos",
        instruccion_corta=(
            "«Voy a decirte algunos números. Escúchalos con atención y cuando termine "
            "repítelos exactamente igual que yo. Por ejemplo, si digo 6-3, tú dices...»"
        ),
        tips_clinicos=(
            "Dígitos directos evalúa span de memoria auditiva. "
            "Dígitos inversos evalúa memoria de trabajo (manipulación). "
            "Hablar a ritmo de 1 dígito/segundo. NO enfatizar ningún número. "
            "Registrar separado: Directos (NiRDD) e Inversos (NiDR)."
        ),
        materiales="Hoja de registro",
        criterios_discontinuacion="2 intentos fallidos en la misma longitud",
        protocolo_principal="WISC-IV",
    ),
    TestInfo(
        test_id="NiWiscConD",
        nombre_display="Conceptos con Dibujos",
        nombre_prueba_completa="WISC-IV — Conceptos con Dibujos",
        dominio="CI_PERCEPTUAL",
        orden_protocolo=4,
        max_pd=28,
        tipo_respuesta="aciertos",
        instruccion_corta=(
            "«Mira estas imágenes en filas. Señala una imagen de la fila de arriba "
            "y una de la fila de abajo que vayan juntas de alguna manera.»"
        ),
        tips_clinicos=(
            "Evalúa razonamiento abstracto y formación de categorías con material visual. "
            "No dar pistas sobre la categoría. El niño puede señalar o decir el número. "
            "Ítem de práctica obligatorio antes de iniciar."
        ),
        materiales="Cuadernillo de estímulos (bloque C)",
        criterios_discontinuacion="3 fracasos consecutivos",
        protocolo_principal="WISC-IV",
    ),
    TestInfo(
        test_id="NiWiscCl",
        nombre_display="Claves",
        nombre_prueba_completa="WISC-IV — Claves",
        dominio="VELOCIDAD",
        orden_protocolo=5,
        tiempo_limite_seg=120,
        max_pd=119,
        tipo_respuesta="tiempo",
        instruccion_corta=(
            "«Mira estos números. Cada número tiene un símbolo debajo. "
            "Dibuja el símbolo que le corresponde a cada número. "
            "Trabaja tan rápido como puedas sin saltarte ninguno.»"
        ),
        tips_clinicos=(
            "Cronómetro en mano — exactamente 120 segundos. "
            "Forma A (menores 8): figuras geométricas simples. "
            "Forma B (8-16): símbolos abstractos. "
            "Contar aciertos completados, no los errores."
        ),
        materiales="Hoja de claves (forma A o B según edad), lápiz sin borrador",
        criterios_discontinuacion="Al sonar el cronómetro",
        protocolo_principal="WISC-IV",
    ),
    TestInfo(
        test_id="NiWiscVoc",
        nombre_display="Vocabulario",
        nombre_prueba_completa="WISC-IV — Vocabulario",
        dominio="CI_VERBAL",
        orden_protocolo=6,
        max_pd=68,
        tipo_respuesta="aciertos",
        instruccion_corta="«Voy a decirte una palabra y tú me dices lo que significa.»",
        tips_clinicos=(
            "Evalúa conocimiento semántico y expresión verbal. "
            "Respuestas de 0, 1 o 2 puntos según profundidad conceptual. "
            "Puede preguntar '¿Puedes decirme más?' si la respuesta es incompleta (solo una vez)."
        ),
        criterios_discontinuacion="3 fracasos consecutivos",
        protocolo_principal="WISC-IV",
    ),
    TestInfo(
        test_id="NiWiscLN",
        nombre_display="Letras y Números",
        nombre_prueba_completa="WISC-IV — Letras y Números",
        dominio="MEMORIA_TRABAJO",
        orden_protocolo=7,
        max_pd=30,
        tipo_respuesta="aciertos",
        instruccion_corta=(
            "«Voy a decirte números y letras mezclados. "
            "Cuando termine, dime primero los números en orden de menor a mayor "
            "y luego las letras en orden alfabético.»"
        ),
        tips_clinicos=(
            "Evalúa secuenciación, memoria de trabajo verbal y atención dividida. "
            "Si el niño repite solo los números o solo las letras = 0 puntos. "
            "3 intentos por ítem. 1 punto si al menos un intento correcto."
        ),
        criterios_discontinuacion="3 fracasos consecutivos",
        protocolo_principal="WISC-IV",
    ),
    TestInfo(
        test_id="NiWiscMat",
        nombre_display="Matrices",
        nombre_prueba_completa="WISC-IV — Matrices",
        dominio="CI_PERCEPTUAL",
        orden_protocolo=8,
        max_pd=35,
        tipo_respuesta="aciertos",
        instruccion_corta=(
            "«Mira el cuadro con el espacio en blanco. "
            "Señala la imagen de abajo que va en ese espacio.»"
        ),
        tips_clinicos=(
            "Evalúa razonamiento fluido no verbal y análisis de patrones. "
            "No hay tiempo límite. Respuesta única (opciones A-E). "
            "No dar pistas sobre patrones."
        ),
        criterios_discontinuacion="3 fracasos consecutivos",
        protocolo_principal="WISC-IV",
    ),
    TestInfo(
        test_id="NiWiscCom",
        nombre_display="Comprensión",
        nombre_prueba_completa="WISC-IV — Comprensión",
        dominio="CI_VERBAL",
        orden_protocolo=9,
        max_pd=38,
        tipo_respuesta="aciertos",
        instruccion_corta=(
            "«Voy a hacerte algunas preguntas. Escucha con atención y responde lo mejor que puedas.»"
        ),
        tips_clinicos=(
            "Evalúa comprensión de normas sociales y juicio práctico. "
            "Puede preguntar '¿Qué más?' para completar respuesta de 1 punto. "
            "Respuestas de 0, 1 o 2 puntos."
        ),
        criterios_discontinuacion="3 fracasos consecutivos",
        protocolo_principal="WISC-IV",
    ),
    TestInfo(
        test_id="NiWiscBusSim",
        nombre_display="Búsqueda de Símbolos",
        nombre_prueba_completa="WISC-IV — Búsqueda de Símbolos",
        dominio="VELOCIDAD",
        orden_protocolo=10,
        tiempo_limite_seg=120,
        max_pd=60,
        tipo_respuesta="tiempo",
        instruccion_corta=(
            "«Mira el símbolo(s) de la izquierda. "
            "Busca si ese símbolo aparece en el grupo de la derecha. "
            "Marca SÍ si aparece, NO si no aparece. Trabaja rápido.»"
        ),
        tips_clinicos=(
            "Exactamente 120 segundos. "
            "Forma A (6-7 años): 1 símbolo de búsqueda. "
            "Forma B (8-16): 2 símbolos de búsqueda. "
            "Puntaje = aciertos − errores."
        ),
        materiales="Hoja de Búsqueda de Símbolos, lápiz sin borrador",
        criterios_discontinuacion="Al sonar el cronómetro",
        protocolo_principal="WISC-IV",
    ),
    TestInfo(
        test_id="NiWiscAri",
        nombre_display="Aritmética",
        nombre_prueba_completa="WISC-IV — Aritmética",
        dominio="MEMORIA_TRABAJO",
        orden_protocolo=11,
        max_pd=34,
        tipo_respuesta="tiempo",
        instruccion_corta="«Voy a hacerte algunas preguntas de matemáticas. No puedes usar papel.»",
        tips_clinicos=(
            "Evalúa razonamiento numérico y memoria de trabajo. "
            "Tiempo por ítem varía (30-120 seg según ítem). "
            "Cronometrar desde que se termina de leer el ítem."
        ),
        criterios_discontinuacion="3 fracasos consecutivos",
        protocolo_principal="WISC-IV",
    ),
    # Subescalas opcionales WISC-IV
    TestInfo(test_id="NiWisFigInc", nombre_display="Figuras Incompletas",
             nombre_prueba_completa="WISC-IV — Figuras Incompletas",
             dominio="CI_PERCEPTUAL", orden_protocolo=12, max_pd=38,
             tiempo_limite_seg=20, tipo_respuesta="tiempo",
             instruccion_corta="«Mira este dibujo. ¿Qué parte importante le falta?»",
             tips_clinicos="20 segundos por ítem. Evalúa reconocimiento visual y atención al detalle.",
             protocolo_principal="WISC-IV", es_opcional=True),
    TestInfo(test_id="NiWisReg", nombre_display="Registros",
             nombre_prueba_completa="WISC-IV — Registros (Clave)",
             dominio="VELOCIDAD", orden_protocolo=12, max_pd=60,
             es_opcional=True, protocolo_principal="WISC-IV"),
    TestInfo(test_id="NiWisInf", nombre_display="Información",
             nombre_prueba_completa="WISC-IV — Información",
             dominio="CI_VERBAL", orden_protocolo=12, max_pd=33,
             instruccion_corta="«Voy a hacerte algunas preguntas sobre cosas generales.»",
             es_opcional=True, protocolo_principal="WISC-IV"),
    TestInfo(test_id="NiWisPalCon", nombre_display="Palabras en Contexto",
             nombre_prueba_completa="WISC-IV — Palabras en Contexto",
             dominio="CI_VERBAL", orden_protocolo=12, max_pd=30,
             es_opcional=True, protocolo_principal="WISC-IV"),
]

# Índices compuestos WISC-IV (se calculan a partir de suma de escalares)
WISC_IV_INDICES: list[TestInfo] = [
    TestInfo(test_id="NiWISCIndComVer", nombre_display="ICV — Índice Comprensión Verbal",
             nombre_prueba_completa="WISC-IV — Índice Comprensión Verbal",
             dominio="CI_VERBAL", tipo_respuesta="suma",
             instruccion_corta="Suma de escalares: Semejanzas + Vocabulario + Comprensión",
             tips_clinicos="Ingresar la SUMA de los puntajes escalares de las 3 subescalas.",
             protocolo_principal="WISC-IV"),
    TestInfo(test_id="NiWISCIndRazPer", nombre_display="IRP — Índice Razonamiento Perceptual",
             nombre_prueba_completa="WISC-IV — Índice Razonamiento Perceptual",
             dominio="CI_PERCEPTUAL", tipo_respuesta="suma",
             instruccion_corta="Suma: Diseño Cubos + Conceptos Dibujos + Matrices",
             protocolo_principal="WISC-IV"),
    TestInfo(test_id="NiWISCIndMemTra", nombre_display="IMT — Índice Memoria de Trabajo",
             nombre_prueba_completa="WISC-IV — Índice Memoria de Trabajo",
             dominio="MEMORIA_TRABAJO", tipo_respuesta="suma",
             instruccion_corta="Suma: Retención Dígitos + Letras y Números",
             protocolo_principal="WISC-IV"),
    TestInfo(test_id="NiWISCIndVelPro", nombre_display="IVP — Índice Velocidad de Procesamiento",
             nombre_prueba_completa="WISC-IV — Índice Velocidad de Procesamiento",
             dominio="VELOCIDAD", tipo_respuesta="suma",
             instruccion_corta="Suma: Claves + Búsqueda de Símbolos",
             protocolo_principal="WISC-IV"),
    TestInfo(test_id="NiWISCTot", nombre_display="CIT — CI Total WISC-IV",
             nombre_prueba_completa="WISC-IV — CI Total",
             dominio="CI_TOTAL", tipo_respuesta="suma",
             instruccion_corta="Suma de los 4 índices compuestos (ICV + IRP + IMT + IVP)",
             tips_clinicos="Ingresar la SUMA de los 4 puntajes de índice (no los escalares directamente).",
             protocolo_principal="WISC-IV"),
]


# ─────────────────────────────────────────────────────────────────
# WAIS-III — Adulto Joven (16-54 años)
# ─────────────────────────────────────────────────────────────────

WAIS_III_TESTS: list[TestInfo] = [
    TestInfo(test_id="AdWAISV", nombre_display="Vocabulario",
             nombre_prueba_completa="WAIS-III — Vocabulario",
             dominio="CI_VERBAL", orden_protocolo=1, max_pd=80,
             instruccion_corta="«¿Qué significa la palabra...?»",
             tips_clinicos="Misma lógica que WISC. Respuestas 0, 1 o 2 pts. Puede pedir aclaración.",
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdWAISI", nombre_display="Información",
             nombre_prueba_completa="WAIS-III — Información",
             dominio="CI_VERBAL", orden_protocolo=2, max_pd=29,
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdWAISC", nombre_display="Comprensión",
             nombre_prueba_completa="WAIS-III — Comprensión",
             dominio="CI_VERBAL", orden_protocolo=3, max_pd=28,
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdWAISA", nombre_display="Aritmética",
             nombre_prueba_completa="WAIS-III — Aritmética",
             dominio="MEMORIA_TRABAJO", orden_protocolo=4, max_pd=22,
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdWAISCC", nombre_display="Construcción Cubos",
             nombre_prueba_completa="WAIS-III — Construcción con Cubos",
             dominio="CI_PERCEPTUAL", orden_protocolo=5, max_pd=68,
             tiempo_limite_seg=120,
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdSDWais", nombre_display="Clave de Números",
             nombre_prueba_completa="WAIS-III — Clave de Números",
             dominio="VELOCIDAD", orden_protocolo=6, max_pd=133,
             tiempo_limite_seg=120,
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdMatr", nombre_display="Matrices",
             nombre_prueba_completa="WAIS-III — Matrices",
             dominio="CI_PERCEPTUAL", orden_protocolo=7, max_pd=26,
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdDDir", nombre_display="Dígitos",
             nombre_prueba_completa="WAIS-III — Dígitos",
             dominio="MEMORIA_TRABAJO", orden_protocolo=8,
             instruccion_corta="Dígitos directos + inversos. Registrar TOTAL.",
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdWAISFI", nombre_display="Figuras Incompletas",
             nombre_prueba_completa="WAIS-III — Figuras Incompletas",
             dominio="CI_PERCEPTUAL", orden_protocolo=9, max_pd=25,
             tiempo_limite_seg=20, protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdWAISHI", nombre_display="Historietas",
             nombre_prueba_completa="WAIS-III — Historietas",
             dominio="CI_PERCEPTUAL", orden_protocolo=10,
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdWAISL", nombre_display="Letras y Números",
             nombre_prueba_completa="WAIS-III — Letras y Números",
             dominio="MEMORIA_TRABAJO", orden_protocolo=11,
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdBusSim", nombre_display="Búsqueda de Símbolos",
             nombre_prueba_completa="WAIS-III — Búsqueda de Símbolos",
             dominio="VELOCIDAD", orden_protocolo=12, tiempo_limite_seg=120,
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdWAISRO", nombre_display="Rompecabezas",
             nombre_prueba_completa="WAIS-III — Rompecabezas",
             dominio="CI_PERCEPTUAL", orden_protocolo=13,
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdSemWais", nombre_display="Semejanzas",
             nombre_prueba_completa="WAIS-III — Semejanzas",
             dominio="CI_VERBAL", orden_protocolo=14,
             protocolo_principal="WAIS-III"),
    # Funciones ejecutivas WAIS
    TestInfo(test_id="AdTMT_AB", nombre_display="TMT A y B",
             nombre_prueba_completa="Trail Making Test — Partes A y B",
             dominio="ATENCION_FE", orden_protocolo=15,
             tiempo_limite_seg=300, tipo_respuesta="tiempo",
             instruccion_corta="«Parte A: una los círculos en orden numérico. Parte B: alterne número-letra: 1-A-2-B-3-C...»",
             tips_clinicos="Evalúa atención, velocidad y flexibilidad cognitiva. Tiempo máx 300 seg por parte.",
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdRDI", nombre_display="Dígitos Inversos",
             nombre_prueba_completa="Dígitos Inversos (separado)",
             dominio="MEMORIA_TRABAJO", orden_protocolo=17,
             tips_clinicos="Algunos protocolos requieren dígitos inversos por separado.",
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdFCROCop", nombre_display="FCRO — Copia",
             nombre_prueba_completa="Figura Compleja de Rey-Osterrieth — Copia",
             dominio="PRAXIAS", orden_protocolo=18,
             tipo_respuesta="tiempo",
             instruccion_corta="«Copia este dibujo tan exactamente como puedas.»",
             tips_clinicos=(
                 "Registrar tiempo de copia (segundos). "
                 "Observar estrategia: configural (bien), fragmentada (señal de dificultad). "
                 "PD máx = 36 (sistema de puntuación de Taylor). "
                 "Pedir memoria a los 30-40 minutos (FCRO Recobro)."
             ),
             protocolo_principal="WAIS-III"),
    TestInfo(test_id="AdFCRORec", nombre_display="FCRO — Memoria (Recobro)",
             nombre_prueba_completa="Figura Compleja de Rey-Osterrieth — Recobro Espontáneo",
             dominio="MEMORIA_VISUAL", orden_protocolo=99,
             instruccion_corta="«Dibuja el mismo dibujo que copiaste antes, de memoria.»",
             tips_clinicos="Administrar 30-40 min después de la copia. Sin tiempo límite.",
             protocolo_principal="WAIS-III"),
]


# ─────────────────────────────────────────────────────────────────
# ENI-2 — Evaluación Neuropsicológica Infantil
# ─────────────────────────────────────────────────────────────────

ENI2_ATENCION: list[TestInfo] = [
    TestInfo(test_id="NiTMTA", nombre_display="TMT-A (versión infantil)",
             nombre_prueba_completa="Trail Making Test A — Infantil",
             dominio="ATENCION", orden_protocolo=1, tiempo_limite_seg=150,
             tipo_respuesta="tiempo",
             tips_clinicos="Registrar tiempo en segundos. Máx 150 seg para niños.",
             protocolo_principal="ENI-2"),
    TestInfo(test_id="NiTMTB", nombre_display="TMT-B (versión infantil)",
             nombre_prueba_completa="Trail Making Test B — Infantil",
             dominio="FE", orden_protocolo=2, tiempo_limite_seg=150,
             tipo_respuesta="tiempo",
             protocolo_principal="ENI-2"),
    TestInfo(test_id="NiTesCA", nombre_display="Test Caras — Aciertos",
             nombre_prueba_completa="Test de Percepción de Diferencias (CARAS) — Aciertos",
             dominio="ATENCION", orden_protocolo=3, tiempo_limite_seg=180,
             tipo_respuesta="tiempo",
             instruccion_corta="«Tacha la cara diferente de cada fila lo más rápido que puedas.»",
             tips_clinicos="3 minutos exactos. Puntaje = aciertos. Registrar errores separado (NiTesCE).",
             protocolo_principal="ENI-2"),
    TestInfo(test_id="NiTesCE", nombre_display="Test Caras — Errores",
             nombre_prueba_completa="CARAS — Errores",
             dominio="ATENCION", orden_protocolo=3,
             tipo_respuesta="aciertos",
             protocolo_principal="ENI-2"),
]


# ─────────────────────────────────────────────────────────────────
# Escalas socioemocionales (Niños)
# ─────────────────────────────────────────────────────────────────

ESCALAS_NINOS: list[TestInfo] = [
    TestInfo(test_id="NiCDI", nombre_display="CDI — Depresión Infantil",
             nombre_prueba_completa="Children's Depression Inventory (CDI)",
             dominio="SOCIOEMOCIONAL", tipo_respuesta="escala",
             instruccion_corta="Aplicar directamente al niño (8+ años). Lee cada ítem y elige la opción.",
             tips_clinicos=(
                 "27 ítems, escala 0-2. PD máx = 54. "
                 "Punto de corte clínico: ≥19 (depresión probable). "
                 "El sistema calcula Z por edad y sexo automáticamente."
             ),
             protocolo_principal="Escalas"),
    TestInfo(test_id="NiSpenceTo", nombre_display="SCAS — Ansiedad Total",
             nombre_prueba_completa="Spence Children's Anxiety Scale — Total",
             dominio="SOCIOEMOCIONAL", tipo_respuesta="escala",
             instruccion_corta="38 ítems sobre situaciones de ansiedad. Escala 0-3.",
             tips_clinicos=(
                 "Registrar TOTAL y cada subescala por separado. "
                 "El sistema calcula T-scores por normativa."
             ),
             protocolo_principal="Escalas"),
    TestInfo(test_id="NiVin", nombre_display="Vineland — Conducta Adaptativa",
             nombre_prueba_completa="Vineland Adaptive Behavior Scale",
             dominio="FUNCIONALIDAD", tipo_respuesta="escala",
             instruccion_corta="Entrevista al cuidador principal. No al niño.",
             tips_clinicos=(
                 "Preguntar por lo que el niño HACE, no lo que puede hacer. "
                 "Cubre comunicación, vida diaria, socialización y motricidad."
             ),
             protocolo_principal="Escalas"),
    TestInfo(test_id="NiMchat", nombre_display="M-CHAT — Autismo temprano",
             nombre_prueba_completa="Modified Checklist for Autism in Toddlers (M-CHAT)",
             dominio="SOCIOEMOCIONAL", tipo_respuesta="escala",
             instruccion_corta="Cuestionario de 20 ítems respondido por los padres. Niños 16-30 meses.",
             protocolo_principal="Complementarias"),
]

# ─────────────────────────────────────────────────────────────────
# PRUEBAS ADULTO MAYOR (Neuronorma Colombia)
# ─────────────────────────────────────────────────────────────────

ADULTO_MAYOR_TESTS: list[TestInfo] = [
    TestInfo(test_id="ViTMTA", nombre_display="TMT Parte A",
             nombre_prueba_completa="Trail Making Test — Parte A (Adulto Mayor)",
             dominio="ATENCION", orden_protocolo=1,
             tiempo_limite_seg=300, tipo_respuesta="tiempo",
             instruccion_corta="«Una los círculos en orden numérico lo más rápido posible.»",
             tips_clinicos="Registrar tiempo en segundos. Errores se corrigen en el momento. Tiempo máx 300 seg.",
             protocolo_principal="Neuronorma_AM"),
    TestInfo(test_id="ViTMTB", nombre_display="TMT Parte B",
             nombre_prueba_completa="Trail Making Test — Parte B (Adulto Mayor)",
             dominio="FE", orden_protocolo=2,
             tiempo_limite_seg=300, tipo_respuesta="tiempo",
             instruccion_corta="«Una los círculos alternando número-letra: 1-A-2-B-3-C...»",
             tips_clinicos="Evalúa flexibilidad cognitiva y control ejecutivo. Tiempo max 300 seg.",
             protocolo_principal="Neuronorma_AM"),
]


# ─────────────────────────────────────────────────────────────────
# DICCIONARIO MAESTRO: test_id → TestInfo
# Cargado una sola vez al iniciar la app
# ─────────────────────────────────────────────────────────────────

_ALL_TESTS: list[TestInfo] = (
    WISC_IV_TESTS + WISC_IV_INDICES + WAIS_III_TESTS +
    ENI2_ATENCION + ESCALAS_NINOS + ADULTO_MAYOR_TESTS
)

TEST_GUIDE: dict[str, TestInfo] = {t.test_id: t for t in _ALL_TESTS}


def get_test_info(test_id: str) -> TestInfo | None:
    """Retorna los metadatos de administración de una prueba."""
    return TEST_GUIDE.get(test_id)


def get_protocol_tests(protocol_name: str, include_optional: bool = False) -> list[TestInfo]:
    """Retorna las pruebas de un protocolo en orden de administración."""
    tests = [
        t for t in _ALL_TESTS
        if t.protocolo_principal == protocol_name
        and (include_optional or not t.es_opcional)
    ]
    return sorted(tests, key=lambda t: t.orden_protocolo)


# ─────────────────────────────────────────────────────────────────
# PROTOCOLOS (19 del VBA + nuevos)
# ─────────────────────────────────────────────────────────────────

PROTOCOLOS_DISPONIBLES = [
    {
        "id": "wisc_ci",
        "nombre": "Protocolo Cognitivo CI — WISC-IV",
        "poblacion": "infantil",
        "descripcion": "Evaluación de inteligencia completa con WISC-IV para niños 6-16 años",
        "pruebas_principales": ["NiWiscDC","NiWiscSem","NiWiscRDD","NiWiscConD","NiWiscCl",
                                 "NiWiscVoc","NiWiscLN","NiWiscMat","NiWiscCom","NiWiscBusSim",
                                 "NiWiscAri","NiWISCIndComVer","NiWISCIndRazPer",
                                 "NiWISCIndMemTra","NiWISCIndVelPro","NiWISCTot"],
    },
    {
        "id": "wisc_perfil",
        "nombre": "Protocolo Perfil Cognitivo + CI — WISC-IV / ENI-2",
        "poblacion": "infantil",
        "descripcion": "CI completo + perfil neuropsicológico por dominios",
        "pruebas_principales": ["NiWiscDC","NiWiscSem","NiWiscRDD","NiWiscConD","NiWiscCl",
                                 "NiWiscVoc","NiWiscLN","NiWiscMat","NiWiscCom","NiWiscBusSim",
                                 "NiWiscAri","NiWISCTot","NiTMTA","NiTMTB","NiTesCA","NiTesCE",
                                 "NiFCROCop","NiFCRORec","NiFM","NiFA","NiCDI"],
    },
    {
        "id": "kabc_ci",
        "nombre": "Protocolo Perfil Cognitivo CI — KABC",
        "poblacion": "infantil",
        "descripcion": "Batería Kaufman para niños 2.5-12.5 años",
        "pruebas_principales": ["NiKabcVMag","NiKabcRC","NiKabcMMa","NiKabcCG","NiKabcRN",
                                 "NiKabcTria","NiKabcOPa","NiKabcMAna","NiKabcMEsp","NiKabcSFot"],
    },
    {
        "id": "ead",
        "nombre": "Protocolo Cognitivo Clínico — Escala Abreviada Desarrollo EAD",
        "poblacion": "infantil",
        "descripcion": "Desarrollo global para niños 0-60 meses",
        "pruebas_principales": ["NiEADMG","NiEADMF","NiEADAL","NiEADPS","NiEADTot"],
    },
    {
        "id": "wais_ci",
        "nombre": "Protocolo Cognitivo CI — WAIS-III",
        "poblacion": "adulto_joven",
        "descripcion": "CI completo adulto 16-74 años",
        "pruebas_principales": ["AdWAISV","AdWAISI","AdWAISC","AdWAISA","AdWAISCC",
                                 "AdSDWais","AdMatr","AdDDir","AdWAISFI","AdWAISHI",
                                 "AdWAISL","AdBusSim","AdWAISRO","AdSemWais",
                                 "AdWAISCIT","AdWAISICV","AdWAISICP","AdWAISIMT","AdWAISIVP"],
    },
    {
        "id": "wais_perfil_adulto",
        "nombre": "Protocolo CI WAIS-III + Perfil Cognitivo Adulto Joven",
        "poblacion": "adulto_joven",
        "descripcion": "CI + perfil ejecutivo + memoria adulto joven",
        "pruebas_principales": ["AdWAISCIT","AdTMT_AB","AdFCROCop","AdFCRORec",
                                 "AdCVLTE1","AdCVLTE2","AdCVLTE3","AdCVLTE4","AdCVLTE5",
                                 "AdStP","AdStC","AdStPC","AdRDI","AdQSM","AdBeck"],
    },
    {
        "id": "adulto_mayor",
        "nombre": "Protocolo Perfil Cognitivo Adulto Mayor",
        "poblacion": "adulto_mayor",
        "descripcion": "Evaluación completa adulto mayor >50 años",
        "pruebas_principales": ["ViTMTA","ViTMTB","ViSimDig","ViRDD","ViRDInv",
                                 "ViGroberLE1","ViGroberLE2","ViGroberLE3",
                                 "ViGroberCE1","ViGroberCE2","ViGroberCE3",
                                 "ViWCat","ViWCor","ViStP","ViStC","ViStPC",
                                 "ViDeno","ViAni","ViYesavage","ViLawton","ViMMSE"],
    },
]
