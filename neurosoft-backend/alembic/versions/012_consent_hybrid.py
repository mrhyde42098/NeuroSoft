"""Consentimiento híbrido: modo_firma y adjunto cifrado.

Revision ID: 012_consent_hybrid
"""

from alembic import op
import sqlalchemy as sa

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("consentimientos") as batch:
        batch.add_column(sa.Column("modo_firma", sa.String(20), nullable=False, server_default="digital"))
        batch.add_column(sa.Column("adjunto_path", sa.String(500), nullable=True))
        batch.add_column(sa.Column("requiere_adjunto", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    with op.batch_alter_table("consentimientos") as batch:
        batch.drop_column("requiere_adjunto")
        batch.drop_column("adjunto_path")
        batch.drop_column("modo_firma")
