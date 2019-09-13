"""first table

Revision ID: 88e4169593b5
Revises: 
Create Date: 2019-08-03 09:43:39.131972

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "88e4169593b5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "reading",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sensor", sa.String(length=64), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("value", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reading_sensor"), "reading", ["sensor"], unique=False)
    op.create_index(
        op.f("ix_reading_timestamp"), "reading", ["timestamp"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_reading_timestamp"), table_name="reading")
    op.drop_index(op.f("ix_reading_sensor"), table_name="reading")
    op.drop_table("reading")
    # ### end Alembic commands ###
