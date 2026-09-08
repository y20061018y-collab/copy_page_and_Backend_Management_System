from sqlalchemy.orm import Session

from app.models import ChildService, Game, GameService, SiteSetting


SEED_GAMES = [
    ("原神", "genshin", "开放世界 · 角色养成", "探索提瓦特，轻松完成养成目标。", "/images/games/原神.jpg", "#7c3aed", "#06b6d4", [("日常委托", "¥ 30"), ("深渊满星", "¥ 88"), ("角色培养", "¥ 120"), ("提瓦特探索", "¥ 30"), ("养成目标", "¥ 120")]),
    ("崩坏·星穹铁道", "star-rail", "回合制 · 银河冒险", "专业代打，助你快速完成版本内容。", "/images/games/崩坏·星穹铁道.jpg", "#2563eb", "#ec4899", [("日常任务", "¥ 25"), ("混沌回忆", "¥ 80"), ("角色培养", "¥ 100"), ("版本内容", "¥ 25"), ("银河冒险", "¥ 100")]),
    ("绝区零", "zenless-zone-zero", "动作战斗 · 都市幻想", "高效完成零号空洞与角色养成服务。", "/images/games/绝区零.jpg", "#f97316", "#ef4444", [("每日活跃", "¥ 20"), ("零号空洞", "¥ 60"), ("代理人培养", "¥ 100"), ("都市幻想", "¥ 20"), ("角色养成", "¥ 100")]),
    ("鸣潮", "wuthering-waves", "开放世界 · 动作冒险", "稳定可靠的鸣潮账号养成服务。", "/images/games/鸣潮.jpg", "#0891b2", "#8b5cf6", [("每日任务", "¥ 25"), ("无音区材料", "¥ 50"), ("角色培养", "¥ 120"), ("账号养成", "¥ 120"), ("动作冒险", "¥ 25")]),
]


CHILD_SERVICE_TEMPLATES = [
    ("11", "完成基础目标与前置内容。", "¥ 30"),
    ("12", "完成常规目标并补齐当日资源。", "¥ 45"),
    ("13", "完成进阶目标与常规收尾。", "¥ 60"),
    ("14", "处理高优先级挑战内容。", "¥ 88"),
    ("15", "按账号进度定制完整清单。", "¥ 120"),
]

def child_services_for(slug: str, service_name: str) -> list[ChildService]:
    return [
        ChildService(
            name=child_name,
            price=price,
            description=description,
            image_path=None,
            sort_order=index,
        )
        for index, (child_name, description, price) in enumerate(CHILD_SERVICE_TEMPLATES)
    ]


def seed_database(db: Session) -> None:
    for order, (name, slug, tag, description, cover, color, color2, services) in enumerate(SEED_GAMES):
        game = db.query(Game).filter_by(slug=slug).one_or_none()
        if game is None:
            game = Game(name=name, slug=slug, tag=tag, description=description, cover_image=cover, accent_color=color, accent_color_2=color2, sort_order=order, is_active=True)
            db.add(game)
        existing_services = {service.name: service for service in game.services}
        for index, (service_name, _service_price) in enumerate(services):
            service = existing_services.get(service_name)
            if service is None:
                service = GameService(
                    name=service_name,
                    price="",
                    description="按需求提供专业服务",
                    cover_image=cover,
                    sort_order=index,
                    is_active=True,
                )
                game.services.append(service)
            existing_child_services = {child_service.name for child_service in service.child_services}
            for child_service in child_services_for(slug, service_name):
                if child_service.name not in existing_child_services:
                    service.child_services.append(child_service)
    if db.get(SiteSetting, 1) is None:
        db.add(SiteSetting(id=1, site_name="11号电竞", site_subtitle="专业游戏服务工作室", studio_image="/images/studio.jpg", contact_description="欢迎联系我们咨询服务详情"))
    db.commit()


if __name__ == "__main__":
    from app.database import SessionLocal, initialize_database

    initialize_database()
