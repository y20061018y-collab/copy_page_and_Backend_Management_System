import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.game_catalog import DuplicateGameSlug, EnabledServiceLimitReached, GameCatalog
from app.models import Game, GameService
from app.schemas import GameWrite, ReorderItem, ServiceWrite


@pytest.fixture()
def db() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    seed_catalog(session)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def seed_catalog(db: Session) -> None:
    active = Game(
        name="原神",
        slug="genshin",
        tag="开放世界",
        description="探索提瓦特",
        cover_image="/images/games/原神.jpg",
        accent_color="#7c3aed",
        accent_color_2="#06b6d4",
        sort_order=2,
        is_active=True,
    )
    active.services = [
        GameService(name="第二服务", description="第二", sort_order=2, is_active=True),
        GameService(name="隐藏服务", description="隐藏", sort_order=1, is_active=False),
        GameService(name="第一服务", description="第一", sort_order=0, is_active=True),
    ]
    disabled = Game(
        name="测试游戏",
        slug="test-game",
        tag="测试",
        description="测试",
        cover_image="/images/games/原神.jpg",
        accent_color="#111111",
        accent_color_2="#222222",
        sort_order=1,
        is_active=False,
    )
    db.add_all([active, disabled])
    db.commit()


def game_write(game: Game, **overrides) -> GameWrite:
    payload = {
        "name": game.name,
        "slug": game.slug,
        "tag": game.tag,
        "description": game.description,
        "cover_image": game.cover_image,
        "accent_color": game.accent_color,
        "accent_color_2": game.accent_color_2,
        "sort_order": game.sort_order,
        "is_active": game.is_active,
    }
    payload.update(overrides)
    return GameWrite(**payload)


def test_public_games_hide_disabled_games_and_services(db: Session):
    games = GameCatalog(db).list_public_games()

    assert [game.slug for game in games] == ["genshin"]
    assert [service.name for service in games[0].services] == ["第一服务", "第二服务"]


def test_admin_games_include_disabled_games_and_sort_services(db: Session):
    games = GameCatalog(db).list_admin_games()

    assert [game.slug for game in games] == ["test-game", "genshin"]
    assert [service.name for service in games[1].services] == ["第一服务", "隐藏服务", "第二服务"]


def test_disabled_game_can_be_updated_from_admin(db: Session):
    game = db.query(Game).filter_by(slug="test-game").one()
    updated = GameCatalog(db).update_game(game.id, game_write(game, name="后台维护测试游戏"))

    assert updated.name == "后台维护测试游戏"
    assert updated.is_active is False


def test_duplicate_slug_raises_catalog_error(db: Session):
    game = db.query(Game).filter_by(slug="test-game").one()

    with pytest.raises(DuplicateGameSlug):
        GameCatalog(db).update_game(game.id, game_write(game, slug="genshin"))


def test_reorder_services_is_catalog_responsibility(db: Session):
    game = db.query(Game).filter_by(slug="genshin").one()
    first, hidden, second = sorted(game.services, key=lambda service: service.sort_order)

    GameCatalog(db).reorder_services(
        game.id,
        [
            ReorderItem(id=second.id, sort_order=0),
            ReorderItem(id=hidden.id, sort_order=1),
            ReorderItem(id=first.id, sort_order=2),
        ],
    )

    services = GameCatalog(db).list_admin_games()[1].services
    assert [service.name for service in services] == ["第二服务", "隐藏服务", "第一服务"]


def test_dashboard_counts_come_from_catalog(db: Session):
    counts = GameCatalog(db).dashboard_counts()

    assert counts.game_count == 2
    assert counts.active_game_count == 1
    assert counts.service_count == 3
    assert counts.active_service_count == 2


def test_create_service_commits_and_returns_service(db: Session):
    game = db.query(Game).filter_by(slug="genshin").one()
    service = GameCatalog(db).create_service(
        game.id,
        ServiceWrite(name="新增服务", description="新增描述", sort_order=3, is_active=True),
    )

    assert service.id is not None
    assert db.get(GameService, service.id).name == "新增服务"


def test_create_service_rejects_a_sixth_enabled_service(db: Session):
    game = db.query(Game).filter_by(slug="genshin").one()
    catalog = GameCatalog(db)
    for index in range(3):
        catalog.create_service(
            game.id,
            ServiceWrite(name=f"补充需求 {index}", description="测试", sort_order=10 + index, is_active=True),
        )

    with pytest.raises(EnabledServiceLimitReached):
        catalog.create_service(
            game.id,
            ServiceWrite(name="第六项", description="测试", sort_order=99, is_active=True),
        )


def test_update_service_rejects_enabling_a_sixth_service(db: Session):
    game = db.query(Game).filter_by(slug="genshin").one()
    catalog = GameCatalog(db)
    for index in range(4):
        catalog.create_service(
            game.id,
            ServiceWrite(name=f"补充需求 {index}", description="测试", sort_order=10 + index, is_active=index < 3),
        )
    disabled_service = next(service for service in game.services if service.name == "补充需求 3")

    with pytest.raises(EnabledServiceLimitReached):
        catalog.update_service(
            disabled_service.id,
            ServiceWrite(name="补充需求 3", description="测试", sort_order=13, is_active=True),
        )


def test_set_service_enabled_rejects_a_sixth_service(db: Session):
    game = db.query(Game).filter_by(slug="genshin").one()
    catalog = GameCatalog(db)
    for index in range(4):
        catalog.create_service(
            game.id,
            ServiceWrite(name=f"补充需求 {index}", description="测试", sort_order=10 + index, is_active=index < 3),
        )
    disabled_service = next(service for service in game.services if service.name == "补充需求 3")

    with pytest.raises(EnabledServiceLimitReached):
        catalog.set_service_enabled(disabled_service.id, True)
