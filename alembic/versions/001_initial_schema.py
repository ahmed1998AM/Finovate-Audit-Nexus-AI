"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2026-06-14
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), server_default="Auditor"),
        sa.Column("is_active", sa.Boolean(), server_default="1"),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="1"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "audit_projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("project_name", sa.String(200), nullable=False),
        sa.Column("audit_type", sa.String(50)),
        sa.Column("start_date", sa.DateTime()),
        sa.Column("end_date", sa.DateTime()),
        sa.Column("status", sa.String(20), server_default="Planning"),
        sa.Column("risk_level", sa.String(20)),
        sa.Column("lead_auditor_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("team_members", sa.JSON()),
        sa.Column("scope", sa.Text()),
        sa.Column("objectives", sa.Text()),
        sa.Column("findings_count", sa.Integer(), server_default="0"),
        sa.Column("recommendations_count", sa.Integer(), server_default="0"),
        sa.Column("results", sa.JSON()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime()),
    )
    op.create_table(
        "audit_findings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("audit_projects.id"), nullable=False),
        sa.Column("finding_number", sa.String(20), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(50)),
        sa.Column("severity", sa.String(20)),
        sa.Column("risk_score", sa.Float()),
        sa.Column("financial_impact", sa.Float()),
        sa.Column("root_cause", sa.Text()),
        sa.Column("recommendation", sa.Text()),
        sa.Column("management_response", sa.Text()),
        sa.Column("action_plan", sa.Text()),
        sa.Column("responsible_person", sa.String(100)),
        sa.Column("due_date", sa.DateTime()),
        sa.Column("status", sa.String(20), server_default="Open"),
        sa.Column("evidence_files", sa.JSON()),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime()),
    )
    op.create_table(
        "fraud_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_number", sa.String(20), unique=True, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("fraud_type", sa.String(50)),
        sa.Column("severity", sa.String(20)),
        sa.Column("detected_by", sa.String(100)),
        sa.Column("detection_date", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("amount_involved", sa.Float()),
        sa.Column("suspects", sa.JSON()),
        sa.Column("evidence", sa.JSON()),
        sa.Column("investigation_status", sa.String(20), server_default="Open"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime()),
    )
    op.create_table(
        "tax_compliance",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id")),
        sa.Column("tax_type", sa.String(50)),
        sa.Column("period", sa.String(20)),
        sa.Column("status", sa.String(20)),
        sa.Column("due_date", sa.DateTime()),
        sa.Column("amount", sa.Float()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime()),
    )
    op.create_table(
        "work_papers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("audit_projects.id"), nullable=False),
        sa.Column("wp_number", sa.String(20), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("file_path", sa.String(500)),
        sa.Column("file_hash", sa.String(64)),
        sa.Column("review_status", sa.String(20), server_default="Draft"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime()),
    )
    op.create_table(
        "ai_agent_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("agent_name", sa.String(100), nullable=False),
        sa.Column("task_id", sa.String(100)),
        sa.Column("input_data", sa.JSON()),
        sa.Column("output_data", sa.JSON()),
        sa.Column("confidence_score", sa.Float()),
        sa.Column("execution_time", sa.Float()),
        sa.Column("tokens_used", sa.Integer()),
        sa.Column("model_used", sa.String(100)),
        sa.Column("status", sa.String(20)),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table("ai_agent_logs")
    op.drop_table("work_papers")
    op.drop_table("tax_compliance")
    op.drop_table("fraud_cases")
    op.drop_table("audit_findings")
    op.drop_table("audit_projects")
    op.drop_table("companies")
    op.drop_table("users")
