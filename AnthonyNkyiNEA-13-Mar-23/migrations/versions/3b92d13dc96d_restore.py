"""restore

Revision ID: 3b92d13dc96d
Revises: 97d58d6a213a
Create Date: 2022-08-21 20:56:49.547777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b92d13dc96d'
down_revision = '97d58d6a213a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.drop_index('ix_patient_email')
        batch_op.create_index(batch_op.f('ix_patient_email'), ['email'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_patient_email'))
        batch_op.create_index('ix_patient_email', ['email'], unique=False)

    # ### end Alembic commands ###