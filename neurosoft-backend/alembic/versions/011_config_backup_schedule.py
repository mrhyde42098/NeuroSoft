"""config_backup_schedule — QW-8 backup programado configurable

Revision ID: 011
Revises: 010
Create Date: 2026-06-06
"""
from alembic import op
import sqlalchemy as sa


revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "config_backup_schedule",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("frequency", sa.String(20), nullable=False, server_default="daily"),
        sa.Column("hour", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("minute", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mantener_total", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("external_path", sa.String(500), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.execute(
        "INSERT INTO config_backup_schedule (id, enabled, frequency, hour, minute, mantener_total) "
        "VALUES ('default', 1, 'daily', 2, 0, 5)"
    )


def downgrade() -> None:
    op.drop_table("config_backup_schedule")
