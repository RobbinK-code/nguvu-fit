"""add referral fields to users

Revision ID: 74d6297af9cd
Revises: 8fab810715cd
Create Date: 2026-08-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74d6297af9cd'
down_revision = '8fab810715cd'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('referral_code', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('referred_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column('referral_reward_granted', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.create_unique_constraint('uq_users_referral_code', ['referral_code'])
        batch_op.create_foreign_key(
            'fk_users_referred_by_id_users', 'users', ['referred_by_id'], ['id']
        )


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_referred_by_id_users', type_='foreignkey')
        batch_op.drop_constraint('uq_users_referral_code', type_='unique')
        batch_op.drop_column('referral_reward_granted')
        batch_op.drop_column('referred_by_id')
        batch_op.drop_column('referral_code')
