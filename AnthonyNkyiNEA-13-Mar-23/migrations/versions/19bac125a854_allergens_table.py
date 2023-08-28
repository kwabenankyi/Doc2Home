"""allergens table

Revision ID: 19bac125a854
Revises: 39958b78e270
Create Date: 2022-08-07 20:33:20.519585

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19bac125a854'
down_revision = '39958b78e270'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('allergen',
    sa.Column('allergen_id', sa.Integer(), nullable=False),
    sa.Column('allergenName', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('allergen_id'),
    sa.UniqueConstraint('allergenName')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('allergen')
    # ### end Alembic commands ###
