"""add password reset fields and body_metric_logs table

Revision ID: f9618feba92d
Revises: 1b4d49f4493a
Create Date: 2026-08-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9618feba92d'
down_revision = '1b4d49f4493a'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reset_token', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('reset_token_expires_at', sa.DateTime(), nullable=True))
        batch_op.create_unique_constraint('uq_users_reset_token', ['reset_token'])

    # body_metric_logs is deliberately NOT created here - it already exists
    # in production. seed.py used to call db.create_all() as a "safety
    # net", which silently created this table from the model definition
    # the first time it deployed, bypassing Alembic entirely and never
    # recording it in alembic_version. That footgun is now removed from
    # seed.py so it can't happen again for future tables.


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_reset_token', type_='unique')
        batch_op.drop_column('reset_token_expires_at')
        batch_op.drop_column('reset_token')