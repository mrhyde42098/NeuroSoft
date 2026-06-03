"""
report_pro.theme
=================
Paleta visual NeuroSoft + registro de fuentes Inter/Lora con fallback robusto.

Fuentes:
  - Si existen TTF en ``app/assets/fonts/`` se registran en ReportLab con los
    alias ``NSSans``, ``NSSans-Bold``, ``NSSerif`` y ``NSSerif-Bold``.
  - Si NO existen, los alias apuntan a Helvetica / Times-Roman (built-in en
    ReportLab) para no romper el build.

Llamar ``ensure_fonts_registered()`` una vez antes de dibujar cualquier texto.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────
# PALETA — NeuroSoft brand
# ──────────────────────────────────────────────────────────
# Cada color como tupla RGB normalizada (0-1) para canvas.setFillColorRGB

#: Teal principal (#0D9488)
TEAL = (0.051, 0.580, 0.533)
#: Teal oscuro para hovers/acentos (#0F766E)
TEAL_DARK = (0.059, 0.463, 0.431)
#: Teal claro decorativo (#5EEAD4)
TEAL_LIGHT = (0.369, 0.918, 0.831)
#: Teal muy claro para fondos de tarjetas (#CCFBF1)
TEAL_PALE = (0.800, 0.984, 0.945)

#: Navy slate (#1E293B) — títulos y texto principal
NAVY = (0.118, 0.161, 0.231)
#: Slate medio (#475569) — texto secundario
SLATE = (0.278, 0.333, 0.412)
#: Slate claro (#94A3B8) — texto terciario y bordes
SLATE_LIGHT = (0.580, 0.639, 0.722)

#: Crema/papel (#FAF7F0)
CREAM = (0.980, 0.969, 0.941)
#: Fondo de banda decorativa (#F1F5F9)
SURFACE = (0.945, 0.961, 0.976)

#: Blanco / negro puros
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)

# ──────────────────────────────────────────────────────────
# Colores semánticos clínicos (gradiente Z)
# ──────────────────────────────────────────────────────────
#: Z ≤ -2 (rojo crítico) #DC2626
SEMANTIC_DEFICIT = (0.863, 0.149, 0.149)
#: -2 < Z ≤ -1 (naranja) #EA580C
SEMANTIC_LIMITE = (0.918, 0.345, 0.047)
#: -1 < Z ≤ 1 (verde) #16A34A
SEMANTIC_PROMEDIO = (0.086, 0.639, 0.290)
#: 1 < Z (azul) #2563EB
SEMANTIC_SUPERIOR = (0.149, 0.388, 0.922)
#: Progreso OK en terapia (verde teal) #0D9488
SEMANTIC_OK = (0.051, 0.580, 0.533)
#: Progreso intermedio en terapia (amarillo) #CA8A04
SEMANTIC_WARN = (0.792, 0.541, 0.016)
#: Sin dato (gris) #9CA3AF
SEMANTIC_NA = (0.612, 0.639, 0.686)


def semantic_color_for_z(z: float | None) -> tuple[float, float, float]:
    """Color clínico por valor Z."""
    if z is None:
        return SEMANTIC_NA
    if z <= -2:
        return SEMANTIC_DEFICIT
    if z <= -1:
        return SEMANTIC_LIMITE
    if z <= 1:
        return SEMANTIC_PROMEDIO
    return SEMANTIC_SUPERIOR


# ──────────────────────────────────────────────────────────
# Tipografía
# ──────────────────────────────────────────────────────────
# Alias internos. Usar SIEMPRE estos nombres en canvas.setFont(...)
FONT_SANS = "NSSans"
FONT_SANS_BOLD = "NSSans-Bold"
FONT_SANS_ITALIC = "NSSans-Italic"
FONT_SERIF = "NSSerif"
FONT_SERIF_BOLD = "NSSerif-Bold"
FONT_SERIF_ITALIC = "NSSerif-Italic"

# Tamaños de tipografía por jerarquía
@dataclass(frozen=True)
class TypeScale:
    """Tamaños en puntos."""
    title_hero: float = 26.0     # Portada principal
    title_h1: float = 18.0       # Sección mayor
    title_h2: float = 13.0       # Subsección
    title_h3: float = 10.5       # Bloque dentro de subsección
    body: float = 8.5            # Cuerpo principal
    body_sm: float = 7.5         # Cuerpo secundario / dos columnas
    caption: float = 6.5         # Pies, leyendas
    micro: float = 5.5           # Marca de agua, footers


TYPE = TypeScale()


# ──────────────────────────────────────────────────────────
# Layout / espaciado
# ──────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Layout:
    """Medidas A4 en puntos (1 pt = 1/72 inch)."""
    page_w: float = 595.27
    page_h: float = 841.89
    margin: float = 42.0           # ~1.5 cm
    margin_top_header: float = 60.0
    margin_bottom_footer: float = 50.0
    gutter: float = 8.0            # gap entre columnas

    @property
    def content_w(self) -> float:
        return self.page_w - 2 * self.margin

    @property
    def content_top(self) -> float:
        return self.page_h - self.margin_top_header

    @property
    def content_bottom(self) -> float:
        return self.margin_bottom_footer


LAYOUT = Layout()


# ──────────────────────────────────────────────────────────
# Registro de fuentes (idempotente)
# ──────────────────────────────────────────────────────────
_FONTS_REGISTERED = False
_FONTS_USING_TTF = False  # True si se cargaron las TTFs custom


def _candidate_font_dirs() -> list[Path]:
    """Carpetas donde buscar TTFs (en orden de prioridad)."""
    here = Path(__file__).resolve()
    # neurosoft-backend/app/infrastructure/report_pro/theme.py
    # → subir a app/ → bajar a assets/fonts
    app_dir = here.parents[2]
    return [
        app_dir / "assets" / "fonts",
        # Alternativas si Johan las pone en otro sitio
        app_dir.parent / "assets" / "fonts",
        Path.cwd() / "neurosoft-backend" / "app" / "assets" / "fonts",
    ]


def _find_ttf(filename: str) -> Path | None:
    for d in _candidate_font_dirs():
        candidate = d / filename
        if candidate.is_file():
            return candidate
    return None


def ensure_fonts_registered() -> bool:
    """Registra las fuentes una sola vez. Retorna True si se cargaron TTFs.

    Si no encuentra los archivos, define los alias como Helvetica/Times-Roman
    y retorna False — el código que dibuja sigue funcionando idéntico.
    """
    global _FONTS_REGISTERED, _FONTS_USING_TTF
    if _FONTS_REGISTERED:
        return _FONTS_USING_TTF
    _FONTS_REGISTERED = True

    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        logger.warning("ReportLab no disponible; theme.ensure_fonts_registered no-op")
        return False

    # ── Intentar registrar TTFs ──
    # Acepta tanto archivos individuales (Inter-Regular.ttf, Lora-Regular.ttf)
    # como bundles "Inter-VariableFont_slnt,wght.ttf" si Johan baja el zip de
    # Google Fonts y lo descomprime sin renombrar.
    # Los archivos "variable" de Google Fonts (Inter[opsz,wght].ttf) contienen
    # todos los pesos (100-900) internamente; ReportLab los puede usar.
    ttf_candidates = {
        FONT_SANS: [
            "Inter-Regular.ttf", "Inter_18pt-Regular.ttf",
            "Inter[opsz,wght].ttf", "Inter-VariableFont_slnt,wght.ttf",
        ],
        FONT_SANS_BOLD: [
            "Inter-Bold.ttf", "Inter_18pt-Bold.ttf",
            # Si no hay bold estático, usamos la variable que tiene todos los pesos
            "Inter-Regular.ttf", "Inter[opsz,wght].ttf",
        ],
        FONT_SANS_ITALIC: [
            "Inter-Italic.ttf", "Inter-Italic[opsz,wght].ttf",
        ],
        FONT_SERIF: [
            "Lora-Regular.ttf", "Lora[wght].ttf", "Lora-VariableFont_wght.ttf",
        ],
        FONT_SERIF_BOLD: [
            "Lora-Bold.ttf", "Lora[wght].ttf", "Lora-Regular.ttf",
        ],
        FONT_SERIF_ITALIC: [
            "Lora-Italic.ttf", "Lora-Italic[wght].ttf",
        ],
    }

    registered: dict[str, bool] = {}
    for alias, filenames in ttf_candidates.items():
        path = None
        for fn in filenames:
            path = _find_ttf(fn)
            if path:
                break
        if path:
            try:
                pdfmetrics.registerFont(TTFont(alias, str(path)))
                registered[alias] = True
            except Exception as e:
                logger.warning("Fallo registrando %s desde %s: %s", alias, path, e)
                registered[alias] = False
        else:
            registered[alias] = False

    # ── Si alguna fuente faltó, mapear a built-in ──
    _fallback_map = {
        FONT_SANS: "Helvetica",
        FONT_SANS_BOLD: "Helvetica-Bold",
        FONT_SANS_ITALIC: "Helvetica-Oblique",
        FONT_SERIF: "Times-Roman",
        FONT_SERIF_BOLD: "Times-Bold",
        FONT_SERIF_ITALIC: "Times-Italic",
    }
    needs_fallback = False
    for alias, ok in registered.items():
        if not ok:
            needs_fallback = True
            # Re-registrar como un Type1 standard alias
            # (ReportLab acepta cualquier nombre que apunte a un built-in via Font)
            try:
                # Estrategia simple: el alias QUEDA como Helvetica/Times en setFont
                # No podemos "redefinir" Helvetica como alias, así que añadimos un mapping
                # de fuente arbitraria a la built-in via Font wrapper.
                # Solución más simple: si una fuente falta, sustituimos al usar.
                pass
            except Exception:
                pass

    _FONTS_USING_TTF = not needs_fallback
    if needs_fallback:
        logger.info(
            "report_pro: algunas fuentes TTF no encontradas — usando fallback. "
            "Aliases registrados: %s. "
            "Para diseño premium, colocar las TTFs en app/assets/fonts/.",
            {k: v for k, v in registered.items()},
        )
    else:
        logger.info("report_pro: fuentes Inter/Lora registradas correctamente.")

    return _FONTS_USING_TTF


# Mapping perezoso: si una fuente custom no se registró, devolvemos su built-in
_BUILTIN_FALLBACK = {
    FONT_SANS: "Helvetica",
    FONT_SANS_BOLD: "Helvetica-Bold",
    FONT_SANS_ITALIC: "Helvetica-Oblique",
    FONT_SERIF: "Times-Roman",
    FONT_SERIF_BOLD: "Times-Bold",
    FONT_SERIF_ITALIC: "Times-Italic",
}


def font(alias: str) -> str:
    """Retorna el nombre real de la fuente a pasar a ``c.setFont(...)``.

    Si las TTFs custom están registradas, retorna el alias tal cual.
    Si no, devuelve la built-in equivalente.
    """
    ensure_fonts_registered()
    if _FONTS_USING_TTF:
        return alias
    return _BUILTIN_FALLBACK.get(alias, alias)


def using_custom_fonts() -> bool:
    """¿Se cargaron las TTFs custom?"""
    ensure_fonts_registered()
    return _FONTS_USING_TTF
