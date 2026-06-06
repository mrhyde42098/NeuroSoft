"""patient via_atencion — vía de atención multi-módulo

Revision ID: 007
Revises: 006
Create Date: 2026-06-05

Añade `via_atencion` a patients: valores comma-separated
(neuropsicologia|psicoterapia|rehabilitacion|mixto). Default mixto.
"""
from alembic import op
import sqlalchemy as sa


revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "patients",
        sa.Column("via_atencion", sa.String(120), nullable=False, server_default="mixto"),
    )


def downgrade() -> None:
    op.drop_column("patients", "via_atencion")
