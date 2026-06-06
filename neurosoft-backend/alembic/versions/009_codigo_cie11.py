"""codigo_cie11 dual coding CIE-10/CIE-11

Revision ID: 009
Revises: 008
Create Date: 2026-06-05

Añade codigo_cie11 a clinical_histories y therapy_plans para
codificación dual (transición CIE-11 Colombia ~2027).
"""
from alembic import op
import sqlalchemy as sa


revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "clinical_histories",
        sa.Column("codigo_cie11", sa.String(15), nullable=True),
    )
    op.add_column(
        "therapy_plans",
        sa.Column("codigo_cie11", sa.String(15), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("therapy_plans", "codigo_cie11")
    op.drop_column("clinical_histories", "codigo_cie11")
