"""patients table

Revision ID: 4bfaef5252a8
Revises: 19bac125a854
Create Date: 2022-08-07 21:50:11.422853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4bfaef5252a8'
down_revision = '19bac125a854'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('patient',
    sa.Column('NHSNumber', sa.Integer(), nullable=False),
    sa.Column('forename', sa.String(length=30), nullable=True),
    sa.Column('surname', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('dob', sa.Date(), nullable=True),
    sa.Column('sex', sa.String(length=1), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('weight', sa.Integer(), nullable=True),
    sa.Column('bloodType', sa.String(length=3), nullable=True),
    sa.Column('houseNo', sa.String(length=5), nullable=True),
    sa.Column('streetName', sa.String(length=36), nullable=True),
    sa.Column('postcode', sa.String(length=7), nullable=True),
    sa.Column('passwordHash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('NHSNumber')
    )
    op.create_index(op.f('ix_patient_bloodType'), 'patient', ['bloodType'], unique=False)
    op.create_index(op.f('ix_patient_dob'), 'patient', ['dob'], unique=False)
    op.create_index(op.f('ix_patient_email'), 'patient', ['email'], unique=True)
    op.create_index(op.f('ix_patient_forename'), 'patient', ['forename'], unique=False)
    op.create_index(op.f('ix_patient_height'), 'patient', ['height'], unique=False)
    op.create_index(op.f('ix_patient_passwordHash'), 'patient', ['passwordHash'], unique=False)
    op.create_index(op.f('ix_patient_postcode'), 'patient', ['postcode'], unique=False)
    op.create_index(op.f('ix_patient_sex'), 'patient', ['sex'], unique=False)
    op.create_index(op.f('ix_patient_streetName'), 'patient', ['streetName'], unique=False)
    op.create_index(op.f('ix_patient_surname'), 'patient', ['surname'], unique=False)
    op.create_index(op.f('ix_patient_weight'), 'patient', ['weight'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_patient_weight'), table_name='patient')
    op.drop_index(op.f('ix_patient_surname'), table_name='patient')
    op.drop_index(op.f('ix_patient_streetName'), table_name='patient')
    op.drop_index(op.f('ix_patient_sex'), table_name='patient')
    op.drop_index(op.f('ix_patient_postcode'), table_name='patient')
    op.drop_index(op.f('ix_patient_passwordHash'), table_name='patient')
    op.drop_index(op.f('ix_patient_height'), table_name='patient')
    op.drop_index(op.f('ix_patient_forename'), table_name='patient')
    op.drop_index(op.f('ix_patient_email'), table_name='patient')
    op.drop_index(op.f('ix_patient_dob'), table_name='patient')
    op.drop_index(op.f('ix_patient_bloodType'), table_name='patient')
    op.drop_table('patient')
    # ### end Alembic commands ###