"""Eliminar unique constraint de emails y documento

Revision ID: 52dc70703aca
Revises: 43c3270a5483
Create Date: 2025-06-11 08:41:46.497478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52dc70703aca'
down_revision = '43c3270a5483'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        'UQ__solicita__A25B3E61F096D5B9',  # nombre exacto del índice
        'solicitantes',
        type_='unique'
    )


def downgrade():
    op.create_unique_constraint(
        'UQ__solicita__A25B3E61F096D5B9',
        'solicitantes',
        ['documento']
    )
