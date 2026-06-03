"""therapy_tasks — tareas terapéuticas entre sesiones

Revision ID: 005
Revises: 004
Create Date: 2026-05-18

Crea la tabla `therapy_tasks` para registrar las tareas-casa que el clínico
asigna al paciente entre sesiones de psicoterapia.

Fundamento clínico: Kazantzis et al. (2016) — meta-análisis que muestra
g≈0.48 sobre outcome cuando hay tarea inter-sesión revisada.

Tipos soportados (campo `tipo`):
    registro_pensamientos, registro_emocional, autorregistro_conducta,
    exposicion, activacion_conductual, habilidades_DBT, psicoeducacion,
    libre

Estados (campo `estado`):
    pendiente, en_progreso, completada, parcial, omitida

Frecuencias (campo `frecuencia`):
    diaria, varias_semana, semanal, unica

Esta migración es complementaria al auto-create de SQLAlchemy
(`Base.metadata.create_all` en `init_database()`): existe para mantener
la coherencia con el sistema de migraciones declarativo y permitir un
upgrade explícito en deployments con servidor central.
"""
from alembic import op
import sqlalchemy as sa


revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "therapy_tasks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("plan_id", sa.String(36), sa.ForeignKey("therapy_plans.id"), nullable=True),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("therapy_sessions.id"), nullable=True),
        sa.Column("profesional_id", sa.String(36), sa.ForeignKey("professionals.id"), nullable=True),
        # Definición
        sa.Column("tipo", sa.String(30), nullable=False, server_default="libre"),
        sa.Column("titulo", sa.String(120), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("objetivo_id", sa.String(36), sa.ForeignKey("therapy_objectives.id"), nullable=True),
        # Calendario
        sa.Column("fecha_asignacion", sa.DateTime(), nullable=False),
        sa.Column("fecha_limite", sa.DateTime(), nullable=True),
        sa.Column("frecuencia", sa.String(20), nullable=True),
        # Estado y entrega
        sa.Column("estado", sa.String(20), nullable=False, server_default="pendiente"),
        sa.Column("completada_en", sa.DateTime(), nullable=True),
        sa.Column("respuesta", sa.Text(), nullable=True),
        sa.Column("adherencia_pct", sa.Integer(), nullable=True),
        sa.Column("dificultad_pct", sa.Integer(), nullable=True),
        sa.Column("utilidad_pct", sa.Integer(), nullable=True),
        # Revisión
        sa.Column("revisada_en", sa.DateTime(), nullable=True),
        sa.Column("nota_clinico", sa.Text(), nullable=True),
        # Auditoría
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
    )
    # Índices para queries frecuentes
    op.create_index("ix_therapy_tasks_patient_id",       "therapy_tasks", ["patient_id"])
    op.create_index("ix_therapy_tasks_plan_id",          "therapy_tasks", ["plan_id"])
    op.create_index("ix_therapy_tasks_session_id",       "therapy_tasks", ["session_id"])
    op.create_index("ix_therapy_tasks_profesional_id",   "therapy_tasks", ["profesional_id"])
    op.create_index("ix_therapy_tasks_tipo",             "therapy_tasks", ["tipo"])
    op.create_index("ix_therapy_tasks_estado",           "therapy_tasks", ["estado"])
    op.create_index("ix_therapy_tasks_fecha_asignacion", "therapy_tasks", ["fecha_asignacion"])


def downgrade() -> None:
    op.drop_index("ix_therapy_tasks_fecha_asignacion", table_name="therapy_tasks")
    op.drop_index("ix_therapy_tasks_estado",           table_name="therapy_tasks")
    op.drop_index("ix_therapy_tasks_tipo",             table_name="therapy_tasks")
    op.drop_index("ix_therapy_tasks_profesional_id",   table_name="therapy_tasks")
    op.drop_index("ix_therapy_tasks_session_id",       table_name="therapy_tasks")
    op.drop_index("ix_therapy_tasks_plan_id",          table_name="therapy_tasks")
    op.drop_index("ix_therapy_tasks_patient_id",       table_name="therapy_tasks")
    op.drop_table("therapy_tasks")
