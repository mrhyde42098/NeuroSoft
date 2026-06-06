"""
report_pro.implicaciones_diarias
================================
"Implications for daily life" — sección que traduce cada dominio cognitivo
debilitado a ejemplos concretos de la vida cotidiana.

Inspirado en:
  * Editorial Médica Panamericana (Cuadro 2.1) — "El informe neuropsicológico"
  * Sattler (2008) — Assessment of Children
  * Beebe (2024, PubMed 38902221) — perspectiva de padres
  * Springer 2026 (s12982-026-01613-x) — visualización funcional
  * NBT NHS — "What my neuropsychology report means"

Cada dominio debilitado se asocia con:
  - 2-4 ejemplos de la vida diaria
  - Una recomendación de apoyo práctica
"""

from __future__ import annotations

from collections.abc import Sequence

# Umbrales Z (alineados con SEMANTIC_* de theme.py)
Z_DEBIL = -1.0
Z_MUY_DEBIL = -2.0


# Por dominio: ejemplos de vida diaria afectados + estrategias de apoyo.
# Textos en español colombiano neutro, lenguaje claro.
IMPLICACIONES_POR_DOMINIO: dict[str, dict[str, list[str]]] = {
    "Atención": {
        "ejemplos": [
            "Mantener el foco en una conversación larga (especialmente en reuniones o clases).",
            "Seguir instrucciones de varios pasos sin perder algún detalle.",
            "Filtrar estímulos distractores en lugares ruidosos o con mucha gente.",
            "Terminar tareas que requieren concentración sostenida (lectura larga, informes).",
        ],
        "estrategias": [
            "Dividir el trabajo en bloques de 20-25 minutos con pausas activas.",
            "Usar temporizadores visuales (Time Timer) y listas de verificación.",
            "Reducir distractores del ambiente: ruido, notificaciones, desorden del escritorio.",
        ],
    },
    "Memoria": {
        "ejemplos": [
            "Recordar listas de pendientes, citas o encargos del día a día.",
            "Retener información nueva (un nombre, una instrucción, un número telefónico).",
            "Recuperar recuerdos autobiográficos o eventos recientes.",
            "Aprender rutas nuevas o lugares desconocidos.",
        ],
        "estrategias": [
            "Anotar todo en agenda, app o post-its a la vista.",
            "Repasar información recién aprendida a los 10 minutos, 1 hora y 1 día.",
            "Usar asociaciones: vincular lo nuevo con algo que ya conoces.",
            "Establecer rutinas: hacer las cosas importantes siempre a la misma hora y lugar.",
        ],
    },
    "Lenguaje": {
        "ejemplos": [
            "Encontrar la palabra exacta cuando se necesita (lo que se llama 'tener la palabra en la punta de la lengua').",
            "Comprender textos largos, abstractos o con doble sentido.",
            "Explicar ideas complejas de forma ordenada.",
            "Seguir el hilo de conversaciones rápidas o con varias personas.",
        ],
        "estrategias": [
            "Practicar lectura activa: subrayar, resumir, explicar en voz alta.",
            "Juegos de palabras: crucigramas, sopas de letras, scrabble, narraciones.",
            "Pedir que le repitan o le expliquen con otras palabras cuando no entienda.",
            "Evitar la autoexigencia: no todas las personas tienen el mismo nivel verbal.",
        ],
    },
    "Funciones Ejecutivas": {
        "ejemplos": [
            "Planear y organizar actividades que requieren varios pasos (cocinar, viaje, proyecto).",
            "Iniciar una tarea que no es agradable pero necesaria.",
            "Adaptarse a cambios de planes o situaciones inesperadas.",
            "Regular emociones intensas (enojo, frustración, euforia) sin 'explotar'.",
        ],
        "estrategias": [
            "Dividir metas grandes en mini-metas con fechas claras.",
            "Usar agenda, alarmas y recordatorios del celular.",
            "Practicar la regla 'parar-pensar-actuar' antes de decisiones impulsivas.",
            "Tener un 'plan B' para imprevistos: reduce la frustración.",
        ],
    },
    "Razonamiento Perceptual": {
        "ejemplos": [
            "Armar rompecabezas, mapas o instrucciones de muebles.",
            "Entender relaciones espaciales (izquierda-derecha, arriba-abajo, rotar mentalmente).",
            "Resolver problemas lógicos nuevos.",
            "Diferenciar detalles visuales similares (ej. letras b/d/p/q).",
        ],
        "estrategias": [
            "Practicar con rompecabezas, tangram, cubos de Kohs, videojuegos de lógica.",
            "Usar material concreto (cubos, figuras) para aprender conceptos abstractos.",
            "Dibujar diagramas o mapas mentales al estudiar.",
        ],
    },
    "Visoconstrucción": {
        "ejemplos": [
            "Copiar dibujos, trazar líneas o reproducir figuras geométricas.",
            "Organizar el espacio físico: escritorio, casa, maleta.",
            "Estacionar un carro, calcular distancias visuales.",
            "Armar rompecabezas físicos o modelos 3D.",
        ],
        "estrategias": [
            "Practicar dibujo libre y copia de figuras.",
            "Usar cuadrículas o guías en tareas que requieren precisión.",
            "Trabajar con material de construcción: Lego, K'NEX, arcilla.",
        ],
    },
    "Velocidad de Procesamiento": {
        "ejemplos": [
            "Hacer cálculos mentales rápidos.",
            "Leer, escribir o copiar a una velocidad funcional para el colegio/trabajo.",
            "Reaccionar a tiempo en situaciones cotidianas (timbre, semáforo, conversación).",
            "Procesar grandes volúmenes de información bajo presión de tiempo.",
        ],
        "estrategias": [
            "Practicar con tiempos: worksheets cronometrados, apps de cálculo rápido.",
            "Usar teclas rápidas y atajos de teclado en computador.",
            "Reducir la carga visual: agrupar información en bloques pequeños.",
        ],
    },
    "Comprensión Verbal": {
        "ejemplos": [
            "Entender el lenguaje oral complejo o abstracto.",
            "Segir instrucciones verbales largas.",
            "Captar ironías, metáforas o dobles sentidos.",
            "Aprender vocabulario nuevo.",
        ],
        "estrategias": [
            "Lectura dialogada: leer y comentar lo leído con alguien más.",
            "Pedir que expliquen las cosas con ejemplos concretos.",
            "Vocabulario activo: usar las palabras nuevas en conversaciones reales.",
        ],
    },
    "Memoria de Trabajo": {
        "ejemplos": [
            "Hacer una operación mental mientras se recuerda otra cosa (ej. contar hacia atrás desde 100 de 7 en 7).",
            "Anotar un teléfono mientras se escucha otra indicación.",
            "Seguir una receta de cocina o instrucciones de varios pasos.",
            "Retener información el tiempo suficiente para usarla (ej. un número de teléfono antes de marcarlo).",
        ],
        "estrategias": [
            "Repetir en voz alta lo que se acaba de escuchar.",
            "Anotar inmediatamente la información importante.",
            "Trabajar en ambientes silenciosos al manejar datos en mente.",
        ],
    },
}


def _normalizar_dominio(d: str) -> str:
    """Compara dominios de forma tolerante (sin acentos, lowercase)."""
    if not d:
        return ""
    nd = d.lower().strip()
    # Mapeo de aliases usados en el motor
    alias = {
        "atencion": "Atención",
        "atención": "Atención",
        "memoria": "Memoria",
        "lenguaje": "Lenguaje",
        "funciones ejecutivas": "Funciones Ejecutivas",
        "funcion ejecutiva": "Funciones Ejecutivas",
        "ff.ee.": "Funciones Ejecutivas",
        "ffee": "Funciones Ejecutivas",
        "razonamiento perceptual": "Razonamiento Perceptual",
        "visoespacial": "Razonamiento Perceptual",
        "visoperceptual": "Razonamiento Perceptual",
        "visoconstruccion": "Visoconstrucción",
        "visoconstrucción": "Visoconstrucción",
        "velocidad de procesamiento": "Velocidad de Procesamiento",
        "vp": "Velocidad de Procesamiento",
        "comprension verbal": "Comprensión Verbal",
        "comprensión verbal": "Comprensión Verbal",
        "memoria de trabajo": "Memoria de Trabajo",
        "memoria trabajo": "Memoria de Trabajo",
        "mt": "Memoria de Trabajo",
    }
    return alias.get(nd, d)


def dominios_con_implicaciones(
    resultados: Sequence[dict],
    z_umbral: float = Z_DEBIL,
) -> list[dict[str, object]]:
    """Devuelve los dominios con Z̄ <= z_umbral y sus implicaciones de vida diaria.

    Output: lista de dicts con estructura::

        {
            "dominio": "Memoria",
            "z_promedio": -1.5,
            "n_pruebas": 3,
            "ejemplos": [...],
            "estrategias": [...],
            "nivel": "moderado" | "severo",
        }
    """
    if not resultados:
        return []

    bucket: dict[str, list[float]] = {}
    for r in resultados:
        z = r.get("z_equivalente")
        if z is None or r.get("tipo_metrica") == "ci":
            continue
        dom = r.get("dominio_cognitivo") or ""
        dom_norm = _normalizar_dominio(dom)
        if not dom_norm:
            continue
        bucket.setdefault(dom_norm, []).append(float(z))

    out: list[dict[str, object]] = []
    for dom, zs in bucket.items():
        media = sum(zs) / len(zs)
        if media > z_umbral:
            continue
        impl = IMPLICACIONES_POR_DOMINIO.get(
            dom,
            {
                "ejemplos": [
                    "Tareas que dependen de esta función pueden requerir más esfuerzo o tiempo.",
                    "Rendimiento bajo comparado con pares de la misma edad y escolaridad.",
                ],
                "estrategias": [
                    "Practicar con constancia y paciencia.",
                    "Acompañar el proceso con apoyo profesional y familiar.",
                ],
            },
        )
        out.append(
            {
                "dominio": dom,
                "z_promedio": media,
                "n_pruebas": len(zs),
                "ejemplos": impl["ejemplos"][:4],
                "estrategias": impl["estrategias"][:3],
                "nivel": "severo" if media <= Z_MUY_DEBIL else "moderado",
            }
        )
    out.sort(key=lambda x: x["z_promedio"])  # más débil primero
    return out


def texto_implicaciones_para_familia(
    resultados: Sequence[dict],
    poblacion: str = "adulto_joven",
) -> str:
    """Genera un párrafo en lenguaje claro para la sección familia.

    Usado cuando el clínico NO ha escrito observaciones manuales y queremos
    dar contexto útil para la familia sin que sea 100% técnico.
    """
    items = dominios_con_implicaciones(resultados)
    if not items:
        return ""

    partes: list[str] = []
    for it in items[:3]:  # máximo 3 dominios para no saturar
        dom = it["dominio"]
        nivel = it["nivel"]
        ej = it["ejemplos"][0] if it["ejemplos"] else ""
        partes.append(
            f"Como {dom.lower()} está {nivel}, es posible que note en la "
            f"vida diaria: {ej.lower() if ej else 'rendimientos por debajo de lo esperado en tareas de esta área'}"
        )
    if not partes:
        return ""
    intro = "Más allá de los puntajes, lo que esto significa en la vida diaria es:"
    return intro + " " + " ".join(partes)
