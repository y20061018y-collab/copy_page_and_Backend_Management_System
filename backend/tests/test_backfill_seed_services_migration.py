import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Game, GameService


def test_backfill_adds_only_missing_defaults_without_overwriting_edits_or_exceeding_cap(monkeypatch):
    alembic_stub = SimpleNamespace(op=SimpleNamespace(get_bind=lambda: None))
    monkeypatch.setitem(sys.modules, "alembic", alembic_stub)
    migration_path = Path(__file__).parents[1] / "alembic" / "versions" / "0003_backfill_seed_services.py"
    spec = importlib.util.spec_from_file_location("backfill_seed_services", migration_path)
    migration = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        genshin = Game(
            name="原神", slug="genshin", tag="测试", description="测试", cover_image="/test.jpg",
            accent_color="#111111", accent_color_2="#222222", sort_order=0, is_active=True,
        )
        capped = Game(
            name="已满服务游戏", slug="star-rail", tag="测试", description="测试", cover_image="/test.jpg",
            accent_color="#111111", accent_color_2="#222222", sort_order=1, is_active=True,
        )
        genshin.services = [
            GameService(name="日常委托", price="¥ 30", description="默认", sort_order=0, is_active=True),
            GameService(name="深渊满星", price="¥ 88", description="默认", sort_order=1, is_active=True),
            GameService(name="角色培养", price="¥ 120", description="默认", sort_order=2, is_active=True),
            GameService(name="提瓦特探索", price="¥ 999", description="管理员编辑", sort_order=3, is_active=True),
        ]
        capped.services = [
            GameService(name=f"自定义服务 {index}", price="¥ 1", description="管理员添加", sort_order=index, is_active=True)
            for index in range(5)
        ]
        session.add_all([genshin, capped])
        session.commit()

        monkeypatch.setattr(migration.op, "get_bind", lambda: session.connection())
        migration.upgrade()
        migration.upgrade()
        session.commit()

        genshin_services = list(session.scalars(select(GameService).where(GameService.game_id == genshin.id)))
        capped_services = list(session.scalars(select(GameService).where(GameService.game_id == capped.id)))

    assert len(genshin_services) == 5
    assert sum(service.name == "养成目标" for service in genshin_services) == 1
    edited_service = next(service for service in genshin_services if service.name == "提瓦特探索")
    assert (edited_service.price, edited_service.description) == ("¥ 999", "管理员编辑")
    assert len(capped_services) == 5
