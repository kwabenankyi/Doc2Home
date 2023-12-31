"""appointments2

Revision ID: bc46b091df51
Revises: 36bc0ee95801
Create Date: 2022-09-15 08:48:47.981195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc46b091df51'
down_revision = '36bc0ee95801'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('time', sa.Time(), nullable=True))
        batch_op.create_index(batch_op.f('ix_appointment_date'), ['date'], unique=False)
        batch_op.create_index(batch_op.f('ix_appointment_time'), ['time'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_appointment_time'))
        batch_op.drop_index(batch_op.f('ix_appointment_date'))
        batch_op.drop_column('time')
        batch_op.drop_column('date')

    # ### end Alembic commands ###
