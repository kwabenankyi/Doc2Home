"""medicines table

Revision ID: 5c53299b5f40
Revises: 1426145c8a26
Create Date: 2022-08-06 20:43:36.868372

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c53299b5f40'
down_revision = '1426145c8a26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('medicine',
    sa.Column('med_id', sa.Integer(), nullable=False),
    sa.Column('medicineName', sa.String(), nullable=True),
    sa.Column('recommendedDose', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('med_id')
    )
    op.create_index(op.f('ix_medicine_medicineName'), 'medicine', ['medicineName'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_medicine_medicineName'), table_name='medicine')
    op.drop_table('medicine')
    # ### end Alembic commands ###
