from alembic import op
import sqlalchemy as sa


revision = "0008_add_child_services"
down_revision = "0007_cleanup_service_items"
branch_labels = None
depends_on = None


def _table_names(connection) -> set[str]:
    return set(sa.inspect(connection).get_table_names())


def upgrade() -> None:
    connection = op.get_bind()
    op.create_table(
        "child_services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("game_service_id", sa.Integer(), sa.ForeignKey("game_services.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("price", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("image_path", sa.String(length=255), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_child_services_game_service_id", "child_services", ["game_service_id"])
    if "service_items" in _table_names(connection):
        op.execute(
            sa.text(
                """
                INSERT INTO child_services (
                    game_service_id,
                    name,
                    price,
                    description,
                    image_path,
                    sort_order,
                    created_at,
                    updated_at
                )
                SELECT
                    service_id,
                    name,
                    price,
                    description,
                    NULL,
                    sort_order,
                    created_at,
                    updated_at
                FROM service_items
                WHERE is_active IS TRUE
                """
            )
        )


def downgrade() -> None:
    op.drop_index("ix_child_services_game_service_id", table_name="child_services")
    op.drop_table("child_services")
