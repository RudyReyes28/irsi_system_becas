"""Agregar usuario_id a EstadoBecado y ampliar enum EstadoSolicitud

Revision ID: 71cc5c5a80da
Revises: 52dc70703aca
Create Date: 2025-06-11 11:06:45.517088

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision = '71cc5c5a80da'
down_revision = '52dc70703aca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sysdiagrams')
    with op.batch_alter_table('estado_becado_historial', schema=None) as batch_op:
        batch_op.add_column(sa.Column('usuario_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'usuarios', ['usuario_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('estado_becado_historial', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('usuario_id')

    op.create_table('sysdiagrams',
    sa.Column('name', sa.NVARCHAR(length=128, collation='Modern_Spanish_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('principal_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('diagram_id', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('version', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('definition', mssql.VARBINARY(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('diagram_id', name='PK__sysdiagr__C2B05B615B68C383')
    )
    # ### end Alembic commands ###
