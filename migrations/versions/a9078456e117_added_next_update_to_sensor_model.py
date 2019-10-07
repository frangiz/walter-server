"""Added next_update to Sensor model.

Revision ID: a9078456e117
Revises: a100346c698b
Create Date: 2019-10-07 20:30:43.880157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9078456e117'
down_revision = 'a100346c698b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sensor', sa.Column('next_update', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sensor', 'next_update')
    # ### end Alembic commands ###
