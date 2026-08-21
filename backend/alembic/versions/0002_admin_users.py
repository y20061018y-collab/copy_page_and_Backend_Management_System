from alembic import op
import sqlalchemy as sa

revision = "0002_admin_users"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("admin_users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("username", sa.String(120), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_admin_users_username", "admin_users", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_admin_users_username", table_name="admin_users")
    op.drop_table("admin_users")
