"""
app/domain/entities/configuration.py
======================================
Entidades de Configuración del Sistema.

Reemplaza la hoja ConfigCarpetas y la gestión de profesionales del VBA.
Incluye:
  - Configuración de la institución
  - Gestión de profesionales (con firma)
  - Preferencias de presentación del informe
  - Catálogo CIE-10 (neuropsicología)
"""

from __future__ import annotations

import json
import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

_log = logging.getLogger(__name__)


@dataclass
class Profesional:
    """
    Perfil de un profesional evaluador.
    En el VBA era un ComboBox fijo; aquí es administrable.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nombre_completo: str = ""
    titulo: str = ""                    # Ej: "Psicóloga Pontificia Universidad Javeriana"
    especialidad: str = ""              # Ej: "Magister Neurociencias"
    registro_profesional: str = ""      # Tarjeta profesional
    firma_base64: str | None = None  # Imagen de firma codificada en base64
    sello_base64: str | None = None  # Sello/logo del profesional
    email: str | None = None
    activo: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def firma_informe(self) -> str:
        """Texto de firma para el informe."""
        parts = [self.nombre_completo]
        if self.titulo:
            parts.append(self.titulo)
        if self.especialidad:
            parts.append(self.especialidad)
        if self.registro_profesional:
            parts.append(f"Reg. Prof.: {self.registro_profesional}")
        return "\n".join(parts)


@dataclass
class ConfiguracionInstitucion:
    """
    Datos de la institución para el encabezado del informe.
    Equivalente a los datos hardcoded en el VBA (NeuroSoft).
    """
    id: str = "institucion_principal"   # Singleton
    nombre: str = ""
    nit: str = ""
    direccion: str = ""
    telefono: str = ""
    email: str = ""
    sitio_web: str = ""
    logo_base64: str | None = None   # Logo de la institución
    ciudad: str = "Bogotá"
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class PreferenciasInforme:
    """
    Configuración visual del informe PDF/Word generado.
    """
    id: str = "prefs_informe"           # Singleton
    fuente_cuerpo: str = "Calibri"      # Fuente del texto del informe
    fuente_titulos: str = "Calibri"     # Fuente de los títulos
    tamano_fuente_cuerpo: int = 11
    tamano_fuente_titulos: int = 13
    color_primario: str = "#1a568c"     # Azul NeuroSoft por defecto
    color_secundario: str = "#2ec4b6"   # Teal
    incluir_logo: bool = True
    incluir_firma: bool = True
    incluir_grafica_z: bool = True
    incluir_tabla_puntajes: bool = True
    formato_fecha: str = "DD/MM/YYYY"
    pie_pagina: str = ""
    nota_pie_informe: str = (
        "El diagnóstico aquí presentado se realiza a partir del perfil neuropsicológico "
        "analizado en la evaluación. El diagnóstico final se dará en el contexto de un "
        "análisis multidisciplinar, en particular, por parte del médico tratante."
    )
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class BackupConfig:
    """
    Registro de backups realizados.
    El VBA tenía un botón de BackUp que copiaba el .xlsm a una carpeta.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha: datetime = field(default_factory=lambda: datetime.now(UTC))
    ruta: str = ""
    tamano_bytes: int = 0
    total_pacientes: int = 0
    exitoso: bool = True
    notas: str | None = None


# ──────────────────────────────────────────────────────────────────
# CATÁLOGO CIE-10 — Neuropsicología (Colombia)
# Se carga desde app/domain/data/cie10_es.json en arranque.
# Si el JSON no está disponible (entorno roto, etc.), cae a la lista
# mínima hardcoded al final del módulo (CIE10_FALLBACK).
# ──────────────────────────────────────────────────────────────────


def _cie10_json_paths() -> list[Path]:
    """
    Devuelve todas las posibles ubicaciones del catálogo CIE-10.
    Soporta:
      - Dev: .../app/domain/data/cie10_es.json  (junto al código)
      - Bundle PyInstaller: _MEIPASS/app/domain/data/cie10_es.json
      - Override externo: NEUROSOFT_CIE10_PATH
    """
    import os

    candidates: list[Path] = []

    override = os.getenv("NEUROSOFT_CIE10_PATH")
    if override:
        candidates.append(Path(override))

    here = Path(__file__).resolve().parent
    candidates.append(here.parent / "data" / "cie10_es.json")  # app/domain/data

    if getattr(sys, "frozen", False):
        meipass = Path(getattr(sys, "_MEIPASS", ""))
        if meipass:
            candidates.append(meipass / "app" / "domain" / "data" / "cie10_es.json")
            candidates.append(meipass / "data" / "cie10_es.json")

    return candidates


def _load_cie10_from_json() -> list[dict[str, str]]:
    """
    Carga el catálogo CIE-10 desde el JSON.
    Devuelve lista vacía si ningún archivo es usable — el caller debe
    caer al FALLBACK en ese caso.
    """
    for p in _cie10_json_paths():
        try:
            if not p.exists():
                continue
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
            codigos = data.get("codigos") or []
            # Normalizar — aceptamos tanto {codigo, descripcion, cat} como {code, desc}
            out: list[dict[str, str]] = []
            for row in codigos:
                if not isinstance(row, dict):
                    continue
                cod = (row.get("codigo") or row.get("code") or "").strip()
                desc = (row.get("descripcion") or row.get("desc") or "").strip()
                if not cod or not desc:
                    continue
                entry: dict[str, str] = {"codigo": cod, "descripcion": desc}
                cat = row.get("cat")
                if cat:
                    entry["categoria"] = str(cat)
                out.append(entry)
            if out:
                _log.info("CIE-10 cargado desde %s (%d códigos)", p, len(out))
                return out
        except Exception as e:  # pragma: no cover — best effort
            _log.warning("No se pudo leer CIE-10 en %s: %s", p, e)
            continue
    return []


# Lista mínima de respaldo — se usa sólo si el JSON no está disponible.
CIE10_FALLBACK: list[dict[str, str]] = [
    # Trastornos del desarrollo psicológico
    {"codigo": "F700", "descripcion": "Retraso mental leve"},
    {"codigo": "F701", "descripcion": "Retraso mental leve con deterioro conductual significativo"},
    {"codigo": "F710", "descripcion": "Retraso mental moderado"},
    {"codigo": "F711", "descripcion": "Retraso mental moderado con deterioro conductual"},
    {"codigo": "F718", "descripcion": "Otro retraso mental moderado"},
    {"codigo": "F730", "descripcion": "Retraso mental grave"},
    {"codigo": "F731", "descripcion": "Retraso mental grave con deterioro conductual"},
    {"codigo": "F799", "descripcion": "Retraso mental no especificado"},
    {"codigo": "F800", "descripcion": "Trastorno específico de la pronunciación"},
    {"codigo": "F801", "descripcion": "Trastorno del lenguaje expresivo"},
    {"codigo": "F802", "descripcion": "Trastorno del lenguaje receptivo"},
    {"codigo": "F809", "descripcion": "Trastorno del desarrollo del habla y del lenguaje, no especificado"},
    {"codigo": "F810", "descripcion": "Trastorno específico de la lectura (Dislexia)"},
    {"codigo": "F811", "descripcion": "Trastorno específico de la ortografía (Disortografía)"},
    {"codigo": "F812", "descripcion": "Trastorno específico de las habilidades aritméticas (Discalculia)"},
    {"codigo": "F813", "descripcion": "Trastorno mixto del aprendizaje escolar"},
    {"codigo": "F819", "descripcion": "Trastorno del desarrollo del aprendizaje escolar, no especificado"},
    {"codigo": "F820", "descripcion": "Trastorno específico del desarrollo de la función motora"},
    {"codigo": "F83X", "descripcion": "Trastornos mixtos del desarrollo"},
    {"codigo": "F840", "descripcion": "Autismo en la niñez (TEA)"},
    {"codigo": "F845", "descripcion": "Síndrome de Asperger"},
    {"codigo": "F848", "descripcion": "Otros trastornos generalizados del desarrollo (TEA otro)"},
    {"codigo": "F89X", "descripcion": "Trastorno del desarrollo psicológico, no especificado"},
    # TDAH y trastornos conductuales
    {"codigo": "F900", "descripcion": "TDAH — Trastorno de la actividad y de la atención"},
    {"codigo": "F918", "descripcion": "Otros trastornos disociales"},
    {"codigo": "F938", "descripcion": "Otros trastornos emocionales en la niñez"},
    # Adulto — deterioro cognitivo
    {"codigo": "F069", "descripcion": "Trastorno mental orgánico, no especificado (deterioro cognitivo leve)"},
    {"codigo": "F060", "descripcion": "Alucinosis orgánica"},
    {"codigo": "F067", "descripcion": "Trastorno cognoscitivo leve"},
    {"codigo": "F068", "descripcion": "Otros trastornos mentales orgánicos"},
    {"codigo": "F070", "descripcion": "Trastorno de la personalidad orgánica"},
    # Demencias
    {"codigo": "F000", "descripcion": "Demencia en la enfermedad de Alzheimer"},
    {"codigo": "F012", "descripcion": "Demencia vascular mixta"},
    # Adulto — ansiedad, depresión
    {"codigo": "F419", "descripcion": "Trastorno de ansiedad, no especificado"},
    {"codigo": "F39X", "descripcion": "Trastorno del humor, no especificado"},
    # Otros
    {"codigo": "F988", "descripcion": "Otros trastornos del comportamiento en la niñez y adolescencia"},
    {"codigo": "G309", "descripcion": "Enfermedad de Alzheimer no especificada"},
    {"codigo": "G318", "descripcion": "Otras degeneraciones del sistema nervioso"},
    {"codigo": "G35X", "descripcion": "Esclerosis múltiple"},
    {"codigo": "I679", "descripcion": "Enfermedad cerebrovascular, no especificada"},
    {"codigo": "R410", "descripcion": "Desorientación, no especificada"},
    {"codigo": "R418", "descripcion": "Otros síntomas y signos cognoscitivos y de la percepción"},
]


# Catálogo expuesto al resto del sistema — JSON completo si existe,
# si no la lista mínima hardcoded.
CIE10_NEUROPSICOLOGIA: list[dict[str, str]] = _load_cie10_from_json() or CIE10_FALLBACK


def get_cie10_categorias() -> dict[str, str]:
    """
    Devuelve el diccionario de categorías del JSON (ej. "F00-F09" → "Demencias...").
    Si no hay JSON, devuelve un dict vacío.
    """
    for p in _cie10_json_paths():
        try:
            if not p.exists():
                continue
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
            cats = data.get("categorias") or {}
            if isinstance(cats, dict):
                return {str(k): str(v) for k, v in cats.items()}
        except Exception:
            continue
    return {}
