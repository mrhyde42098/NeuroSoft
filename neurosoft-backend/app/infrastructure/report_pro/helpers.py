"""
report_pro.helpers
===================
Helpers de bajo nivel para dibujar en ReportLab canvas con la tipografía Pro.

Diseñados para componer secciones sin acoplarse a una variante concreta.
"""
from __future__ import annotations

from collections.abc import Sequence

from reportlab.pdfbase import pdfmetrics

from .theme import (
    ACCENT,
    FONT_SANS,
    FONT_SANS_BOLD,
    FONT_SANS_ITALIC,
    FONT_SERIF,
    FONT_SERIF_BOLD,
    FONT_SERIF_ITALIC,
    HAIRLINE,
    LAYOUT,
    NAVY,
    SLATE,
    SLATE_LIGHT,
    SURFACE,
    TEAL,
    TEAL_DARK,
    TEAL_PALE,
    TYPE,
    WHITE,
    font,
)

# ──────────────────────────────────────────────────────────
# Texto: medición y wrap
# ──────────────────────────────────────────────────────────

def char_width(font_name: str, size: float) -> float:
    """Ancho aproximado en puntos por carácter para un tipo + tamaño dados.

    Usado como fallback cuando la fuente aún no está registrada (p.ej. tests
    que no invocan ``ensure_fonts_registered()``). Prefiere ``measure_text``.
    """
    if "Serif" in font_name or "Times" in font_name or "Lora" in font_name:
        return size * 0.50
    return size * 0.52


def measure_text(text: str, font_name: str, size: float) -> float:
    """Ancho en puntos de ``text`` con la fuente PostScript real.

    Usa ``pdfmetrics.stringWidth`` (resuelve aliases Inter/Lora/Helvetica/Times).
    Si la fuente aún no está registrada, cae al heurístico ``char_width``.
    """
    if not text:
        return 0.0
    try:
        return pdfmetrics.stringWidth(text, font(font_name), size)
    except Exception:
        return len(str(text)) * char_width(font_name, size)


def _truncate_to_width(text: str, font_name: str, size: float, max_width: float) -> str:
    """Recorta ``text`` con elipsis (…) para que entre en ``max_width`` puntos."""
    if not text:
        return text
    s = str(text)
    if measure_text(s, font_name, size) <= max_width:
        return s
    ellipsis = "…"
    while s and measure_text(s + ellipsis, font_name, size) > max_width:
        s = s[:-1]
    return s + ellipsis if s else ellipsis


def wrap_text(text: str, max_width: float, font_name: str, size: float) -> list[str]:
    """Word-wrap usando ``pdfmetrics.stringWidth`` real.

    Maneja saltos de línea explícitos (``\\n``) y parte palabras demasiado
    largas para una línea (las corta con guion visual "-").

    No produce overflow: cada línea tiene ``measure_text(line) <= max_width``.
    """
    if not text:
        return []
    lines: list[str] = []
    space_w = measure_text(" ", font_name, size)
    hyphen_w = measure_text("-", font_name, size)

    for paragraph in str(text).splitlines() or [""]:
        if not paragraph.strip():
            lines.append("")
            continue
        words = paragraph.split()
        line = ""
        line_w = 0.0
        for word in words:
            word_w = measure_text(word, font_name, size)
            # Palabra sola más ancha que la línea → partir por glifos
            if word_w > max_width and not line:
                chunk = ""
                chunk_w = 0.0
                for ch in word:
                    ch_w = measure_text(ch, font_name, size)
                    if chunk_w + ch_w + hyphen_w > max_width and chunk:
                        lines.append(chunk + "-")
                        chunk = ch
                        chunk_w = ch_w
                    else:
                        chunk += ch
                        chunk_w += ch_w
                if chunk:
                    line = chunk
                    line_w = chunk_w
                continue
            # ¿Cabe la palabra en la línea actual?
            tentative = line_w + (space_w if line else 0) + word_w
            if tentative <= max_width or not line:
                if line:
                    line += " " + word
                    line_w = tentative
                else:
                    line = word
                    line_w = word_w
            else:
                lines.append(line)
                line = word
                line_w = word_w
        if line:
            lines.append(line)
    return lines


def fit_text_to_width(
    text: str,
    max_width: float,
    font_name: str,
    size: float,
    ellipsis: str = "\u2026",
) -> str:
    """Trunca ``text`` con elipsis para que quepa en ``max_width``.

    Usa ``pdfmetrics.stringWidth`` real, glifo a glifo cuando es necesario.
    Si el texto ya cabe, se devuelve intacto. No produce strings más anchos
    que ``max_width`` (midiendo con la misma fuente/tamaño).
    """
    if not text:
        return text or ""
    if measure_text(text, font_name, size) <= max_width:
        return text
    ell_w = measure_text(ellipsis, font_name, size)
    if ell_w >= max_width:
        # No hay espacio ni para la elipsis — devolver string vacío.
        return ""
    out = ""
    for ch in text:
        candidate = out + ch
        if measure_text(candidate, font_name, size) + ell_w > max_width:
            return out + ellipsis
        out = candidate
    return out


def draw_text(
    c,
    text: str,
    x: float,
    y: float,
    *,
    font_name: str = FONT_SANS,
    size: float = TYPE.body,
    color: tuple[float, float, float] = NAVY,
    align: str = "left",
) -> None:
    """Dibuja una sola línea de texto con la fuente real (resuelve alias)."""
    c.setFillColorRGB(*color)
    c.setFont(font(font_name), size)
    if align == "center":
        c.drawCentredString(x, y, text)
    elif align == "right":
        c.drawRightString(x, y, text)
    else:
        c.drawString(x, y, text)


def draw_paragraph(
    c,
    text: str,
    x: float,
    y: float,
    w: float,
    *,
    font_name: str = FONT_SANS,
    size: float = TYPE.body,
    color: tuple[float, float, float] = SLATE,
    leading: float | None = None,
) -> float:
    """Dibuja un párrafo con word-wrap. Retorna el nuevo ``y`` después del bloque.

    No pagina automáticamente — usa ``new_page_if_needed`` antes si hace falta.
    """
    if not text or not str(text).strip():
        return y
    if leading is None:
        leading = size * 1.45
    lines = wrap_text(text, w, font_name, size)
    c.setFillColorRGB(*color)
    c.setFont(font(font_name), size)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def measure_paragraph_height(
    text: str, w: float, *, font_name: str = FONT_SANS, size: float = TYPE.body,
    leading: float | None = None,
) -> float:
    """Altura total en puntos que ocuparía un párrafo si se dibujara."""
    if not text:
        return 0.0
    if leading is None:
        leading = size * 1.45
    lines = wrap_text(text, w, font_name, size)
    return len(lines) * leading


# ──────────────────────────────────────────────────────────
# Bandas, separadores, viñetas
# ──────────────────────────────────────────────────────────

def section_title(
    c,
    title: str,
    y: float,
    *,
    subtitle: str | None = None,
    accent: tuple[float, float, float] = ACCENT,
) -> float:
    """Encabezado de sección — estilo editorial clínico.

    Antes: ``▌ TÍTULO EN MAYÚSCULAS SERIF`` (pesado, aspecto de plantilla).
    Ahora: una *kicker rule* corta de acento, el título en serif en
    caja mixta (sin gritar en mayúsculas), un subtítulo en cursiva y una
    hairline cálida a todo el ancho. Más cercano a un informe clínico real
    que a un dashboard.

    Sólo consume espacio hacia abajo desde ``y`` (no dibuja por encima),
    para no solaparse con el contenido previo.
    """
    L = LAYOUT
    # Kicker: regla corta de acento como "eyebrow" editorial
    c.setFillColorRGB(*accent)
    c.rect(L.margin, y - 3, 28, 2.2, fill=1, stroke=0)
    y -= 13
    # Título en serif, caja mixta (respeta el casing que envía el caller)
    size_t = TYPE.title_h1 - 2.0  # ~16 pt — refinado, no monumental
    draw_text(
        c, title, L.margin, y - size_t,
        font_name=FONT_SERIF_BOLD, size=size_t, color=NAVY,
    )
    y -= size_t + 5
    if subtitle:
        draw_text(
            c, subtitle, L.margin, y - TYPE.caption,
            font_name=FONT_SERIF_ITALIC, size=TYPE.caption + 0.5, color=SLATE,
        )
        y -= TYPE.caption + 7
    else:
        y -= 2
    # Hairline cálida a todo el ancho
    c.setStrokeColorRGB(*HAIRLINE)
    c.setLineWidth(0.7)
    c.line(L.margin, y, L.page_w - L.margin, y)
    return y - 13


def section_subtitle(c, title: str, y: float) -> float:
    """Subtítulo H2 con underline sutil."""
    L = LAYOUT
    draw_text(
        c, title, L.margin, y - TYPE.title_h2,
        font_name=FONT_SERIF_BOLD, size=TYPE.title_h2, color=NAVY,
    )
    y -= TYPE.title_h2 + 2
    c.setStrokeColorRGB(*TEAL)
    c.setLineWidth(0.6)
    c.line(L.margin, y, L.margin + 40, y)
    return y - 8


def chart_title(
    c,
    title: str,
    y: float,
    *,
    note: str | None = None,
) -> float:
    """Título descriptivo para gráficos — combina nombre + nota opcional.

    A diferencia de ``section_title``, este es más compacto: se usa encima
    de cada gráfico (radar, gaussiana, perfil Z, discrepancias) para que
    el lector entienda qué está viendo sin tener que descifrar el
    contenido de la imagen.

    Args:
        title: nombre del gráfico (p.ej. "Perfil cognitivo por dominio").
        note:  nota pequeña debajo, p.ej. "verde = rango normal (-1 a +1 σ)".

    Returns:
        ``y`` actualizado tras dibujar el título.
    """
    L = LAYOUT
    # Eyebrow: nombre del gráfico en sans-bold, caja mixta, ancla discreta
    draw_text(
        c, title, L.margin, y - 8,
        font_name=FONT_SANS_BOLD, size=TYPE.body + 0.5, color=NAVY,
    )
    y -= 13
    if note:
        draw_text(
            c, note, L.margin, y - 7,
            font_name=FONT_SANS_ITALIC, size=TYPE.micro + 0.5, color=SLATE,
        )
        y -= 10
    return y - 2


# ──────────────────────────────────────────────────────────
# Nombres humanos para pruebas (fallback si test_nombre falta)
# ──────────────────────────────────────────────────────────

# Mapa test_id → nombre legible. Cobertura básica para los IDs más comunes.
# Si el ID no está, el caller debe haber recibido el nombre desde el motor
# (``prueba.nombre``). Este mapa es el ÚLTIMO recurso — si llega aquí, el
# motor entregó algo inesperado y preferimos mostrar algo legible a un
# identificador técnico tipo "NiWiscDC".
TEST_ID_TO_HUMAN: dict[str, str] = {
    "NiWiscDC": "Diseño con Cubos",
    "NiWiscSem": "Semejanzas",
    "NiWiscRDD": "Retención de Dígitos",
    "NiWiscConD": "Conceptos con Dibujos",
    "NiWiscCl": "Claves",
    "NiWiscVoc": "Vocabulario",
    "NiWiscLN": "Letras y Números",
    "NiWiscMat": "Matrices",
    "NiWiscCom": "Comprensión",
    "NiWiscBusSim": "Búsqueda de Símbolos",
    "NiWiscAri": "Aritmética",
    "NiWISCIndComVer": "Índice Comprensión Verbal",
    "NiWISCIndRazPer": "Índice Razonamiento Perceptual",
    "NiWISCIndMemTra": "Índice Memoria de Trabajo",
    "NiWISCIndVelPro": "Índice Velocidad de Procesamiento",
    "NiWISCTot": "CI Total",
    "NiWISCIndCapGen": "Índice Capacidad General",
    "NiWISCIndCopCog": "Índice Competencia Cognitiva",
    "AdWAISA": "Aritmética",
    "AdWAISC": "Comprensión",
    "AdWAISCC": "Claves de Símbolos",
    "AdWAISFI": "Figuras Incompletas",
    "AdWAISHI": "Historias",
    "AdWAISI": "Información",
    "AdWAISL": "Letras y Números",
    "AdWAISRO": "Diseño con Cubos",
    "AdWAISV": "Vocabulario",
    "AdWAISICV": "Índice Comprensión Verbal",
    "AdWAISICP": "Índice Razonamiento Perceptual",
    "AdWAISIMT": "Índice Memoria de Trabajo",
    "AdWAISIVP": "Índice Velocidad de Procesamiento",
    "AdWAISEMan": "Índice Manipulación Mental",
    "AdWAISTot": "CI Total",
    "ViTMTA": "Trail Making Test A",
    "ViTMTB": "Trail Making Test B",
    "ViRDD": "Retención de Dígitos Directos",
    "ViRDInv": "Retención de Dígitos Inversos",
    "ViStP": "Stroop Palabra",
    "ViStC": "Stroop Color",
    "ViStPC": "Stroop Palabra-Color",
    "ViGroberRLT": "Grober Recuerdo Libre Total",
    "ViGroberRT": "Grober Recuerdo Total",
    "ViGroberMC_Tot": "Grober Memoria con Claves",
    "ViGroberML_Tot": "Grober Memoria Libre",
    "ViAni": "Fluidez Animales",
    "ViYesavage": "Yesavage (Depresión Geriátrica)",
    "NiSpaDC": "Span Dígitos Directo",
    "NiSpaDI": "Span Dígitos Inverso",
    "NiTMTA": "Trail Making Test A",
    "NiTMTB": "Trail Making Test B",
}


def human_test_name(test_id: str, test_nombre: str | None = None) -> str:
    """Resuelve el nombre legible de una prueba.

    Prioridad:
        1. ``test_nombre`` (lo que devuelve el motor de scoring).
        2. Mapa ``TEST_ID_TO_HUMAN`` (fallback de seguridad).
        3. ``test_id`` con la primera letra en mayúscula (último recurso,
           evita el aspecto robótico tipo "NiWiscDC" si falla todo).

    Esta función es la ÚNICA vía autorizada para resolver el nombre de
    una prueba antes de imprimirla. Nunca uses ``r["test_id"]`` directo
    en el PDF — siempre pasa por acá.
    """
    if test_nombre and test_nombre.strip() and test_nombre != test_id:
        return test_nombre.strip()
    if test_id in TEST_ID_TO_HUMAN:
        return TEST_ID_TO_HUMAN[test_id]
    if test_id:
        # Último recurso: humanizar el ID
        # "NiWiscDC" -> "Ni Wisc DC" -> "Prueba Wisc DC"
        pretty = test_id.replace("Ni", "Niño ").replace("Ad", "Adulto ").replace("Vi", "AM ")
        return pretty.strip() or "Prueba aplicada"
    return "Prueba aplicada"


def block_header(
    c, title: str, y: float, *, color=TEAL_DARK, x: float | None = None,
) -> float:
    """Encabezado H3 para bloques cortos (label de campo, dominio...).

    Args:
        x: posición horizontal opcional. Si es ``None`` (default), usa
           ``LAYOUT.margin`` — útil para layouts de una sola columna.
           En layouts de dos columnas, pasar ``L.margin`` para la columna
           izquierda y ``L.margin + col_w + gap`` para la derecha, para
           evitar que ambas cabeceras se solapen en el mismo ``x``.
    """
    L = LAYOUT
    draw_text(
        c, title, x if x is not None else L.margin, y,
        font_name=FONT_SANS_BOLD, size=TYPE.title_h3, color=color,
    )
    return y - TYPE.title_h3 - 2


def divider(c, y: float, *, color=SLATE_LIGHT, weight: float = 0.4) -> float:
    L = LAYOUT
    c.setStrokeColorRGB(*color)
    c.setLineWidth(weight)
    c.line(L.margin, y, L.page_w - L.margin, y)
    return y - 6


def bullet(
    c, text: str, x: float, y: float, w: float,
    *, marker: str = "•", indent: float = 12.0, size: float = TYPE.body_sm,
) -> float:
    """Viñeta con texto wrapping. Retorna nuevo y."""
    draw_text(c, marker, x, y, font_name=FONT_SANS_BOLD, size=size, color=TEAL_DARK)
    return draw_paragraph(
        c, text, x + indent, y, w - indent,
        font_name=FONT_SANS, size=size, color=SLATE,
    )


def field_pair(
    c,
    label: str,
    value: str,
    x: float,
    y: float,
    *,
    label_w: float = 80.0,
    value_w: float = 200.0,
    size: float = TYPE.body_sm,
) -> float:
    """Dibuja ``Label: valor`` en una línea — etiqueta en bold, valor en regular.

    El valor se trunca con elipsis (…) si excede ``value_w`` puntos (medido
    con ``pdfmetrics.stringWidth``). La etiqueta se trunca igual si excede
    ``label_w``. Line-height: ``size * 1.8`` (espacio respiratorio para 2 líneas).
    """
    # Etiqueta: truncar con elipsis si no cabe
    label_text = f"{label}:"
    label_text = _truncate_to_width(label_text, FONT_SANS_BOLD, size, label_w)
    draw_text(
        c, label_text, x, y,
        font_name=FONT_SANS_BOLD, size=size, color=NAVY,
    )
    val = value if value not in (None, "", "N/A") else "—"
    val_str = _truncate_to_width(str(val), FONT_SANS, size, value_w)
    draw_text(
        c, val_str, x + label_w, y, font_name=FONT_SANS, size=size, color=SLATE,
    )
    return y - size * 1.8


# ──────────────────────────────────────────────────────────
# Paginación
# ──────────────────────────────────────────────────────────

def new_page_if_needed(c, y: float, *, need: float = 80.0) -> tuple[float, bool]:
    """Si no queda espacio para ``need`` puntos, salta de página.

    Retorna ``(new_y, did_break)``.
    """
    L = LAYOUT
    if y - need < L.content_bottom:
        c.showPage()
        return L.content_top, True
    return y, False


# ──────────────────────────────────────────────────────────
# Cajas decorativas
# ──────────────────────────────────────────────────────────

def callout(
    c,
    text: str,
    x: float,
    y: float,
    w: float,
    *,
    accent: tuple[float, float, float] = TEAL,
    fill: tuple[float, float, float] = TEAL_PALE,
    title: str | None = None,
    padding: float = 8.0,
    size: float = TYPE.body_sm,
) -> float:
    """Caja informativa con borde lateral de acento (estilo "callout")."""
    inner_w = w - 2 * padding - 4
    title_h = 0
    if title:
        title_h = TYPE.title_h3 + 4
    body_lines = wrap_text(text, inner_w, FONT_SANS, size)
    body_h = len(body_lines) * size * 1.5
    box_h = padding * 2 + title_h + body_h + 2

    c.setFillColorRGB(*fill)
    c.rect(x, y - box_h, w, box_h, fill=1, stroke=0)
    c.setFillColorRGB(*accent)
    c.rect(x, y - box_h, 3, box_h, fill=1, stroke=0)

    inner_y = y - padding
    if title:
        draw_text(
            c, title, x + padding + 4, inner_y - TYPE.title_h3,
            font_name=FONT_SANS_BOLD, size=TYPE.title_h3, color=NAVY,
        )
        inner_y -= title_h
    c.setFillColorRGB(*NAVY)
    c.setFont(font(FONT_SANS), size)
    cy = inner_y - size
    for line in body_lines:
        c.drawString(x + padding + 4, cy, line)
        cy -= size * 1.5
    return y - box_h - 4


def field_grid(
    c,
    items: Sequence[tuple[str, str]],
    x: float,
    y: float,
    w: float,
    *,
    cols: int = 3,
    row_h: float = 34.0,
    size: float = TYPE.body_sm,
    placeholder: str = "—",
) -> float:
    """Rejilla de campos etiquetados con borde (estilo ficha IN&S).

    Cada celda muestra ``ETIQUETA`` arriba (caption) y el valor abajo (body).
    Dibuja borde externo + hairlines internas. Retorna el ``y`` inferior.
    """
    if not items:
        return y
    n = len(items)
    rows = (n + cols - 1) // cols
    col_w = w / cols
    grid_h = rows * row_h

    # Fondo + borde externo
    c.setFillColorRGB(*WHITE)
    c.setStrokeColorRGB(*HAIRLINE)
    c.setLineWidth(0.7)
    c.rect(x, y - grid_h, w, grid_h, fill=1, stroke=1)

    # Hairlines internas
    c.setStrokeColorRGB(*HAIRLINE)
    c.setLineWidth(0.4)
    for r in range(1, rows):
        ly = y - r * row_h
        c.line(x, ly, x + w, ly)
    for cc in range(1, cols):
        lx = x + cc * col_w
        c.line(lx, y - grid_h, lx, y)

    pad = 7.0
    for idx, (label, value) in enumerate(items):
        r = idx // cols
        cc = idx % cols
        cx = x + cc * col_w
        cy = y - r * row_h
        draw_text(
            c, label.upper(), cx + pad, cy - pad - TYPE.caption + 2,
            font_name=FONT_SANS_BOLD, size=TYPE.caption, color=ACCENT,
        )
        val = value if (value and str(value).strip() and str(value) not in ("N/A", "")) else placeholder
        val_str = _truncate_to_width(str(val), FONT_SANS, size, col_w - 2 * pad)
        draw_text(
            c, val_str, cx + pad, cy - row_h + pad + 2,
            font_name=FONT_SANS, size=size, color=NAVY,
        )
    return y - grid_h


def measure_info_box(
    value: str,
    w: float,
    *,
    size: float = TYPE.body,
    label_lines: int = 1,
    placeholder: str = "No reportado",
) -> float:
    """Altura total que ocuparía un ``info_box`` con este contenido y ancho."""
    pad = 9.0
    inner_w = w - 2 * pad
    text = value if (value and str(value).strip() and str(value) not in ("N/A", "-", "(-)")) else placeholder
    body_lines = wrap_text(str(text), inner_w, FONT_SANS, size)
    body_h = max(1, len(body_lines)) * size * 1.42
    label_h = label_lines * (TYPE.caption + 4)
    return pad + label_h + body_h + pad


def info_box(
    c,
    label: str,
    value: str,
    x: float,
    y: float,
    w: float,
    *,
    size: float = TYPE.body,
    placeholder: str = "No reportado",
    accent: tuple[float, float, float] = ACCENT,
    fill: tuple[float, float, float] = WHITE,
) -> float:
    """Caja etiquetada estilo IN&S: encabezado de campo + valor en caja con borde.

    Muestra ``placeholder`` (en cursiva, gris) cuando el valor está vacío, para
    que todas las áreas figuren en el informe aunque no se diligencien — igual
    que el formato IN&S. El texto del valor se imprime **verbatim**.

    Retorna el ``y`` inferior de la caja.
    """
    pad = 9.0
    inner_w = w - 2 * pad
    is_empty = not (value and str(value).strip() and str(value) not in ("N/A", "-", "(-)"))
    text = placeholder if is_empty else str(value)
    body_lines = wrap_text(text, inner_w, FONT_SANS, size)
    body_h = max(1, len(body_lines)) * size * 1.42
    label_h = TYPE.caption + 4
    box_h = pad + label_h + body_h + pad

    # Caja
    c.setFillColorRGB(*fill)
    c.setStrokeColorRGB(*HAIRLINE)
    c.setLineWidth(0.7)
    c.roundRect(x, y - box_h, w, box_h, 3, fill=1, stroke=1)
    # Acento lateral
    c.setFillColorRGB(*accent)
    c.rect(x, y - box_h, 2.4, box_h, fill=1, stroke=0)

    # Etiqueta (eyebrow)
    draw_text(
        c, label.upper(), x + pad, y - pad - TYPE.caption + 2,
        font_name=FONT_SANS_BOLD, size=TYPE.caption, color=accent,
    )
    # Valor
    cy = y - pad - label_h - size
    color = SLATE_LIGHT if is_empty else NAVY
    fnt = FONT_SANS_ITALIC if is_empty else FONT_SANS
    c.setFillColorRGB(*color)
    c.setFont(font(fnt), size)
    for line in body_lines:
        c.drawString(x + pad, cy, line)
        cy -= size * 1.42
    return y - box_h


def kpi_card(
    c,
    label: str,
    value: str,
    interpretation: str,
    x: float,
    y: float,
    *,
    w: float = 110.0,
    h: float = 56.0,
    accent: tuple[float, float, float] = TEAL,
) -> None:
    """Tarjeta con un valor grande tipo "métrica clínica".

    Diseñada para los índices CIT/ICV/IRP… en la sección de resultados.
    El label y la interpretation se truncan con elipsis según el ancho real
    (medido con ``pdfmetrics.stringWidth``), no por número de caracteres
    heurístico. La interpretation baja a ``size=TYPE.micro`` si no cabe.
    """
    # Borde + fondo
    c.setFillColorRGB(*SURFACE)
    c.setStrokeColorRGB(*accent)
    c.setLineWidth(0.8)
    c.roundRect(x, y - h, w, h, 4, fill=1, stroke=1)
    # Top stripe
    c.setFillColorRGB(*accent)
    c.rect(x, y - 4, w, 4, fill=1, stroke=0)
    # Label: truncar con elipsis al ancho real
    label_max_w = w - 12
    label_text = _truncate_to_width(label, FONT_SANS_BOLD, TYPE.caption, label_max_w)
    draw_text(
        c, label_text, x + w / 2, y - 14,
        font_name=FONT_SANS_BOLD, size=TYPE.caption, color=accent, align="center",
    )
    # Value grande
    draw_text(
        c, value, x + w / 2, y - 36,
        font_name=FONT_SERIF_BOLD, size=20, color=NAVY, align="center",
    )
    # Interpretación: bajar de tamaño si no cabe
    inter_max_w = w - 12
    inter_size = TYPE.micro + 0.5
    inter_text = _truncate_to_width(interpretation, FONT_SANS, inter_size, inter_max_w)
    if interpretation and inter_text.endswith("…") and inter_text != interpretation:
        # Si truncó, intentar con un punto menos (sin elipsis) a menor tamaño
        inter_size = TYPE.micro
        inter_text = _truncate_to_width(interpretation, FONT_SANS, inter_size, inter_max_w)
    draw_text(
        c, inter_text, x + w / 2, y - h + 8,
        font_name=FONT_SANS, size=inter_size, color=SLATE, align="center",
    )


# ──────────────────────────────────────────────────────────
# Tablas simples (alternancia + colores)
# ──────────────────────────────────────────────────────────

def draw_table(
    c,
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    col_widths: Sequence[float],
    x: float,
    y: float,
    *,
    row_h: float = 14.0,
    header_color: tuple[float, float, float] = NAVY,
    header_text_color: tuple[float, float, float] = WHITE,
    zebra_color: tuple[float, float, float] = SURFACE,
    row_colors: list[tuple[float, float, float] | None] | None = None,
    size: float = TYPE.body_sm,
) -> float:
    """Tabla simple con cabecera coloreada y filas alternas.

    ``row_colors[i]`` (si se pasa) pinta el texto de toda la fila i de ese color.
    Retorna el nuevo y al finalizar la tabla. Las celdas se truncan con elipsis
    según el ancho real de cada columna (``pdfmetrics.stringWidth``).
    """
    # Header
    c.setFillColorRGB(*header_color)
    total_w = sum(col_widths)
    c.rect(x, y - row_h, total_w, row_h, fill=1, stroke=0)
    cx = x
    for h_text, cw in zip(headers, col_widths):
        header_max_w = cw - 8
        h_trunc = _truncate_to_width(h_text, FONT_SANS_BOLD, size, header_max_w)
        draw_text(
            c, h_trunc, cx + 4, y - row_h + 4,
            font_name=FONT_SANS_BOLD, size=size, color=header_text_color,
        )
        cx += cw
    y -= row_h

    # Body
    for i, row in enumerate(rows):
        # Zebra
        if i % 2 == 1:
            c.setFillColorRGB(*zebra_color)
            c.rect(x, y - row_h, total_w, row_h, fill=1, stroke=0)
        text_color = row_colors[i] if row_colors and i < len(row_colors) and row_colors[i] else SLATE
        cx = x
        for val, cw in zip(row, col_widths):
            cell_max_w = cw - 8
            cell_text = _truncate_to_width(str(val), FONT_SANS, size, cell_max_w)
            draw_text(
                c, cell_text, cx + 4, y - row_h + 4,
                font_name=FONT_SANS, size=size, color=text_color,
            )
            cx += cw
        y -= row_h
    return y


def two_column_blocks(
    c,
    *,
    x: float,
    y: float,
    width: float,
    gap: float = 12.0,
    left_title: str,
    left_color: tuple[float, float, float],
    left_items: Sequence[str],
    right_title: str,
    right_color: tuple[float, float, float],
    right_items: Sequence[str],
    ensure_room_fn=None,
    bullet_size: float = TYPE.body_sm,
) -> float:
    """Dibuja DOS bloques (fortalezas vs áreas) en paralelo.

    Ambos bloques están a la misma altura y se extienden hacia abajo de
    forma independiente. Retorna el ``y`` mínimo de los dos.

    Args:
        x, width: coordenadas y ancho total disponible.
        gap: separación entre las dos columnas.
        left_title, right_title: títulos de cada bloque.
        left_color, right_color: color del acento de cada bloque.
        left_items, right_items: bullets a dibujar.
        ensure_room_fn: callable ``(c, y, need) -> y`` para paginar.
        bullet_size: tamaño de fuente para los bullets.
    """
    col_w = (width - gap) / 2
    x_left = x
    x_right = x + col_w + gap
    # Adaptar ensure_room_fn a interfaz (c, y, need) -> y.
    # Si el caller pasa self._ensure_room (firma c, data, y, need=80),
    # hay que reenvolver para que el orden coincida.
    if ensure_room_fn is not None:
        import inspect
        try:
            sig = inspect.signature(ensure_room_fn)
            n_params = len([p for p in sig.parameters.values()
                            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)])
        except (TypeError, ValueError):
            n_params = 3
        if n_params >= 4:
            # Firma (c, data, y, need). Necesitamos pasar `data` extra.
            # Lo capturamos vía __self__ del bound method, o lo pedimos al caller.
            data_arg = getattr(ensure_room_fn, "__self__", None)
            if data_arg is not None:
                # Bound method: self ya está bound, así que pasamos
                # (c, data, y, need) directamente.
                ensure = lambda c, y, need, _f=ensure_room_fn, _d=data_arg: _f(c, _d, y, need)
            else:
                # Función suelta con (c, data, y, need) — el caller
                # probablemente olvidó pasar self. Como fallback, usamos
                # ensure_room_fn.__defaults__ si existe.
                ensure = ensure_room_fn
        else:
            ensure = ensure_room_fn
    else:
        ensure = lambda c, y, need: y
    y_left = y
    y_right = y
    y_left = ensure(c, y_left, 40)
    y_left = block_header(c, left_title, y_left, color=left_color, x=x_left)
    if not left_items:
        y_left = draw_paragraph(
            c, "—", x_left, y_left - 4, col_w,
            font_name=FONT_SANS, size=TYPE.caption, color=SLATE_LIGHT,
            leading=TYPE.caption * 1.4,
        )
    else:
        for frase in left_items[:5]:
            y_left = ensure(c, y_left, 32)
            y_left = bullet(c, frase, x_left, y_left - 2, col_w) - 2
    y_right = ensure(c, y_right, 40)
    y_right = block_header(c, right_title, y_right, color=right_color, x=x_right)
    if not right_items:
        y_right = draw_paragraph(
            c, "—", x_right, y_right - 4, col_w,
            font_name=FONT_SANS, size=TYPE.caption, color=SLATE_LIGHT,
            leading=TYPE.caption * 1.4,
        )
    else:
        for frase in right_items[:5]:
            y_right = ensure(c, y_right, 32)
            y_right = bullet(c, frase, x_right, y_right - 2, col_w) - 2
    return min(y_left, y_right)


def two_column_layout(
    c,
    items: Sequence[tuple[str, str]],
    x: float,
    y: float,
    *,
    column_w: float = 240.0,
    gap: float = 16.0,
    size: float = TYPE.body_sm,
) -> float:
    """Dibuja una lista de (label, value) en dos columnas balanceadas.

    Útil para datos sociodemográficos. Las dos columnas se alinean al fondo
    usando ``min(y_left, y_right)`` para que las dos líneas inferiores coincidan.
    """
    if not items:
        return y
    mid = (len(items) + 1) // 2
    left = items[:mid]
    right = items[mid:]
    y_left, y_right = y, y
    label_w = 90
    value_w = column_w - label_w - 4
    for lbl, val in left:
        y_left = field_pair(
            c, lbl, val, x, y_left,
            label_w=label_w, value_w=value_w, size=size,
        )
    for lbl, val in right:
        y_right = field_pair(
            c, lbl, val, x + column_w + gap, y_right,
            label_w=label_w, value_w=value_w, size=size,
        )
    return min(y_left, y_right)
