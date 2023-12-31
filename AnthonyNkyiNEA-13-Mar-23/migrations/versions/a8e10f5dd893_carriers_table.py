"""carriers table

Revision ID: a8e10f5dd893
Revises: 047f131fdd5e
Create Date: 2022-08-10 21:44:56.575719

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8e10f5dd893'
down_revision = '047f131fdd5e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('carrier',
    sa.Column('carrier_id', sa.Integer(), nullable=False),
    sa.Column('NHSNumber', sa.Integer(), nullable=True),
    sa.Column('disease_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['NHSNumber'], ['patient.NHSNumber'], ),
    sa.ForeignKeyConstraint(['disease_id'], ['disease.disease_id'], ),
    sa.PrimaryKeyConstraint('carrier_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('carrier')
    # ### end Alembic commands ###
