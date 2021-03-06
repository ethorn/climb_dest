"""adding continent to destination table

Revision ID: c7a95c76e625
Revises: 13cb99a5e7c7
Create Date: 2019-05-21 13:08:42.129863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7a95c76e625'
down_revision = '13cb99a5e7c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('destination', schema=None) as batch_op:
        batch_op.add_column(sa.Column('continent', sa.String(length=64), nullable=True))
        batch_op.create_index(batch_op.f('ix_destination_continent'), ['continent'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('destination', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_destination_continent'))
        batch_op.drop_column('continent')

    # ### end Alembic commands ###
