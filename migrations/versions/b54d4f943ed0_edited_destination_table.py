"""edited destination table

Revision ID: b54d4f943ed0
Revises: 0001990d4b19
Create Date: 2019-05-07 14:13:22.786332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b54d4f943ed0'
down_revision = '0001990d4b19'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('destination', schema=None) as batch_op:
        batch_op.add_column(sa.Column('featured_photo_filename', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('featured_photo_url', sa.String(length=256), nullable=True))
        batch_op.drop_column('image_url')
        batch_op.drop_column('image_filename')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('destination', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_filename', sa.VARCHAR(length=64), nullable=True))
        batch_op.add_column(sa.Column('image_url', sa.VARCHAR(length=256), nullable=True))
        batch_op.drop_column('featured_photo_url')
        batch_op.drop_column('featured_photo_filename')

    # ### end Alembic commands ###
