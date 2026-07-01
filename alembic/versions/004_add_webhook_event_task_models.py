"""
Add WebhookSubscription, EventLog, TaskRecord models
مراجعة 004: إضافة نماذج الـ Webhook والأحداث والمهام
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON

revision = '004'
down_revision = 'a5705417729d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('webhook_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.String(length=36), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('events', sa.JSON(), nullable=True),
        sa.Column('secret', sa.String(length=255), nullable=True, server_default=''),
        sa.Column('enabled', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('retry_count', sa.Integer(), nullable=True, server_default='3'),
        sa.Column('timeout', sa.Integer(), nullable=True, server_default='30'),
        sa.Column('headers', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('subscription_id'),
    )
    op.create_index('ix_webhook_subscriptions_sub_id', 'webhook_subscriptions', ['subscription_id'])

    op.create_table('event_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.String(length=36), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=True, server_default='system'),
        sa.Column('priority', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id'),
    )
    op.create_index('ix_event_logs_type', 'event_logs', ['event_type'])
    op.create_index('ix_event_logs_timestamp', 'event_logs', ['timestamp'])

    op.create_table('task_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id'),
    )
    op.create_index('ix_task_records_task_id', 'task_records', ['task_id'])


def downgrade():
    op.drop_index('ix_task_records_task_id', table_name='task_records')
    op.drop_table('task_records')
    op.drop_index('ix_event_logs_timestamp', table_name='event_logs')
    op.drop_index('ix_event_logs_type', table_name='event_logs')
    op.drop_table('event_logs')
    op.drop_index('ix_webhook_subscriptions_sub_id', table_name='webhook_subscriptions')
    op.drop_table('webhook_subscriptions')
