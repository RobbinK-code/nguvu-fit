"""add user_challenges table

Revision ID: 2413d0501459
Revises: 74d6297af9cd
Create Date: 2026-08-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2413d0501459'
down_revision = '74d6297af9cd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.String(), nullable=False),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('left_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_user_challenges_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user_challenges')),
    )


def downgrade():
    op.drop_table('user_challenges')
