"""acompañante detallado + hipótesis pre-eval + informe inconcluso

Revision ID: 004
Revises: 003
Create Date: 2026-05-11

Cambios:
    • patients: acompanante_relacion, acompanante_telefono
      → Datos de contacto del acompañante como entidad separada (§1.1 CLINICAL_ROADMAP)
    • clinical_histories: hipotesis_pre_eval
      → Campo de hipótesis diagnóstica al cierre de HC, antes de evaluación (§1.2)
    • evaluations: informe_inconcluso_cat, informe_inconcluso_nota
      → Modo informe inconcluso con 4 categorías documentadas (§1.4)
"""
from alembic import op
import sqlalchemy as sa


revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- patients: acompañante extendido -----------------------------------
    with op.batch_alter_table("patients") as batch_op:
        batch_op.add_column(sa.Column("acompanante_relacion", sa.String(100), nullable=True))
        batch_op.add_column(sa.Column("acompanante_telefono", sa.String(50), nullable=True))

    # --- clinical_histories: hipótesis pre-evaluación ----------------------
    with op.batch_alter_table("clinical_histories") as batch_op:
        batch_op.add_column(sa.Column("hipotesis_pre_eval", sa.Text(), nullable=True, server_default="N/A"))

    # --- evaluations: informe inconcluso -----------------------------------
    with op.batch_alter_table("evaluations") as batch_op:
        batch_op.add_column(sa.Column(
            "informe_inconcluso_cat", sa.String(80), nullable=True,
            comment="Categoría de informe inconcluso: completo_2da_orden|evaluacion_incompleta|con_pruebas_recientes|estado_paciente"
        ))
        batch_op.add_column(sa.Column("informe_inconcluso_nota", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("evaluations") as batch_op:
        batch_op.drop_column("informe_inconcluso_nota")
        batch_op.drop_column("informe_inconcluso_cat")

    with op.batch_alter_table("clinical_histories") as batch_op:
        batch_op.drop_column("hipotesis_pre_eval")

    with op.batch_alter_table("patients") as batch_op:
        batch_op.drop_column("acompanante_telefono")
        batch_op.drop_column("acompanante_relacion")
