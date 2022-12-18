"""Added order table

Revision ID: 935be10f6488
Revises: c381ddbc4dd7
Create Date: 2022-09-21 01:03:03.031515

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '935be10f6488'
down_revision = 'c381ddbc4dd7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_types',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('type', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('customers',
                    sa.Column('id', postgresql.UUID(), nullable=False),
                    sa.Column('email', sa.Text(), nullable=False),
                    sa.Column('password', sa.Text(), nullable=False),
                    sa.Column('name', sa.Text(), nullable=False),
                    sa.Column('second_name', sa.Text(), nullable=False),
                    sa.Column('birth_date', sa.Date(), nullable=False),
                    sa.Column('photo_url', postgresql.INET(), nullable=True),
                    sa.Column('phone_number', sa.Text(), nullable=False),
                    sa.Column('country', sa.Text(), nullable=True),
                    sa.Column('city', sa.Text(), nullable=True),
                    sa.Column('role', sa.Text(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('customer_id', UUID(), nullable=True),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('files', postgresql.INET(), nullable=True),
    sa.Column('price', postgresql.MONEY(), nullable=True),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('executor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['executor_id'], ['executors.id'], ),
    sa.ForeignKeyConstraint(['type'], ['order_types.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['executors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('user', 'password',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('user', 'name',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('user', 'second_name',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('user', 'birth_date',
               existing_type=sa.DATE(),
               nullable=False)
    op.alter_column('user', 'phone_number',
               existing_type=sa.TEXT(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'phone_number',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('user', 'birth_date',
               existing_type=sa.DATE(),
               nullable=True)
    op.alter_column('user', 'second_name',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('user', 'name',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('user', 'password',
               existing_type=sa.TEXT(),
               nullable=True)
    op.drop_table('order')
    op.drop_table('order_types')
    # ### end Alembic commands ###
