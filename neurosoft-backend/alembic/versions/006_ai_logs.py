"""ai_logs — trazabilidad de invocaciones al Asistente IA

Revision ID: 006
Revises: 005
Create Date: 2026-05-18

Crea la tabla `ai_logs` para registrar cada llamada al Asistente IA.
NO se guarda el contenido completo de las peticiones (sería PHI en algunos
casos) — solo metadata útil para auditoría clínica según Resolución 1995
de 1999 y trazabilidad de uso de herramientas IA en informes firmados.

Campos clave:
    - prompt_id: cuál prompt especializado se invocó
    - provider/model: qué LLM respondió
    - input_length / output_length: tamaño de la interacción
    - duration_ms: latencia
    - applied_to_report: si el clínico aceptó la sugerencia

Esta migración es complementaria al auto-create de SQLAlchemy
(Base.metadata.create_all en init_database).
"""
from alembic import op
import sqlalchemy as sa


revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("patients.id"), nullable=True),
        sa.Column("evaluation_id", sa.String(36), nullable=True),
        sa.Column("session_id", sa.String(36), nullable=True),
        # Qué se invocó
        sa.Column("prompt_id", sa.String(60), nullable=False),
        sa.Column("endpoint", sa.String(40), nullable=True),
        # Proveedor / modelo
        sa.Column("provider", sa.String(20), nullable=True),
        sa.Column("model", sa.String(60), nullable=True),
        # Métricas
        sa.Column("input_length", sa.Integer(), nullable=True),
        sa.Column("output_length", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("tokens_in", sa.Integer(), nullable=True),
        sa.Column("tokens_out", sa.Integer(), nullable=True),
        # Estado
        sa.Column("success", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("applied_to_report", sa.Boolean(), nullable=True, server_default="0"),
        # Auditoría
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_ai_logs_user_id",       "ai_logs", ["user_id"])
    op.create_index("ix_ai_logs_patient_id",    "ai_logs", ["patient_id"])
    op.create_index("ix_ai_logs_evaluation_id", "ai_logs", ["evaluation_id"])
    op.create_index("ix_ai_logs_session_id",    "ai_logs", ["session_id"])
    op.create_index("ix_ai_logs_prompt_id",     "ai_logs", ["prompt_id"])
    op.create_index("ix_ai_logs_created_at",    "ai_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_ai_logs_created_at",    table_name="ai_logs")
    op.drop_index("ix_ai_logs_prompt_id",     table_name="ai_logs")
    op.drop_index("ix_ai_logs_session_id",    table_name="ai_logs")
    op.drop_index("ix_ai_logs_evaluation_id", table_name="ai_logs")
    op.drop_index("ix_ai_logs_patient_id",    table_name="ai_logs")
    op.drop_index("ix_ai_logs_user_id",       table_name="ai_logs")
    op.drop_table("ai_logs")
