"""medicines table

Revision ID: 29fddc399a19
Revises: 5c53299b5f40
Create Date: 2022-08-06 21:34:16.418627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29fddc399a19'
down_revision = '5c53299b5f40'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('medicine',
    sa.Column('med_id', sa.Integer(), nullable=False),
    sa.Column('medicineName', sa.String(length=64), nullable=True),
    sa.Column('recommendedDose', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('med_id')
    )
    op.create_index(op.f('ix_medicine_medicineName'), 'medicine', ['medicineName'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_medicine_medicineName'), table_name='medicine')
    op.drop_table('medicine')
    # ### end Alembic commands ###
