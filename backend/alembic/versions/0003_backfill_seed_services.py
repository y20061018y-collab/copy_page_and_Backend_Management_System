from alembic import op
import sqlalchemy as sa


revision = "0003_backfill_seed_services"
down_revision = "0002_admin_users"
branch_labels = None
depends_on = None


BACKFILL = {
    "genshin": [("提瓦特探索", "¥ 30"), ("养成目标", "¥ 120")],
    "star-rail": [("版本内容", "¥ 25"), ("银河冒险", "¥ 100")],
    "zenless-zone-zero": [("都市幻想", "¥ 20"), ("角色养成", "¥ 100")],
    "wuthering-waves": [("账号养成", "¥ 120"), ("动作冒险", "¥ 25")],
}


def upgrade() -> None:
    games = sa.table("games", sa.column("id", sa.Integer), sa.column("slug", sa.String))
    services = sa.table(
        "game_services",
        sa.column("game_id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("price", sa.String),
        sa.column("description", sa.String),
        sa.column("sort_order", sa.Integer),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    connection = op.get_bind()

    for slug, additions in BACKFILL.items():
        game_id = connection.execute(sa.select(games.c.id).where(games.c.slug == slug)).scalar_one_or_none()
        if game_id is None:
            continue

        existing_names = set(connection.execute(sa.select(services.c.name).where(services.c.game_id == game_id)).scalars())
        enabled_count = connection.execute(
            sa.select(sa.func.count()).select_from(services).where(
                services.c.game_id == game_id,
                services.c.is_active.is_(True),
            )
        ).scalar_one()

        for sort_order, (name, price) in enumerate(additions, start=3):
            if name in existing_names or enabled_count >= 5:
                continue
            connection.execute(
                services.insert().values(
                    game_id=game_id,
                    name=name,
                    price=price,
                    description="按需求提供专业服务",
                    sort_order=sort_order,
                    is_active=True,
                    created_at=sa.func.now(),
                    updated_at=sa.func.now(),
                )
            )
            existing_names.add(name)
            enabled_count += 1


def downgrade() -> None:
    pass
