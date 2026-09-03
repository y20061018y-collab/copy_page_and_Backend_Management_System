from sqlalchemy.orm import Session

from app.models import Game, GameService, ServiceItem, SiteSetting


SEED_GAMES = [
    ("原神", "genshin", "开放世界 · 角色养成", "探索提瓦特，轻松完成养成目标。", "/images/games/原神.jpg", "#7c3aed", "#06b6d4", ["日常委托", "深渊满星", "角色培养", "提瓦特探索", "养成目标"]),
    ("崩坏·星穹铁道", "star-rail", "回合制 · 银河冒险", "专业代打，助你快速完成版本内容。", "/images/games/崩坏·星穹铁道.jpg", "#2563eb", "#ec4899", ["日常任务", "混沌回忆", "角色培养", "版本内容", "银河冒险"]),
    ("绝区零", "zenless-zone-zero", "动作战斗 · 都市幻想", "高效完成零号空洞与角色养成服务。", "/images/games/绝区零.jpg", "#f97316", "#ef4444", ["每日活跃", "零号空洞", "代理人培养", "都市幻想", "角色养成"]),
    ("鸣潮", "wuthering-waves", "开放世界 · 动作冒险", "稳定可靠的鸣潮账号养成服务。", "/images/games/鸣潮.jpg", "#0891b2", "#8b5cf6", ["每日任务", "无音区材料", "角色培养", "账号养成", "动作冒险"]),
]

SEED_SERVICE_ITEMS = [
    ("基础方案", "¥ 30", "完成基础目标与前置内容。"),
    ("标准方案", "¥ 88", "按推荐路线完成主要内容。"),
    ("进阶方案", "¥ 120", "包含高难目标与资源规划。"),
    ("定制方案", "¥ 30", "根据账号进度安排执行内容。"),
    ("专属方案", "¥ 120", "沟通后提供专属服务安排。"),
]


def seed_database(db: Session) -> None:
    for order, (name, slug, tag, description, cover, color, color2, services) in enumerate(SEED_GAMES):
        game = Game(name=name, slug=slug, tag=tag, description=description, cover_image=cover, accent_color=color, accent_color_2=color2, sort_order=order, is_active=True)
        game.services = [
            GameService(
                name=service_name,
                description="按需求提供专业服务",
                cover_image=cover,
                sort_order=index,
                is_active=True,
                items=[
                    ServiceItem(name=item_name, price=item_price, description=item_description, sort_order=item_index, is_active=True)
                    for item_index, (item_name, item_price, item_description) in enumerate(SEED_SERVICE_ITEMS)
                ],
            )
            for index, service_name in enumerate(services)
        ]
        db.add(game)
    db.add(SiteSetting(id=1, site_name="11号电竞", site_subtitle="专业游戏服务工作室", studio_image="/images/studio.jpg", contact_description="欢迎联系我们咨询服务详情"))
    db.commit()


if __name__ == "__main__":
    from app.database import SessionLocal, initialize_database

    initialize_database()
