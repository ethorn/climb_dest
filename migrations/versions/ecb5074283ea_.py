"""empty message

Revision ID: ecb5074283ea
Revises: 3b3b1e9880ab
Create Date: 2019-07-17 10:05:58.010814

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecb5074283ea'
down_revision = '3b3b1e9880ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('additional_photos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('additional_photo_extension', sa.String(length=256), nullable=True))
        batch_op.drop_column('additional_photo_url')

    with op.batch_alter_table('destination', schema=None) as batch_op:
        batch_op.add_column(sa.Column('featured_photo_extension', sa.String(length=8), nullable=True))
        batch_op.add_column(sa.Column('photo_folder_url', sa.String(length=256), nullable=True))
        batch_op.drop_column('featured_photo_url')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('destination', schema=None) as batch_op:
        batch_op.add_column(sa.Column('featured_photo_url', sa.VARCHAR(length=256), nullable=True))
        batch_op.drop_column('photo_folder_url')
        batch_op.drop_column('featured_photo_extension')

    with op.batch_alter_table('additional_photos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('additional_photo_url', sa.VARCHAR(length=256), nullable=True))
        batch_op.drop_column('additional_photo_extension')

    # ### end Alembic commands ###
