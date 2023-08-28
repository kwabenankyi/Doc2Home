"""ingredients table

Revision ID: 047f131fdd5e
Revises: d155637bdc32
Create Date: 2022-08-10 21:35:07.975971

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '047f131fdd5e'
down_revision = 'd155637bdc32'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ingredient',
    sa.Column('ingredient_id', sa.Integer(), nullable=False),
    sa.Column('med_id', sa.Integer(), nullable=True),
    sa.Column('allergen_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['allergen_id'], ['allergen.allergen_id'], ),
    sa.ForeignKeyConstraint(['med_id'], ['medicine.med_id'], ),
    sa.PrimaryKeyConstraint('ingredient_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ingredient')
    # ### end Alembic commands ###