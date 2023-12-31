"""add address_id to doctor

Revision ID: d155637bdc32
Revises: 2c59806908cb
Create Date: 2022-08-10 20:56:25.436698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd155637bdc32'
down_revision = '2c59806908cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('doctor', schema=None) as batch_op:
        batch_op.add_column(sa.Column('address_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('doctor', 'address', ['address_id'], ['address_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('doctor', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('address_id')

    # ### end Alembic commands ###
