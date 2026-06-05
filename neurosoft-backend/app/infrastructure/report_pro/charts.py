"""
report_pro.charts
==================
Gráficos clínicos profesionales dibujados directamente sobre el canvas
ReportLab. No usamos ``reportlab.graphics.charts.*`` porque la personalización
y los anti-aliasing son limitados — preferimos primitivas (línea, polígono,
rect, círculo) que dan resultado más limpio.

Gráficos disponibles:

* ``draw_z_profile``       — perfil Z horizontal por prueba (versión Pro).
* ``draw_domain_radar``    — radar/spider de dominios cognitivos.
* ``draw_normal_curve``    — curva gaussiana con perfil del paciente superpuesto.
* ``draw_discrepancies``   — barras horizontales con líneas críticas (p<.05, p<.15).
* ``draw_ci_kpi_row``      — fila de "tarjetas KPI" para los índices CI principales.

Cada función recibe ``c`` (canvas) y ``y`` (posición vertical), devuelve el
``y`` final tras dibujar.
"""
from __future__ import annotations

import logging
import math
from collections import defaultdict
from collections.abc import Sequence

logger = logging.getLogger("neurosoft.report_pro.charts")

from .helpers import draw_text
from .theme import (
    FONT_SANS,
    FONT_SANS_BOLD,
    FONT_SERIF,
    LAYOUT,
    NAVY,
    SEMANTIC_DEFICIT,
    SEMANTIC_LIMITE,
    SEMANTIC_PROMEDIO,
    SEMANTIC_SUPERIOR,
    SLATE,
    SLATE_LIGHT,
    SURFACE,
    TEAL,
    TEAL_DARK,
    TYPE,
    WHITE,
    semantic_color_for_z,
)

# ──────────────────────────────────────────────────────────
# 1) PERFIL Z HORIZONTAL — versión Pro
# ──────────────────────────────────────────────────────────

def draw_z_profile(
    c,
    resultados: Sequence[dict],
    y: float,
    *,
    max_rows_per_page: int = 22,
) -> float:
    """Perfil Z horizontal con bandas semánticas y tipografía mejorada."""
    L = LAYOUT
    Z_MIN, Z_MAX = -3.0, 3.0
    z_range = Z_MAX - Z_MIN

    label_w = 175
    val_w = 50
    track_w = L.content_w - label_w - val_w - 8
    track_x = L.margin + label_w + 4
    row_h = 16
    bar_h = 9
    label_size = TYPE.caption

    def _header(yy: float) -> float:
        # Banda semántica de fondo
        c.setFillColorRGB(*SURFACE)
        c.rect(L.margin, yy - 18, L.content_w, 16, fill=1, stroke=0)
        draw_text(
            c, "PRUEBA", L.margin + 4, yy - 12,
            font_name=FONT_SANS_BOLD, size=TYPE.caption, color=NAVY,
        )
        for z_val in [-3, -2, -1, 0, 1, 2, 3]:
            px = track_x + (z_val - Z_MIN) / z_range * track_w
            draw_text(
                c, str(z_val), px, yy - 12,
                font_name=FONT_SANS, size=TYPE.caption, color=SLATE, align="center",
            )
        draw_text(
            c, "Z", track_x + track_w + 4, yy - 12,
            font_name=FONT_SANS_BOLD, size=TYPE.caption, color=NAVY,
        )
        return yy - 22

    y = _header(y)

    # Bandas semánticas verticales muy sutiles
    def _semantic_bands(top: float, bot: float) -> None:
        # rojo claro (-3 a -2)
        c.setFillColorRGB(0.99, 0.93, 0.93)
        x1 = track_x + ((-3) - Z_MIN) / z_range * track_w
        x2 = track_x + ((-2) - Z_MIN) / z_range * track_w
        c.rect(x1, bot, x2 - x1, top - bot, fill=1, stroke=0)
        # naranja claro (-2 a -1)
        c.setFillColorRGB(0.99, 0.95, 0.91)
        x1 = track_x + ((-2) - Z_MIN) / z_range * track_w
        x2 = track_x + ((-1) - Z_MIN) / z_range * track_w
        c.rect(x1, bot, x2 - x1, top - bot, fill=1, stroke=0)
        # verde claro (-1 a 1) — zona normal
        c.setFillColorRGB(0.93, 0.99, 0.94)
        x1 = track_x + ((-1) - Z_MIN) / z_range * track_w
        x2 = track_x + (1 - Z_MIN) / z_range * track_w
        c.rect(x1, bot, x2 - x1, top - bot, fill=1, stroke=0)
        # azul claro (1 a 3)
        c.setFillColorRGB(0.92, 0.95, 0.99)
        x1 = track_x + (1 - Z_MIN) / z_range * track_w
        x2 = track_x + (3 - Z_MIN) / z_range * track_w
        c.rect(x1, bot, x2 - x1, top - bot, fill=1, stroke=0)

    # Título descriptivo del gráfico
    from .helpers import chart_title
    y = chart_title(
        c, "Perfil Z por prueba",
        y, note=(
            "Eje horizontal: puntaje Z (rango -3 a +3). Verde = zona normal; "
            "rojo/naranja = debajo del promedio; azul = por encima."
        ),
    )

    y = _header(y)

    rows_drawn = 0
    band_top = y + 2
    for r in resultados:
        z = r.get("z_equivalente")
        if z is None:
            continue

        # Salto de página si hace falta
        if y - row_h < L.content_bottom + 30:
            # cerrar banda
            _semantic_bands(band_top, y - 2)
            c.showPage()
            y = L.content_top
            y = _header(y)
            band_top = y + 2
            rows_drawn = 0
        rows_drawn += 1

        from .helpers import human_test_name
        nombre = human_test_name(
            r.get("test_id", "") or "",
            r.get("test_nombre", "") or "",
        )
        color = semantic_color_for_z(z)

        # Línea central Z=0 (sutil)
        center_x = track_x + ((0 - Z_MIN) / z_range) * track_w
        c.setStrokeColorRGB(*SLATE_LIGHT)
        c.setLineWidth(0.3)
        c.line(center_x, y - row_h + 2, center_x, y + 2)

        # Barra Z (anclada en 0)
        bar_pct = max(0.0, min(1.0, (z - Z_MIN) / z_range))
        bar_px = track_x + bar_pct * track_w
        zero_px = track_x + ((0 - Z_MIN) / z_range) * track_w
        bx = min(bar_px, zero_px)
        bw = max(1.0, abs(bar_px - zero_px))
        c.setFillColorRGB(*color)
        c.rect(bx, y - bar_h + 1, bw, bar_h, fill=1, stroke=0)
        # Punto en el extremo de la barra
        c.setFillColorRGB(*color)
        c.circle(bar_px, y - bar_h / 2 + 1, 1.6, fill=1, stroke=0)

        # Label — truncado inteligente con elipsis según ancho real
        from .helpers import fit_text_to_width, human_test_name
        nombre_legible = human_test_name(
            r.get("test_id", "") or "",
            nombre,
        )
        nombre_visible = fit_text_to_width(
            nombre_legible,
            max_width=label_w - 8,
            font_name=FONT_SANS,
            size=label_size,
        )
        draw_text(
            c, nombre_visible, L.margin + 4, y - 9,
            font_name=FONT_SANS, size=label_size, color=NAVY,
        )

        # Valor Z numérico
        z_str = f"{z:+.2f}"
        draw_text(
            c, z_str, track_x + track_w + 4, y - 9,
            font_name=FONT_SANS_BOLD, size=TYPE.caption, color=color,
        )
        y -= row_h

    # cerrar última banda
    _semantic_bands(band_top, y - 2)

    # Leyenda compacta
    y -= 6
    draw_text(
        c, "Banda verde = rango normal (-1 a +1 σ).  Z<-1 sugiere debilidad.  Z>+1 sugiere fortaleza relativa.",
        L.margin, y, font_name=FONT_SANS, size=TYPE.micro + 0.5, color=SLATE,
    )
    return y - 10


# ──────────────────────────────────────────────────────────
# 2) RADAR DE DOMINIOS COGNITIVOS
# ──────────────────────────────────────────────────────────

def _aggregate_by_domain(resultados: Sequence[dict]) -> dict[str, float]:
    """Agrupa resultados por ``dominio_cognitivo`` y promedia el Z."""
    bucket: dict[str, list[float]] = defaultdict(list)
    for r in resultados:
        z = r.get("z_equivalente")
        if z is None:
            continue
        dom = (r.get("dominio_cognitivo") or "").strip()
        if not dom or dom.lower() in ("", "n/a", "general"):
            continue
        # Filtrar índices CI (ya van en KPIs)
        if r.get("tipo_metrica") == "ci":
            continue
        bucket[dom].append(float(z))
    return {dom: sum(vals) / len(vals) for dom, vals in bucket.items() if vals}


def draw_domain_radar(
    c,
    resultados: Sequence[dict],
    y: float,
    *,
    size: float = 220.0,
) -> float:
    """Radar de promedios Z por dominio cognitivo.

    Si hay <3 dominios distintos, omite el gráfico y retorna y sin cambios.
    """
    L = LAYOUT
    domain_z = _aggregate_by_domain(resultados)
    if len(domain_z) < 3:
        return y  # No tiene sentido un radar con 2 ejes

    # Título descriptivo (visible antes del gráfico)
    from .helpers import chart_title
    y = chart_title(
        c, "Perfil cognitivo por dominio",
        y, note=(
            "Cada eje representa un dominio cognitivo. El polígono teal "
            "muestra el Z̄ del paciente; la franja verde central equivale "
            "al rango normal (-1 a +1 σ)."
        ),
    )

    # Orden estable: dominios clínicos típicos primero
    preferred = [
        "Atención", "Memoria", "Lenguaje", "Funciones Ejecutivas",
        "Visoespacial", "Visoconstrucción", "Velocidad de Procesamiento",
        "Comprensión Verbal", "Memoria de Trabajo", "Razonamiento Perceptual",
        "Praxias", "Gnosias", "Habilidades Académicas",
    ]
    ordered = [d for d in preferred if d in domain_z]
    ordered += [d for d in domain_z if d not in ordered]

    n = len(ordered)
    cx = L.margin + L.content_w / 2
    cy = y - size / 2 - 10
    radius = size / 2 - 30  # margen para labels

    # Z mapeado a r normalizado (0 a 1) — usamos rango -3 a +3
    Z_MIN, Z_MAX = -3.0, 3.0
    def z_to_r(z: float) -> float:
        return max(0.05, min(1.0, (z - Z_MIN) / (Z_MAX - Z_MIN)))

    # ── Anillos concéntricos en Z = -3, -2, -1, 0, 1, 2, 3 ──
    rings = [(-3, 0.0, SLATE_LIGHT, 0.15),
             (-2, 0.167, SEMANTIC_DEFICIT, 0.3),
             (-1, 0.333, SEMANTIC_LIMITE, 0.35),
             (0, 0.5, SLATE, 0.5),
             (1, 0.667, SEMANTIC_PROMEDIO, 0.35),
             (2, 0.833, SEMANTIC_SUPERIOR, 0.3),
             (3, 1.0, SLATE_LIGHT, 0.15)]
    for z_val, frac, col, alpha in rings:
        r_ring = radius * frac
        if z_val == 0:
            # Anillo Z=0 más marcado
            c.setStrokeColorRGB(*SLATE)
            c.setLineWidth(0.8)
        else:
            c.setStrokeColorRGB(col[0], col[1], col[2])
            c.setLineWidth(0.4)
        # ReportLab circle no admite dashed fácil — dibujamos polígono regular
        pts = []
        for i in range(n):
            ang = math.pi / 2 - 2 * math.pi * i / n
            px = cx + r_ring * math.cos(ang)
            py = cy + r_ring * math.sin(ang)
            pts.append((px, py))
        path = c.beginPath()
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        path.close()
        c.drawPath(path, stroke=1, fill=0)

    # Banda verde de zona normal (-1 a +1) sombreada
    inner_frac, outer_frac = 0.333, 0.667
    inner_pts = []
    outer_pts = []
    for i in range(n):
        ang = math.pi / 2 - 2 * math.pi * i / n
        inner_pts.append((cx + radius * inner_frac * math.cos(ang),
                          cy + radius * inner_frac * math.sin(ang)))
        outer_pts.append((cx + radius * outer_frac * math.cos(ang),
                          cy + radius * outer_frac * math.sin(ang)))
    # Sombreado del anillo normal (verde muy translúcido)
    c.setFillColorRGB(0.92, 0.98, 0.93)
    path = c.beginPath()
    path.moveTo(*outer_pts[0])
    for p in outer_pts[1:]:
        path.lineTo(*p)
    path.close()
    c.drawPath(path, stroke=0, fill=1)
    # Recortar el centro (hueco interior)
    c.setFillColorRGB(*WHITE)
    path = c.beginPath()
    path.moveTo(*inner_pts[0])
    for p in inner_pts[1:]:
        path.lineTo(*p)
    path.close()
    c.drawPath(path, stroke=0, fill=1)

    # ── Líneas radiales + labels ──
    from .helpers import fit_text_to_width
    for i, dom in enumerate(ordered):
        ang = math.pi / 2 - 2 * math.pi * i / n
        end_x = cx + radius * math.cos(ang)
        end_y = cy + radius * math.sin(ang)
        c.setStrokeColorRGB(*SLATE_LIGHT)
        c.setLineWidth(0.35)
        c.line(cx, cy, end_x, end_y)

        # Label — versión corta con abreviatura + versión completa
        # abreviada a 14 caracteres, con fit_to_width para no truncar bruscamente.
        # Abreviaturas legibles para los nombres largos más comunes.
        ABBREV = {
            "Funciones Ejecutivas": "F. Ejecutivas",
            "Razonamiento Perceptual": "Raz. Perceptual",
            "Velocidad de Procesamiento": "Veloc. Procesam.",
            "Comprensión Verbal": "Comprens. Verbal",
            "Memoria de Trabajo": "Mem. de Trabajo",
            "Habilidades Académicas": "Hab. Académicas",
            "Visoconstrucción": "Visoconstrucción",
            "Visoespacial": "Visoespacial",
        }
        label_x = cx + (radius + 14) * math.cos(ang)
        label_y = cy + (radius + 14) * math.sin(ang)
        z_val = domain_z[dom]
        # Título con abreviatura si existe; si no, fit_to_width lo recorta
        # elegantemente a un ancho máximo según el lado del radar.
        max_label_w = 90 if math.cos(ang) > 0.7 or math.cos(ang) < -0.7 else 80
        raw_label = ABBREV.get(dom, dom)
        label = fit_text_to_width(
            raw_label, max_width=max_label_w,
            font_name=FONT_SANS_BOLD, size=TYPE.caption,
        )
        align = "center"
        if math.cos(ang) > 0.3:
            align = "left"
        elif math.cos(ang) < -0.3:
            align = "right"
        draw_text(
            c, label, label_x, label_y - 3,
            font_name=FONT_SANS_BOLD, size=TYPE.caption, color=NAVY, align=align,
        )
        draw_text(
            c, f"Z={z_val:+.1f}", label_x, label_y - 11,
            font_name=FONT_SANS, size=TYPE.micro + 0.5,
            color=semantic_color_for_z(z_val), align=align,
        )

    # ── Polígono del paciente ──
    poly_pts = []
    for i, dom in enumerate(ordered):
        ang = math.pi / 2 - 2 * math.pi * i / n
        rr = radius * z_to_r(domain_z[dom])
        px = cx + rr * math.cos(ang)
        py = cy + rr * math.sin(ang)
        poly_pts.append((px, py))

    # Relleno translúcido (teal con baja opacidad usando overlay)
    c.saveState()
    try:
        c.setFillColorRGB(*TEAL)
        c.setFillAlpha(0.18)  # ReportLab soporta alpha en versiones modernas
    except Exception as _exc:
        # §A4-fix: ReportLab antiguo sin setFillAlpha — degradamos gracefully.
        logger.debug("setFillAlpha no soportado (ReportLab antiguo): %s", _exc)
    path = c.beginPath()
    path.moveTo(*poly_pts[0])
    for p in poly_pts[1:]:
        path.lineTo(*p)
    path.close()
    c.drawPath(path, stroke=0, fill=1)
    c.restoreState()

    # Contorno sólido
    c.setStrokeColorRGB(*TEAL_DARK)
    c.setLineWidth(1.5)
    path = c.beginPath()
    path.moveTo(*poly_pts[0])
    for p in poly_pts[1:]:
        path.lineTo(*p)
    path.close()
    c.drawPath(path, stroke=1, fill=0)

    # Vértices
    for (px, py), dom in zip(poly_pts, ordered):
        c.setFillColorRGB(*semantic_color_for_z(domain_z[dom]))
        c.circle(px, py, 2.4, fill=1, stroke=0)

    # Título del gráfico
    # (movido al inicio de la función para que el lector vea el nombre ANTES del polígono)

    return cy - radius - 28


# ──────────────────────────────────────────────────────────
# 3) CURVA GAUSSIANA CON PERFIL DEL PACIENTE
# ──────────────────────────────────────────────────────────

def draw_domain_traffic_light(
    c,
    resultados: Sequence[dict],
    y: float,
    *,
    max_rows: int = 9,
) -> float:
    """Semáforo de dominios: una fila por dominio con indicador ● + Z̄ + banda.

    Cada fila tiene:
      ●  color de la banda del Z̄ del dominio (rojo/amarillo/verde/azul)
      Nombre del dominio
      Z̄ = X.XXσ
      Banda (severo / moderado / promedio / superior)
    """
    L = LAYOUT
    from .narrative import _domain_summary
    domains = _domain_summary(resultados)
    if not domains:
        return y
    # Ordenar por Z̄ ascendente (peor primero)
    items = sorted(domains.items(), key=lambda kv: kv[1]["mean_z"])
    items = items[:max_rows]

    row_h = 14
    dot_r = 3.5
    # Cabecera
    y = y - 4
    c.setFillColorRGB(*SURFACE)
    c.rect(L.margin, y - 14, L.content_w, 12, fill=1, stroke=0)
    from .helpers import draw_text  # type: ignore
    draw_text(c, "DOMINIO", L.margin + 4, y - 10, font_name=FONT_SANS_BOLD, size=TYPE.caption, color=NAVY)
    draw_text(c, "Z̄", L.margin + L.content_w * 0.55, y - 10, font_name=FONT_SANS_BOLD, size=TYPE.caption, color=NAVY, align="left")
    draw_text(c, "BANDA", L.margin + L.content_w * 0.70, y - 10, font_name=FONT_SANS_BOLD, size=TYPE.caption, color=NAVY, align="left")
    y -= 16

    def _banda(z: float) -> tuple[str, tuple[float, float, float]]:
        if z <= -2:
            return ("severo", SEMANTIC_DEFICIT)
        if z <= -1:
            return ("moderado", SEMANTIC_LIMITE)
        if z <= 1:
            return ("promedio", SEMANTIC_PROMEDIO)
        return ("superior", SEMANTIC_SUPERIOR)

    for dominio, info in items:
        z = info["mean_z"]
        banda, color = _banda(z)
        # Fila zebra sutil
        c.setFillColorRGB(*SURFACE)
        c.rect(L.margin, y - row_h, L.content_w, row_h - 1, fill=1, stroke=0)
        # Semáforo
        c.setFillColorRGB(*color)
        c.circle(L.margin + 7, y - row_h / 2, dot_r, fill=1, stroke=0)
        # Nombre
        from .helpers import fit_text_to_width  # type: ignore
        nombre_v = fit_text_to_width(
            dominio, max_width=L.content_w * 0.50,
            font_name=FONT_SANS, size=TYPE.body_sm,
        )
        draw_text(
            c, nombre_v, L.margin + 16, y - row_h + 3,
            font_name=FONT_SANS, size=TYPE.body_sm, color=NAVY,
        )
        # Z̄
        draw_text(
            c, f"{z:+.2f}σ", L.margin + L.content_w * 0.55, y - row_h + 3,
            font_name=FONT_SANS_BOLD, size=TYPE.body_sm, color=color,
        )
        # Banda
        draw_text(
            c, banda, L.margin + L.content_w * 0.70, y - row_h + 3,
            font_name=FONT_SANS, size=TYPE.body_sm, color=SLATE,
        )
        y -= row_h
    return y - 4


def draw_normal_curve(
    c,
    resultados: Sequence[dict],
    y: float,
    *,
    height: float = 100.0,
) -> float:
    """Curva normal estándar (μ=0, σ=1) con marcadores Z del paciente."""
    L = LAYOUT
    width = L.content_w
    bottom = y - height - 22

    # Datos
    z_values = [r.get("z_equivalente") for r in resultados
                if r.get("z_equivalente") is not None
                and r.get("tipo_metrica") != "ci"]
    if not z_values:
        return y

    # Título descriptivo
    from .helpers import chart_title
    y = chart_title(
        c, "Curva normal con puntajes Z del paciente",
        y, note=(
            "Eje horizontal: puntaje Z (unidades de desviación estándar). "
            "Las marcas rojas son los puntajes del paciente sobre la curva."
        ),
    )

    Z_MIN, Z_MAX = -3.5, 3.5

    def x_of(z: float) -> float:
        return L.margin + (z - Z_MIN) / (Z_MAX - Z_MIN) * width

    # Curva gaussiana — sample points
    n = 100
    max_density = 1.0 / math.sqrt(2 * math.pi)  # = ~0.3989
    pts = []
    for i in range(n + 1):
        z = Z_MIN + (Z_MAX - Z_MIN) * i / n
        density = math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
        py = bottom + (density / max_density) * height
        pts.append((x_of(z), py))

    # Banda de zona normal sombreada (-1 a 1)
    _band_pts = [(x_of(-1), bottom)]
    for px, py in pts:
        # estamos en zona [-1, 1]
        pass  # construimos abajo
    c.saveState()
    try:
        c.setFillColorRGB(0.92, 0.98, 0.93)
        c.setFillAlpha(0.8)
    except Exception as _exc:
        # §A4-fix: ReportLab antiguo — degradación silenciosa OK aquí pero loggeada.
        logger.debug("setFillAlpha no soportado en banda normal: %s", _exc)
    band_path = c.beginPath()
    band_path.moveTo(x_of(-1), bottom)
    for px, py in pts:
        z_at = Z_MIN + (Z_MAX - Z_MIN) * (px - L.margin) / width
        if -1 <= z_at <= 1:
            band_path.lineTo(px, py)
    band_path.lineTo(x_of(1), bottom)
    band_path.close()
    c.drawPath(band_path, stroke=0, fill=1)
    c.restoreState()

    # Curva en sí
    c.setStrokeColorRGB(*NAVY)
    c.setLineWidth(1.2)
    path = c.beginPath()
    path.moveTo(*pts[0])
    for px, py in pts[1:]:
        path.lineTo(px, py)
    c.drawPath(path, stroke=1, fill=0)

    # Eje X
    c.setStrokeColorRGB(*SLATE)
    c.setLineWidth(0.5)
    c.line(L.margin, bottom, L.margin + width, bottom)
    for z_val in [-3, -2, -1, 0, 1, 2, 3]:
        px = x_of(z_val)
        c.line(px, bottom, px, bottom - 3)
        draw_text(
            c, str(z_val), px, bottom - 12,
            font_name=FONT_SANS, size=TYPE.caption, color=SLATE, align="center",
        )

    # Marcadores del paciente: ticks verticales coloreados sobre la curva
    # Densidad de tick alta = peor visibilidad; sumamos jitter vertical leve
    for z in z_values:
        if z < Z_MIN or z > Z_MAX:
            continue
        px = x_of(z)
        density = math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
        ty = bottom + (density / max_density) * height
        col = semantic_color_for_z(z)
        c.setStrokeColorRGB(*col)
        c.setLineWidth(1.2)
        c.line(px, bottom, px, ty)
        c.setFillColorRGB(*col)
        c.circle(px, ty, 1.6, fill=1, stroke=0)

    # Título + leyenda
    draw_text(
        c, "Distribución del rendimiento (Z) del paciente sobre la curva normal estándar",
        L.margin, y - 8,
        font_name=FONT_SERIF, size=TYPE.title_h3, color=NAVY,
    )
    draw_text(
        c, f"n = {len(z_values)} pruebas con norma disponible",
        L.margin + width, y - 8,
        font_name=FONT_SANS, size=TYPE.micro + 0.5, color=SLATE, align="right",
    )
    return bottom - 20


def _extract_cit(resultados: Sequence[dict]) -> float | None:
    """Extrae el CIT (Cociente Intelectual Total) si está presente."""
    for r in resultados:
        if r.get("tipo_metrica") != "ci":
            continue
        tid = str(r.get("test_id", "")).lower()
        nombre = str(r.get("nombre", "")).lower()
        if "tot" in tid or "cit" in nombre or "global" in nombre:
            pe = r.get("puntaje_escalar")
            if pe is not None:
                try:
                    return float(pe)
                except (TypeError, ValueError):
                    continue
    return None


def draw_bell_curve_with_ci(
    c,
    resultados: Sequence[dict],
    y: float,
    *,
    height: float = 100.0,
    se_cit: float = 4.0,
) -> float:
    """Curva normal + bandas de intervalo de confianza 90% y 95% para el CIT.

    Si el CIT no está disponible, degrada a ``draw_normal_curve`` (sólo Z's).

    Parámetros:
        c: canvas ReportLab.
        resultados: lista de dicts con ``puntaje_escalar``, ``tipo_metrica``.
        y: posición vertical de inicio.
        height: altura de la curva en pts.
        se_cit: error estándar de medición del CIT. Por defecto 4.0 (Sattler
            2010, WISC-IV full battery). Subir a 5-7 si es forma corta.
    """
    cit = _extract_cit(resultados)
    if cit is None:
        return draw_normal_curve(c, resultados, y, height=height)

    # 1) Dibuja la curva normal estándar
    y_after = draw_normal_curve(c, resultados, y, height=height)

    # 2) Sobre la curva, dibuja la campana CIT (μ=cit, σ=15)
    L = LAYOUT
    width = L.content_w

    # Eje X de la curva va de Z = -3.5 a 3.5
    Z_MIN, Z_MAX = -3.5, 3.5
    def x_of(z: float) -> float:
        return L.margin + (z - Z_MIN) / (Z_MAX - Z_MIN) * width

    # Transformar CIT a Z: Z_cit = (CIT - 100) / 15
    z_cit = (cit - 100) / 15
    z_cit_clipped = max(Z_MIN + 0.05, min(Z_MAX - 0.05, z_cit))

    # Curva gaussiana centrada en z_cit
    n = 100
    sigma = 1.0
    max_density = 1.0 / math.sqrt(2 * math.pi)
    pts = []
    for i in range(n + 1):
        z = Z_MIN + (Z_MAX - Z_MIN) * i / n
        density = math.exp(-((z - z_cit_clipped) ** 2) / (2 * sigma * sigma)) / (sigma * math.sqrt(2 * math.pi))
        py = y_after + 22 + (density / max_density) * (height * 0.55)
        pts.append((x_of(z), py))

    # Dibujar la curva CIT (sin sombreado, sólo contorno)
    c.setStrokeColorRGB(*TEAL)
    c.setLineWidth(1.6)
    path = c.beginPath()
    path.moveTo(*pts[0])
    for px, py in pts[1:]:
        path.lineTo(px, py)
    c.drawPath(path, stroke=1, fill=0)

    # Banda IC 95% (línea más oscura, ancha)
    ic_95_lo = cit - 1.96 * se_cit
    ic_95_hi = cit + 1.96 * se_cit
    z_95_lo = (ic_95_lo - 100) / 15
    z_95_hi = (ic_95_hi - 100) / 15
    z_95_lo = max(Z_MIN + 0.05, min(Z_MAX - 0.05, z_95_lo))
    z_95_hi = max(Z_MIN + 0.05, min(Z_MAX - 0.05, z_95_hi))
    x_95_lo = x_of(z_95_lo)
    x_95_hi = x_of(z_95_hi)
    c.setStrokeColorRGB(*NAVY)
    c.setLineWidth(3.5)
    c.setFillColorRGB(*NAVY)
    c.setFillAlpha(0.20)
    c.rect(x_95_lo, y_after + 22, x_95_hi - x_95_lo, 6, fill=1, stroke=0)
    c.setFillAlpha(1.0)

    # Banda IC 90% (línea más fina encima)
    ic_90_lo = cit - 1.645 * se_cit
    ic_90_hi = cit + 1.645 * se_cit
    z_90_lo = (ic_90_lo - 100) / 15
    z_90_hi = (ic_90_hi - 100) / 15
    z_90_lo = max(Z_MIN + 0.05, min(Z_MAX - 0.05, z_90_lo))
    z_90_hi = max(Z_MIN + 0.05, min(Z_MAX - 0.05, z_90_hi))
    x_90_lo = x_of(z_90_lo)
    x_90_hi = x_of(z_90_hi)
    c.setStrokeColorRGB(*TEAL_DARK)
    c.setLineWidth(2.0)
    c.setFillColorRGB(*TEAL_DARK)
    c.setFillAlpha(0.35)
    c.rect(x_90_lo, y_after + 30, x_90_hi - x_90_lo, 4, fill=1, stroke=0)
    c.setFillAlpha(1.0)

    # Etiqueta del CIT y bandas
    label_y = y_after + 42
    draw_text(
        c, f"IC 95% [{ic_95_lo:.0f}–{ic_95_hi:.0f}]  ·  IC 90% [{ic_90_lo:.0f}–{ic_90_hi:.0f}]  ·  CIT observado: {cit:.0f}",
        L.margin, label_y,
        font_name=FONT_SANS, size=TYPE.micro + 0.5, color=NAVY,
    )

    return label_y - 8


# ──────────────────────────────────────────────────────────
# 4) DISCREPANCIAS ENTRE ÍNDICES (WISC-IV / WAIS-III)
# ──────────────────────────────────────────────────────────

DEFAULT_DISCREPANCY_PAIRS = [
    # (a, b, name, critical_15, critical_05) — WISC-IV adaptado de Wechsler
    ("ICV", "IRP", "ICV − IRP", 11, 15),
    ("ICV", "IMT", "ICV − IMT", 12, 16),
    ("ICV", "IVP", "ICV − IVP", 15, 19),
    ("IRP", "IMT", "IRP − IMT", 13, 17),
    ("IRP", "IVP", "IRP − IVP", 15, 19),
    ("IMT", "IVP", "IMT − IVP", 16, 20),
]


def _extract_indices(resultados: Sequence[dict]) -> dict[str, int]:
    """Extrae los CI compuestos del listado de resultados.

    Reconoce nombres tipo ``NiWISCIndComVer`` (→ ICV), ``NiWISCIndRazPer`` (→ IRP), etc.
    """
    mapping = {
        # WISC-IV
        "indcomver": "ICV", "icv": "ICV",
        "indrazper": "IRP", "irp": "IRP",
        "indmemtra": "IMT", "imt": "IMT",
        "indvelpro": "IVP", "ivp": "IVP",
        "tot": "CIT", "cit": "CIT", "indtot": "CIT",
        # WAIS-III
        "icp": "IRP",  # alias frecuente
    }
    out: dict[str, int] = {}
    for r in resultados:
        if r.get("tipo_metrica") != "ci":
            continue
        score = r.get("puntaje_escalar")
        if score is None:
            continue
        raw_id = str(r.get("test_id", "")).lower()
        # Buscar substring conocido
        for key, alias in mapping.items():
            if key in raw_id:
                out.setdefault(alias, int(score))
                break
    return out


def draw_discrepancies(
    c,
    resultados: Sequence[dict],
    y: float,
    *,
    pairs: Sequence[tuple[str, str, str, int, int]] = DEFAULT_DISCREPANCY_PAIRS,
) -> float:
    """Tabla visual de discrepancias entre pares de índices, con líneas críticas."""
    L = LAYOUT
    indices = _extract_indices(resultados)
    if len(indices) < 2:
        return y  # No hay suficientes índices

    # Título descriptivo
    from .helpers import chart_title
    y = chart_title(
        c, "Discrepancias entre índices",
        y, note=(
            "Líneas punteadas: tendencia (p<.15). Líneas continuas: "
            "diferencia confiable (p<.05). La barra central es la diferencia "
            "observada entre los dos índices."
        ),
    )

    # Filtrar pares aplicables (con datos)
    rows = []
    max_diff = 0
    for a, b, name, c15, c05 in pairs:
        if a not in indices or b not in indices:
            continue
        diff = indices[a] - indices[b]
        rows.append((name, indices[a], indices[b], diff, c15, c05))
        max_diff = max(max_diff, abs(diff), c05)
    if not rows:
        return y

    # Escala X
    label_w = 110
    val_w = 60
    chart_x = L.margin + label_w + val_w + 8
    chart_w = L.content_w - label_w - val_w - 16
    # Eje: simétrico, ancho = max_diff * 1.3
    scale_max = max(20, math.ceil(max_diff * 1.3))

    def x_of(diff: float) -> float:
        return chart_x + chart_w / 2 + (diff / scale_max) * (chart_w / 2)

    # Header
    draw_text(
        c, "Discrepancias entre índices",
        L.margin, y, font_name=FONT_SERIF, size=TYPE.title_h2, color=NAVY,
    )
    y -= 14
    draw_text(
        c, "Diferencia = valor del primer índice − segundo. Líneas críticas según Wechsler (p<.15 ··· y p<.05 ───).",
        L.margin, y, font_name=FONT_SANS, size=TYPE.micro + 0.5, color=SLATE,
    )
    y -= 14

    # Eje y línea central
    row_h = 18
    chart_top = y
    chart_bottom = y - row_h * len(rows)

    # Eje central
    c.setStrokeColorRGB(*SLATE)
    c.setLineWidth(0.6)
    cx = chart_x + chart_w / 2
    c.line(cx, chart_top + 4, cx, chart_bottom - 2)

    # Etiquetas eje X
    for delta in [-scale_max, -scale_max // 2, 0, scale_max // 2, scale_max]:
        px = x_of(delta)
        draw_text(
            c, str(delta), px, chart_bottom - 12,
            font_name=FONT_SANS, size=TYPE.micro + 0.5, color=SLATE, align="center",
        )

    # Filas
    for i, (name, a_val, b_val, diff, c15, c05) in enumerate(rows):
        row_y = chart_top - row_h * i - row_h / 2

        # Líneas críticas a izquierda y derecha
        for crit, dashed in [(c15, True), (c05, False)]:
            for sign in (-1, 1):
                px = x_of(sign * crit)
                c.setStrokeColorRGB(0.75, 0.25, 0.25)
                if dashed:
                    c.setDash(2, 2)
                    c.setLineWidth(0.5)
                else:
                    c.setDash()
                    c.setLineWidth(0.7)
                c.line(px, row_y + 5, px, row_y - 5)
        c.setDash()

        # Barra desde 0 hasta diff
        end_x = x_of(diff)
        # Color por significancia
        abs_d = abs(diff)
        if abs_d >= c05:
            color = SEMANTIC_DEFICIT
            tag = "p<.05"
        elif abs_d >= c15:
            color = SEMANTIC_LIMITE
            tag = "p<.15"
        else:
            color = SEMANTIC_PROMEDIO
            tag = "n.s."
        bar_x = min(cx, end_x)
        bar_w = abs(end_x - cx)
        c.setFillColorRGB(*color)
        c.rect(bar_x, row_y - 3, bar_w, 6, fill=1, stroke=0)
        c.circle(end_x, row_y, 2.0, fill=1, stroke=0)

        # Label izquierda
        draw_text(
            c, name, L.margin, row_y - 3,
            font_name=FONT_SANS_BOLD, size=TYPE.caption, color=NAVY,
        )
        # Valores
        draw_text(
            c, f"{a_val} − {b_val}", L.margin + label_w, row_y - 3,
            font_name=FONT_SANS, size=TYPE.caption, color=SLATE,
        )
        # Diff numérico
        draw_text(
            c, f"{diff:+d} ({tag})",
            chart_x + chart_w + 6, row_y - 3,
            font_name=FONT_SANS_BOLD, size=TYPE.caption, color=color,
        )
    return chart_bottom - 20


# ──────────────────────────────────────────────────────────
# 5) FILA DE "TARJETAS KPI" PARA ÍNDICES CI
# ──────────────────────────────────────────────────────────

def draw_ci_kpi_row(
    c,
    resultados: Sequence[dict],
    y: float,
) -> float:
    """Tarjetas grandes con los índices CI compuestos (estilo "métricas")."""
    L = LAYOUT
    indices_ci = [r for r in resultados
                  if r.get("tipo_metrica") == "ci"
                  and r.get("puntaje_escalar") is not None]
    if not indices_ci:
        return y

    n = len(indices_ci)
    gap = 10
    card_w = min(120.0, (L.content_w - (n - 1) * gap) / n)
    total_w = card_w * n + (n - 1) * gap
    start_x = L.margin + (L.content_w - total_w) / 2
    card_h = 64

    # Función local del helpers.kpi_card pero adaptada al contexto
    from .helpers import kpi_card, human_test_name  # local import para evitar ciclos
    for i, r in enumerate(indices_ci):
        bx = start_x + i * (card_w + gap)
        val = r.get("puntaje_escalar")
        z = r.get("z_equivalente")
        color = semantic_color_for_z(z)
        label = human_test_name(
            r.get("test_id", "") or "",
            r.get("test_nombre", "") or "",
        )
        # Normalizar nombres comunes (WISC)
        label = (label.replace("Ind ", "").replace("NiWISC", "")
                       .replace("AdWAIS", "").replace("Índice ", "")
                       .strip())[:16]
        interp = str(r.get("interpretacion", "—"))[:22]
        kpi_card(
            c, label, str(int(val)), interp, bx, y,
            w=card_w, h=card_h, accent=color,
        )
    return y - card_h - 8
