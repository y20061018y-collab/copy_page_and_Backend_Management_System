from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


revision = "0004_service_items"
down_revision = "0003_backfill_seed_services"
branch_labels = None
depends_on = None


DEFAULT_ITEMS = [
    ("基础方案", "¥ 30", "完成基础目标与前置内容。"),
    ("标准方案", "¥ 88", "按推荐路线完成主要内容。"),
    ("进阶方案", "¥ 120", "包含高难目标与资源规划。"),
    ("定制方案", "¥ 30", "根据账号进度安排执行内容。"),
    ("专属方案", "¥ 120", "沟通后提供专属服务安排。"),
]


def upgrade() -> None:
    op.create_table(
        "service_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("game_services.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("price", sa.String(80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_service_items_service_id", "service_items", ["service_id"])

    services = sa.table("game_services", sa.column("id", sa.Integer))
    items = sa.table(
        "service_items",
        sa.column("service_id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("price", sa.String),
        sa.column("description", sa.Text),
        sa.column("sort_order", sa.Integer),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    connection = op.get_bind()
    migration_time = datetime.now(timezone.utc)
    for service_id in connection.execute(sa.select(services.c.id)).scalars():
        connection.execute(
            items.insert(),
            [
                {
                    "service_id": service_id,
                    "name": name,
                    "price": price,
                    "description": description,
                    "sort_order": sort_order,
                    "is_active": True,
                    "created_at": migration_time,
                    "updated_at": migration_time,
                }
                for sort_order, (name, price, description) in enumerate(DEFAULT_ITEMS)
            ],
        )


def downgrade() -> None:
    op.drop_index("ix_service_items_service_id", table_name="service_items")
    op.drop_table("service_items")
