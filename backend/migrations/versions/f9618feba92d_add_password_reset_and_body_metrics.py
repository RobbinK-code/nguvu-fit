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

    op.create_table(
        'body_metric_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=True),
        sa.Column('chest_cm', sa.Float(), nullable=True),
        sa.Column('waist_cm', sa.Float(), nullable=True),
        sa.Column('hips_cm', sa.Float(), nullable=True),
        sa.Column('arm_cm', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.CheckConstraint('weight_kg IS NULL OR weight_kg > 0', name=op.f('ck_body_metric_logs_weight_positive')),
        sa.CheckConstraint('chest_cm IS NULL OR chest_cm > 0', name=op.f('ck_body_metric_logs_chest_positive')),
        sa.CheckConstraint('waist_cm IS NULL OR waist_cm > 0', name=op.f('ck_body_metric_logs_waist_positive')),
        sa.CheckConstraint('hips_cm IS NULL OR hips_cm > 0', name=op.f('ck_body_metric_logs_hips_positive')),
        sa.CheckConstraint('arm_cm IS NULL OR arm_cm > 0', name=op.f('ck_body_metric_logs_arm_positive')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_body_metric_logs_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_body_metric_logs')),
    )


def downgrade():
    op.drop_table('body_metric_logs')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_reset_token', type_='unique')
        batch_op.drop_column('reset_token_expires_at')
        batch_op.drop_column('reset_token')