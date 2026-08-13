"""add tracking_type and video_id to exercises, fitness_tier to users

Revision ID: 8fab810715cd
Revises: f9618feba92d
Create Date: 2026-08-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8fab810715cd'
down_revision = 'f9618feba92d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('exercises', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tracking_type', sa.String(), nullable=False, server_default='reps'))
        batch_op.add_column(sa.Column('video_id', sa.String(), nullable=True))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fitness_tier', sa.String(), nullable=False, server_default='beginner'))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('fitness_tier')

    with op.batch_alter_table('exercises', schema=None) as batch_op:
        batch_op.drop_column('video_id')
        batch_op.drop_column('tracking_type')
