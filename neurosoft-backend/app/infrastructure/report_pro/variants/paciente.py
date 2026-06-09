"""
Variante "Paciente" — versión del informe en lenguaje claro para el paciente
y su familia. (S3.2)

Características:
  - Sin portada dedicada.
  - Lenguaje claro, sin percentiles ni jerga técnica.
  - Estructura: bienvenida → qué hicimos → qué encontramos →
    implicaciones diarias → fortalezas → recomendaciones → preguntas frecuentes.
  - Mención explícita de que el informe técnico completo está disponible
    con el profesional tratante.
  - 2-3 páginas, apto para imprimir y llevar a casa.
"""

from __future__ import annotations

from ..base import NeuroPDFGeneratorPro
from ..helpers import (
    block_header,
    bullet,
    callout,
    draw_paragraph,
    section_title,
)
from ..implicaciones import dominios_con_implicaciones, titulo_implicacion_humano
from ..narrative import generar_resumen_paciente, parse_recomendaciones
from ..theme import (
    CREAM,
    FONT_SANS,
    FONT_SANS_BOLD,
    FONT_SERIF,
    FONT_SERIF_BOLD,
    LAYOUT,
    NAVY,
    SEMANTIC_DEFICIT,
    SEMANTIC_LIMITE,
    SEMANTIC_SUPERIOR,
    SLATE,
    SURFACE,
    TEAL,
    TEAL_DARK,
    TYPE,
)


class PacienteGenerator(NeuroPDFGeneratorPro):
    VARIANT_LABEL = "Versión para el Paciente"
    VARIANT_SUBTITLE = "Resumen de la Evaluación en Lenguaje Claro"
    USE_COVER = False
    INCLUDE_ANNEX = False

    def _resumen_data(self, data) -> dict:
        recomendaciones: list[str] = []
        if data.obs_recomendaciones and data.obs_recomendaciones not in ("N/A", ""):
            for grupo in parse_recomendaciones(data.obs_recomendaciones).values():
                for it in grupo:
                    recomendaciones.append(it["texto"])
        return generar_resumen_paciente(
            data.resultados or [],
            paciente_nombre=data.nombre_completo or "",
            recomendaciones=recomendaciones,
            **self._kwargs_resumen_paciente(data),
        )

    def _build_pages(self, c, data) -> None:
        y = self._page_top_with_header(c, data)
        y = self._section_sello_paciente(c, data, y)
        y = self._section_saludo(c, data, y)
        y = self._section_que_hicimos(c, data, y)
        y = self._section_que_encontramos(c, data, y)
        y = self._section_implicaciones_paciente(c, data, y)
        y = self._section_fortalezas_apoyo(c, data, y)
        y = self._section_recomendaciones_paciente(c, data, y)
        y = self._section_faq(c, data, y)
        y = self._section_aviso_informe_tecnico(c, data, y)
        self._section_firma(c, data, y)

    def _section_sello_paciente(self, c, data, y: float) -> float:
        L = LAYOUT
        c.setFillColorRGB(*TEAL)
        c.rect(L.margin, y - 36, L.content_w, 36, fill=1, stroke=0)
        c.setFillColorRGB(*CREAM)
        c.rect(L.margin, y - 40, L.content_w, 4, fill=1, stroke=0)

        from ..helpers import draw_text

        draw_text(
            c,
            "INFORME PARA EL PACIENTE",
            L.margin + 12,
            y - 18,
            font_name=FONT_SERIF_BOLD,
            size=TYPE.title_h2,
            color=CREAM,
        )
        draw_text(
            c,
            "Resumen en lenguaje claro — sin términos técnicos",
            L.margin + 12,
            y - 30,
            font_name=FONT_SANS,
            size=TYPE.caption,
            color=CREAM,
        )

        if data.fecha_atencion:
            draw_text(
                c,
                data.fecha_atencion.strftime("%d / %m / %Y"),
                L.page_w - L.margin - 12,
                y - 22,
                font_name=FONT_SANS_BOLD,
                size=TYPE.body,
                color=CREAM,
                align="right",
            )
        return y - 50

    def _section_saludo(self, c, data, y: float) -> float:
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=80)
        resumen = self._resumen_data(data)
        y = draw_paragraph(
            c,
            resumen["saludo"],
            L.margin,
            y,
            L.content_w,
            font_name=FONT_SERIF,
            size=TYPE.body,
            color=NAVY,
            leading=TYPE.body * 1.5,
        )
        return y - 8

    def _section_que_hicimos(self, c, data, y: float) -> float:
        L = LAYOUT
        resumen = self._resumen_data(data)
        y = self._ensure_room(c, data, y, need=100)
        y = section_title(
            c,
            "¿Qué hicimos?",
            y,
            subtitle="Cómo fue la evaluación",
        )
        y = draw_paragraph(
            c,
            resumen["que_hicimos"],
            L.margin,
            y,
            L.content_w,
            font_name=FONT_SERIF,
            size=TYPE.body_sm,
            color=NAVY,
            leading=TYPE.body_sm * 1.5,
        )
        return y - 8

    def _section_que_encontramos(self, c, data, y: float) -> float:
        L = LAYOUT
        resumen = self._resumen_data(data)
        if not resumen["que_encontramos"]:
            return y
        y = self._ensure_room(c, data, y, need=100)
        y = section_title(
            c,
            "¿Qué encontramos?",
            y,
            subtitle="Los resultados, explicados de forma sencilla",
        )
        y = draw_paragraph(
            c,
            resumen["que_encontramos"],
            L.margin,
            y,
            L.content_w,
            font_name=FONT_SERIF,
            size=TYPE.body_sm,
            color=NAVY,
            leading=TYPE.body_sm * 1.5,
        )
        return y - 8

    def _section_implicaciones_paciente(self, c, data, y: float) -> float:
        L = LAYOUT
        resumen = self._resumen_data(data)
        modo_voz = resumen.get("modo_voz", "paciente")
        implicaciones = dominios_con_implicaciones(data.resultados or [])
        if not implicaciones:
            return y

        y = self._ensure_room(c, data, y, need=140)
        y = section_title(
            c,
            "Implicaciones para la vida diaria",
            y,
            subtitle="Ejemplos concretos de lo que puede notarse en casa",
        )
        y = (
            draw_paragraph(
                c,
                "Esto es lo que podría notarse en la vida cotidiana:",
                L.margin,
                y,
                L.content_w,
                font_name=FONT_SANS,
                size=TYPE.body_sm,
                color=SLATE,
                leading=TYPE.body_sm * 1.4,
            )
            - 4
        )
        for impl in implicaciones[:4]:
            y = self._ensure_room(c, data, y, need=80)
            dom = str(impl["dominio"])
            nivel = impl["nivel"]
            color = SEMANTIC_DEFICIT if nivel == "severo" else SEMANTIC_LIMITE
            titulo = titulo_implicacion_humano(
                dom,
                nombre_paciente=data.nombre_completo or "",
                modo_voz=modo_voz,
            )
            y = block_header(c, titulo, y, color=color)
            for ej in impl["ejemplos"][:3]:
                y = self._ensure_room(c, data, y, need=28)
                y = bullet(c, ej, L.margin, y - 2, L.content_w) - 1
            if impl["estrategias"]:
                estr_txt = "Apoyos sugeridos: " + " · ".join(impl["estrategias"][:2])
                y = (
                    draw_paragraph(
                        c,
                        estr_txt,
                        L.margin + 8,
                        y,
                        L.content_w - 8,
                        font_name=FONT_SANS,
                        size=TYPE.caption,
                        color=TEAL_DARK,
                        leading=TYPE.caption * 1.35,
                    )
                    - 4
                )
        return y - 6

    def _section_fortalezas_apoyo(self, c, data, y: float) -> float:
        L = LAYOUT
        resumen = self._resumen_data(data)
        if not resumen["fortalezas"] and not resumen["areas_apoyo"]:
            return y

        y = self._ensure_room(c, data, y, need=140)
        titulo_fort = (
            "Fortalezas y áreas de apoyo"
            if resumen.get("modo_voz") != "paciente"
            else "Tus fortalezas y áreas de apoyo"
        )
        y = section_title(
            c,
            titulo_fort,
            y,
            subtitle="Lo que va bien y lo que se puede trabajar",
        )

        col_w = (L.content_w - 16) / 2
        x_left = L.margin
        x_right = L.margin + col_w + 16
        y_f = y_d = y

        if resumen["fortalezas"]:
            y_f = block_header(c, "Fortalezas", y_f, color=SEMANTIC_SUPERIOR, x=x_left)
            for item in resumen["fortalezas"][:5]:
                y_f = bullet(c, item, x_left, y_f, col_w) - 2

        if resumen["areas_apoyo"]:
            y_d = block_header(c, "Áreas de apoyo", y_d, color=SEMANTIC_DEFICIT, x=x_right)
            for item in resumen["areas_apoyo"][:5]:
                y_d = bullet(c, item, x_right, y_d, col_w) - 2

        y = min(y_f, y_d) - 6
        return y

    def _section_recomendaciones_paciente(self, c, data, y: float) -> float:
        L = LAYOUT
        resumen = self._resumen_data(data)
        y = self._ensure_room(c, data, y, need=120)
        y = section_title(
            c,
            "¿Qué recomendamos?",
            y,
            subtitle="Pasos a seguir",
        )
        rec_items = resumen.get("que_recomendamos_items") or []
        if rec_items:
            for i, item in enumerate(rec_items[:6], start=1):
                y = self._ensure_room(c, data, y, need=28)
                y = bullet(c, f"{i}. {item}", L.margin, y, L.content_w, size=TYPE.body_sm) - 2
        else:
            y = draw_paragraph(
                c,
                resumen["que_recomendamos"],
                L.margin,
                y,
                L.content_w,
                font_name=FONT_SERIF,
                size=TYPE.body_sm,
                color=NAVY,
                leading=TYPE.body_sm * 1.5,
            )
        return y - 8

    def _section_faq(self, c, data, y: float) -> float:
        L = LAYOUT
        resumen = self._resumen_data(data)
        y = self._ensure_room(c, data, y, need=180)
        y = section_title(
            c,
            "Preguntas frecuentes",
            y,
            subtitle="Dudas comunes sobre la evaluación",
        )
        for pregunta, respuesta in resumen["preguntas_frecuentes"]:
            y = self._ensure_room(c, data, y, need=60)
            y = draw_paragraph(
                c,
                f"• {pregunta}",
                L.margin,
                y,
                L.content_w,
                font_name=FONT_SANS_BOLD,
                size=TYPE.body_sm,
                color=NAVY,
                leading=TYPE.body_sm * 1.3,
            )
            y = draw_paragraph(
                c,
                respuesta,
                L.margin + 14,
                y,
                L.content_w - 14,
                font_name=FONT_SERIF,
                size=TYPE.caption,
                color=SLATE,
                leading=TYPE.caption * 1.4,
            )
            y -= 4
        return y

    def _section_aviso_informe_tecnico(self, c, data, y: float) -> float:
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=60)
        aviso = (
            "Este es un resumen en lenguaje claro. El informe técnico "
            "completo (con puntuaciones, percentiles, análisis detallado "
            "y firma profesional) está disponible con tu psicólogo/a "
            "tratante. No dudes en pedirlo y revisarlo junto a él/ella."
        )
        y = callout(
            c,
            aviso,
            L.margin,
            y,
            L.content_w,
            accent=NAVY,
            fill=SURFACE,
            title="Sobre este documento",
            size=TYPE.caption,
        )
        return y - 4
