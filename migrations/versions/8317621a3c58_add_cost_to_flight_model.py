"""Add cost to Flight model

Revision ID: 8317621a3c58
Revises: 0022be26d3fd
Create Date: 2024-08-25 00:54:20.116157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8317621a3c58'
down_revision = '0022be26d3fd'
branch_labels = None
depends_on = None


def upgrade():
    # Add the new column with NULL allowed initially
    with op.batch_alter_table('flights', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cost', sa.Float(), nullable=True))
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=36),
               existing_nullable=False)

    # Update existing rows to set a default value for 'cost'
    op.execute("UPDATE flights SET cost = 0.0 WHERE cost IS NULL")

    # Alter the column to not allow NULL values after setting defaults
    with op.batch_alter_table('flights', schema=None) as batch_op:
        batch_op.alter_column('cost',
               existing_type=sa.Float(),
               nullable=False)

    with op.batch_alter_table('passengers', schema=None) as batch_op:
        batch_op.alter_column('flight_id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(),
               existing_nullable=False)
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=36),
               existing_nullable=False)


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('passengers', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.String(length=36),
               type_=sa.INTEGER(),
               existing_nullable=False)
        batch_op.alter_column('flight_id',
               existing_type=sa.UUID(),
               type_=sa.INTEGER(),
               existing_nullable=False)

    with op.batch_alter_table('flights', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.String(length=36),
               type_=sa.INTEGER(),
               existing_nullable=False)
        batch_op.drop_column('cost')

    # ### end Alembic commands ###
