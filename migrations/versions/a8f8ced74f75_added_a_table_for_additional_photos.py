"""added a table for additional photos

Revision ID: a8f8ced74f75
Revises: 849fb7127501
Create Date: 2019-05-07 15:31:39.774237

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8f8ced74f75'
down_revision = '849fb7127501'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('additional_photos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('additional_photo_filename', sa.String(length=64), nullable=True),
    sa.Column('additional_photo_url', sa.String(length=256), nullable=True),
    sa.Column('destination_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['destination_id'], ['destination.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('additional_photos', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_additional_photos_destination_id'), ['destination_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('additional_photos', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_additional_photos_destination_id'))

    op.drop_table('additional_photos')
    # ### end Alembic commands ###
