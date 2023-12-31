"""hoursSpent table

Revision ID: e21f80c52032
Revises: 7f533775308a
Create Date: 2022-07-06 19:45:01.432274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e21f80c52032'
down_revision = '7f533775308a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hours_spent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('entryTime', sa.Time(), nullable=True),
    sa.Column('leaveTime', sa.Time(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['doctor.doctor_id'], ),
    sa.PrimaryKeyConstraint('id', 'date')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('hours_spent')
    # ### end Alembic commands ###
