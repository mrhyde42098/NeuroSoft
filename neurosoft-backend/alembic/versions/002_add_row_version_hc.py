"""add_row_version_to_clinical_history

Revision ID: 002
Revises: 001
Create Date: 2026-03-22
"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Agrega optimistic locking a clinical_histories.
    Agrega tabla clinical_history_versions para historial de cambios.
    Agrega columnas faltantes a EvaluationORM (from v4 refactor).
    Agrega tabla appointments (agenda).
    Agrega tabla users (autenticación).
    """
    with op.batch_alter_table('clinical_histories') as batch_op:
        batch_op.add_column(sa.Column('row_version', sa.Integer(), nullable=False, server_default='1'))

    op.create_table(
        'clinical_history_versions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('hc_id', sa.String(36), sa.ForeignKey('clinical_histories.id'), nullable=False, index=True),
        sa.Column('patient_id', sa.String(36), nullable=False, index=True),
        sa.Column('version_num', sa.Integer(), nullable=False),
        sa.Column('snapshot_json', sa.Text(), nullable=False),
        sa.Column('saved_by', sa.String(100), nullable=True),
        sa.Column('saved_at', sa.DateTime(), nullable=False),
    )

    # EvaluationORM new columns
    with op.batch_alter_table('evaluations') as batch_op:
        batch_op.add_column(sa.Column('poblacion', sa.String(30), nullable=True))
        batch_op.add_column(sa.Column('edad_display', sa.String(30), nullable=True))
        batch_op.add_column(sa.Column('pruebas_realizadas', sa.Integer(), server_default='0'))
        batch_op.add_column(sa.Column('pruebas_sin_dato', sa.Integer(), server_default='0'))
        batch_op.add_column(sa.Column('advertencias_json', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('puntos_debiles_json', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('puntos_fuertes_json', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('is_latest', sa.Boolean(), nullable=False, server_default='1'))

    op.create_table(
        'appointments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('patient_id', sa.String(36), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('profesional_id', sa.String(36), sa.ForeignKey('professionals.id'), nullable=True),
        sa.Column('fecha', sa.Date(), nullable=False, index=True),
        sa.Column('hora_inicio', sa.String(5), nullable=False),
        sa.Column('hora_fin', sa.String(5), nullable=True),
        sa.Column('tipo_cita', sa.String(50), server_default='evaluacion'),
        sa.Column('motivo', sa.Text(), nullable=True),
        sa.Column('estado', sa.String(20), server_default='programada', index=True),
        sa.Column('notas_internas', sa.Text(), nullable=True),
        sa.Column('recordatorio_env', sa.Boolean(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(200), nullable=False),
        sa.Column('nombre_completo', sa.String(150), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='profesional'),
        sa.Column('profesional_id', sa.String(36), sa.ForeignKey('professionals.id'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('users')
    op.drop_table('appointments')
    op.drop_table('clinical_history_versions')
    with op.batch_alter_table('evaluations') as batch_op:
        for col in ['poblacion','edad_display','pruebas_realizadas','pruebas_sin_dato',
                    'advertencias_json','puntos_debiles_json','puntos_fuertes_json','is_latest']:
            batch_op.drop_column(col)
    with op.batch_alter_table('clinical_histories') as batch_op:
        batch_op.drop_column('row_version')
