"""patient etiquetas — QW-6 chips de categorización

Revision ID: 010
Revises: 009
Create Date: 2026-06-05

Añade `etiquetas` a patients: JSON array de strings (ej. Particular, EPS Sanitas).
"""
from alembic import op
import sqlalchemy as sa


revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("patients", sa.Column("etiquetas", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("patients", "etiquetas")
