"""initial_schema

Revision ID: 001
Revises: 
Create Date: 2026-03-22
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Migración inicial: crea todas las tablas desde cero.
    Solo se ejecuta si la BD está vacía.
    """
    # Las tablas se crean via SQLAlchemy Base.metadata.create_all() en el startup.
    # Esta migración es el punto de partida para el historial de migraciones.
    pass


def downgrade() -> None:
    pass
