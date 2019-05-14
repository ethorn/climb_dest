"""empty message

Revision ID: 823bb1671107
Revises: cb11dafe5ec9
Create Date: 2019-05-14 14:17:53.097737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '823bb1671107'
down_revision = 'cb11dafe5ec9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cost', schema=None) as batch_op:
        batch_op.add_column(sa.Column('currency', sa.String(length=32), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cost', schema=None) as batch_op:
        batch_op.drop_column('currency')

    # ### end Alembic commands ###
