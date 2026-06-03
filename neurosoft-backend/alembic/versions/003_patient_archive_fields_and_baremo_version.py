"""add archive fields to patients + baremo version to evaluations

Revision ID: 003
Revises: 002
Create Date: 2026-04-18

Cambios:
    • patients.archived_at / archived_by / archived_reason  → soft-delete trazable
      (obligatorio por Resolución 1995 / Ley 1581: no borrar HC, archivar).
    • evaluations.baremo_version / baremo_checksum          → versionado clínico
      del baremo con el que se generó cada informe.
    • patients.profesional_id                                → índice para mejorar
      performance de queries por profesional.
    • patients / evaluations / clinical_histories.is_active → índice para soft-delete.
"""
from alembic import op
import sqlalchemy as sa


revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- patients: campos de archivado ----------------------------------
    with op.batch_alter_table("patients") as batch_op:
        batch_op.add_column(sa.Column("archived_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("archived_by", sa.String(36), nullable=True))
        batch_op.add_column(sa.Column("archived_reason", sa.Text(), nullable=True))
    op.create_index("ix_patients_archived_at", "patients", ["archived_at"])
    op.create_index("ix_patients_profesional_id", "patients", ["profesional_id"])
    op.create_index("ix_patients_is_active", "patients", ["is_active"])

    # --- evaluations: versionado de baremo ------------------------------
    with op.batch_alter_table("evaluations") as batch_op:
        batch_op.add_column(sa.Column("baremo_version", sa.String(30), nullable=True))
        batch_op.add_column(sa.Column("baremo_checksum", sa.String(64), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("evaluations") as batch_op:
        batch_op.drop_column("baremo_checksum")
        batch_op.drop_column("baremo_version")
    op.drop_index("ix_patients_is_active", table_name="patients")
    op.drop_index("ix_patients_profesional_id", table_name="patients")
    op.drop_index("ix_patients_archived_at", table_name="patients")
    with op.batch_alter_table("patients") as batch_op:
        batch_op.drop_column("archived_reason")
        batch_op.drop_column("archived_by")
        batch_op.drop_column("archived_at")
