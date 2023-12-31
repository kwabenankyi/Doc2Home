"""disease prescription

Revision ID: 5c641ee97b82
Revises: 96351c18dcb4
Create Date: 2022-10-25 19:36:43.584797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c641ee97b82'
down_revision = '96351c18dcb4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prescription', schema=None) as batch_op:
        batch_op.add_column(sa.Column('disease_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_disease_id_prescription', 'disease', ['disease_id'], ['disease_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prescription', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('disease_id')

    # ### end Alembic commands ###
