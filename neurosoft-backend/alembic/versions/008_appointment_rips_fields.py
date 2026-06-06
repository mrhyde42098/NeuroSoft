"""appointment RIPS/agenda fields

Revision ID: 008
Revises: 007
Create Date: 2026-06-05

Extiende appointments con EPS, régimen, autorización, CUPS,
modalidad, discapacidad y contacto para agenda + RIPS.
"""
from alembic import op
import sqlalchemy as sa


revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("appointments", sa.Column("eps", sa.String(100), nullable=True))
    op.add_column("appointments", sa.Column("regimen", sa.String(40), nullable=True))
    op.add_column("appointments", sa.Column("autorizacion_no", sa.String(50), nullable=True))
    op.add_column("appointments", sa.Column("cups", sa.String(20), nullable=True))
    op.add_column("appointments", sa.Column("modalidad", sa.String(30), nullable=True))
    op.add_column("appointments", sa.Column("discapacidad", sa.String(100), nullable=True))
    op.add_column("appointments", sa.Column("contacto_telefono", sa.String(20), nullable=True))
    op.add_column("appointments", sa.Column("contacto_correo", sa.String(100), nullable=True))


def downgrade() -> None:
    for col in (
        "contacto_correo", "contacto_telefono", "discapacidad", "modalidad",
        "cups", "autorizacion_no", "regimen", "eps",
    ):
        op.drop_column("appointments", col)
