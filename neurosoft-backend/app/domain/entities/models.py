"""
app/domain/entities/models.py
==============================
Entidades de dominio puras. Sin dependencias de framework.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any


@dataclass(frozen=True)
class PacienteId:
    """Value Object: identificador único del paciente."""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 4:
            raise ValueError(f"PacienteId inválido: '{self.value}'")

    @classmethod
    def generate(cls) -> PacienteId:
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_string(cls, s: str) -> PacienteId:
        return cls(value=s.strip())

    def __str__(self) -> str:
        return self.value


@dataclass
class Paciente:
    """Entidad central: persona evaluada neuropsicológicamente."""

    id: PacienteId
    numero_documento: str
    tipo_documento: str
    primer_nombre: str
    primer_apellido: str
    fecha_nacimiento: date
    sexo: str  # "H" | "M"
    escolaridad: str
    fecha_atencion: date
    segundo_nombre: str | None = None
    segundo_apellido: str | None = None
    lateralidad: str = "Diestro"
    ocupacion: str | None = None
    ciudad: str | None = None
    localidad: str | None = None
    estrato: int | None = None
    telefono: str | None = None
    correo: str | None = None
    direccion: str | None = None
    estado_civil: str | None = None
    lugar_nacimiento: str | None = None
    acompanante: str | None = None
    acompanante_relacion: str | None = None
    acompanante_telefono: str | None = None
    grupo_etnico: str | None = None
    profesional_id: str | None = None
    motivo_consulta: str | None = None
    remite: str | None = None
    eps: str | None = None
    regimen: str | None = None
    pais: str | None = None
    orden_medica_no: str | None = None
    discapacidad: str | None = None
    codigo_rips: str | None = None
    cups: str | None = None
    finalidad_consulta: str | None = None
    numero_sesiones: int = 1
    donante: bool = False
    via_atencion: str = "mixto"
    etiquetas: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True

    @property
    def nombre_completo(self) -> str:
        parts = [self.primer_nombre]
        if self.segundo_nombre:
            parts.append(self.segundo_nombre)
        parts.append(self.primer_apellido)
        if self.segundo_apellido:
            parts.append(self.segundo_apellido)
        return " ".join(parts)

    def __post_init__(self):
        if not self.numero_documento.strip():
            raise ValueError("numero_documento no puede estar vacío")
        if self.sexo not in ("H", "M"):
            raise ValueError("sexo debe ser 'H' o 'M'")


@dataclass(frozen=True)
class ResultadoPrueba:
    """Resultado estandarizado de una prueba. Inmutable."""

    test_id: str
    test_nombre: str
    puntaje_bruto: float | None
    puntaje_escalar: float | None
    tipo_metrica: str
    interpretacion: str
    z_equivalente: float | None
    dominio_cognitivo: str
    llave_baremo_usada: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict, hash=False, compare=False)

    @property
    def fue_realizada(self) -> bool:
        return self.puntaje_bruto is not None and self.puntaje_bruto != 9999

    @property
    def es_punto_debil(self) -> bool:
        return self.interpretacion in ("Bajo", "Limítrofe")

    @property
    def es_punto_fuerte(self) -> bool:
        return self.interpretacion == "Superior"


@dataclass
class Evaluacion:
    """Sesión de evaluación neuropsicológica completa."""

    id: str
    paciente_id: PacienteId
    protocolo: str | None
    fecha: date
    resultados: list[ResultadoPrueba] = field(default_factory=list)
    observaciones: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(cls, paciente_id: PacienteId, protocolo: str | None, fecha: date) -> Evaluacion:
        return cls(id=str(uuid.uuid4()), paciente_id=paciente_id, protocolo=protocolo, fecha=fecha)

    @property
    def pruebas_realizadas(self) -> list[ResultadoPrueba]:
        return [r for r in self.resultados if r.fue_realizada]

    @property
    def puntos_debiles(self) -> list[ResultadoPrueba]:
        return [r for r in self.pruebas_realizadas if r.es_punto_debil]

    def agregar_resultado(self, resultado: ResultadoPrueba) -> None:
        self.resultados = [r for r in self.resultados if r.test_id != resultado.test_id]
        self.resultados.append(resultado)


@dataclass(frozen=True)
class PruebaDefinicion:
    """Definición de una prueba desde BD_NEURO_MAESTRA.json."""

    id: str
    nombre: str
    tipo_calculo: str
    tipo_metrica: str
    poblacion: str
    baremos: dict[str, Any] = field(default_factory=dict, hash=False, compare=False)
