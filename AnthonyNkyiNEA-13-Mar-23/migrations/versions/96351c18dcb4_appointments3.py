"""appointments3

Revision ID: 96351c18dcb4
Revises: bc46b091df51
Create Date: 2022-09-15 09:14:45.901720

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96351c18dcb4'
down_revision = 'bc46b091df51'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('appdate', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('apptime', sa.Time(), nullable=True))
        batch_op.create_index(batch_op.f('ix_appointment_appdate'), ['appdate'], unique=False)
        batch_op.create_index(batch_op.f('ix_appointment_apptime'), ['apptime'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_appointment_apptime'))
        batch_op.drop_index(batch_op.f('ix_appointment_appdate'))
        batch_op.drop_column('apptime')
        batch_op.drop_column('appdate')

    # ### end Alembic commands ###
