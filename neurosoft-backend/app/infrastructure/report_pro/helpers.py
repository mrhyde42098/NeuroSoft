"""
report_pro.helpers
===================
Helpers de bajo nivel para dibujar en ReportLab canvas con la tipografía Pro.

Diseñados para componer secciones sin acoplarse a una variante concreta.
"""
from __future__ import annotations

from collections.abc import Sequence

from .theme import (
    FONT_SANS,
    FONT_SANS_BOLD,
    FONT_SERIF_BOLD,
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

    Mucho más rápido que ``pdfmetrics.stringWidth`` para wrap heurístico.
    Sobreestima ligeramente para evitar overflow.
    """
    # Promedios empíricos para Helvetica/Times: ~0.50 * size para sans, ~0.48 para serif
    if "Serif" in font_name or "Times" in font_name or "Lora" in font_name:
        return size * 0.50
    return size * 0.52


def wrap_text(text: str, max_width: float, font_name: str, size: float) -> list[str]:
    """Word-wrap heurístico (sin pdfmetrics) — produce líneas que entran en max_width.

    Maneja saltos de línea explícitos y palabras muy largas (las parte).
    """
    if not text:
        return []
    cw = char_width(font_name, size)
    chars_per_line = max(8, int(max_width / cw))
    lines: list[str] = []
    for paragraph in str(text).splitlines() or [""]:
        if not paragraph.strip():
            lines.append("")
            continue
        words = paragraph.split()
        line = ""
        for word in words:
            if not line:
                line = word
            elif len(line) + 1 + len(word) <= chars_per_line:
                line += " " + word
            else:
                lines.append(line)
                line = word
            # Palabra demasiado larga → partir
            while len(line) > chars_per_line:
                lines.append(line[:chars_per_line])
                line = line[chars_per_line:]
        if line:
            lines.append(line)
    return lines


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
        leading = size * 1.35
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
        leading = size * 1.35
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
    accent: tuple[float, float, float] = TEAL,
) -> float:
    """Título de sección H1 con barra de acento + subtítulo opcional.

    Estilo:
        ▌ TÍTULO EN MAYÚSCULAS, SERIF
          subtítulo, sans, slate
    """
    L = LAYOUT
    # Barra de acento vertical
    c.setFillColorRGB(*accent)
    c.rect(L.margin, y - TYPE.title_h1 - 2, 3, TYPE.title_h1 + 4, fill=1, stroke=0)
    # Título
    draw_text(
        c, title.upper(), L.margin + 10, y - TYPE.title_h1 + 2,
        font_name=FONT_SERIF_BOLD, size=TYPE.title_h1, color=NAVY,
    )
    y -= TYPE.title_h1 + 2
    if subtitle:
        draw_text(
            c, subtitle, L.margin + 10, y - 10,
            font_name=FONT_SANS, size=TYPE.caption, color=SLATE,
        )
        y -= 12
    # Línea inferior fina
    y -= 6
    c.setStrokeColorRGB(*SLATE_LIGHT)
    c.setLineWidth(0.4)
    c.line(L.margin, y, L.page_w - L.margin, y)
    return y - 12


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


def block_header(c, title: str, y: float, *, color=TEAL_DARK) -> float:
    """Encabezado H3 para bloques cortos (label de campo, dominio...)."""
    L = LAYOUT
    draw_text(
        c, title, L.margin, y,
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
    """Dibuja ``Label: valor`` en una línea — etiqueta en bold, valor en regular."""
    draw_text(
        c, f"{label}:", x, y,
        font_name=FONT_SANS_BOLD, size=size, color=NAVY,
    )
    val = value if value not in (None, "", "N/A") else "—"
    draw_text(
        c, str(val)[:int(value_w / char_width(FONT_SANS, size))],
        x + label_w, y, font_name=FONT_SANS, size=size, color=SLATE,
    )
    return y - size * 1.5


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
    body_h = len(body_lines) * size * 1.4
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
        cy -= size * 1.4
    return y - box_h - 4


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
    """
    # Borde + fondo
    c.setFillColorRGB(*SURFACE)
    c.setStrokeColorRGB(*accent)
    c.setLineWidth(0.8)
    c.roundRect(x, y - h, w, h, 4, fill=1, stroke=1)
    # Top stripe
    c.setFillColorRGB(*accent)
    c.rect(x, y - 4, w, 4, fill=1, stroke=0)
    # Label
    draw_text(
        c, label[:18], x + w / 2, y - 14,
        font_name=FONT_SANS_BOLD, size=TYPE.caption, color=accent, align="center",
    )
    # Value grande
    draw_text(
        c, value, x + w / 2, y - 36,
        font_name=FONT_SERIF_BOLD, size=20, color=NAVY, align="center",
    )
    # Interpretación
    draw_text(
        c, interpretation[:22], x + w / 2, y - h + 8,
        font_name=FONT_SANS, size=TYPE.micro + 0.5, color=SLATE, align="center",
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
    Retorna el nuevo y al finalizar la tabla.
    """
    # Header
    c.setFillColorRGB(*header_color)
    total_w = sum(col_widths)
    c.rect(x, y - row_h, total_w, row_h, fill=1, stroke=0)
    cx = x
    for h_text, cw in zip(headers, col_widths):
        draw_text(
            c, h_text, cx + 4, y - row_h + 4,
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
            chars = max(1, int((cw - 8) / char_width(FONT_SANS, size)))
            truncated = str(val)[:chars]
            draw_text(
                c, truncated, cx + 4, y - row_h + 4,
                font_name=FONT_SANS, size=size, color=text_color,
            )
            cx += cw
        y -= row_h
    return y


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

    Útil para datos sociodemográficos.
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
