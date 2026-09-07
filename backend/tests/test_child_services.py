import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.game_catalog import GameCatalog
from app.models import ChildService, Game, GameService
from app.public_game_catalog import PublicGameCatalog
from app.schemas import ChildServiceWrite, ReorderItem


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
    visible_service = GameService(name="日常委托", price="¥ 30", description="每日基础", sort_order=0, is_active=True)
    visible_service.child_services = [
        ChildService(
            name="12",
            price="¥ 88",
            description="完成进阶目标。",
            image_path=None,
            sort_order=2,
        ),
        ChildService(
            name="11",
            price="¥ 30",
            description="完成基础目标与前置内容。",
            image_path="/uploads/games/child-service-sample.png",
            sort_order=1,
        ),
    ]
    hidden_service = GameService(name="隐藏服务", price="¥ 99", description="后台可见", sort_order=1, is_active=False)
    hidden_service.child_services = [
        ChildService(name="后台子服务", price="¥ 9", description="仅后台读取。", image_path=None, sort_order=0)
    ]
    game = Game(
        name="原神",
        slug="genshin",
        tag="开放世界",
        description="探索提瓦特",
        cover_image="/images/games/原神.jpg",
        accent_color="#7c3aed",
        accent_color_2="#06b6d4",
        sort_order=0,
        is_active=True,
        services=[visible_service, hidden_service],
    )
    db.add(game)
    db.commit()


def test_child_services_persist_nullable_images_and_cascade_with_service(db: Session):
    service = db.scalar(select(GameService).where(GameService.name == "日常委托"))
    child_services = list(db.scalars(select(ChildService).where(ChildService.game_service_id == service.id)))

    assert {child_service.image_path for child_service in child_services} == {
        "/uploads/games/child-service-sample.png",
        None,
    }

    db.delete(service)
    db.commit()

    remaining_child_services = list(db.scalars(select(ChildService)))
    assert all(child_service.game_service_id != service.id for child_service in remaining_child_services)
    assert [child_service.name for child_service in remaining_child_services] == ["后台子服务"]


def test_public_catalog_reads_sorted_child_services_for_enabled_services(db: Session):
    games = PublicGameCatalog(db).list_games()

    service = games[0].services[0]
    assert service.name == "日常委托"
    assert [child_service.name for child_service in service.child_services] == ["11", "12"]
    assert [child_service.price for child_service in service.child_services] == ["¥ 30", "¥ 88"]
    assert [child_service.image_path for child_service in service.child_services] == [
        "/uploads/games/child-service-sample.png",
        None,
    ]
    assert all(service.name != "隐藏服务" for service in games[0].services)


def test_admin_catalog_reads_sorted_child_services_for_all_services(db: Session):
    games = GameCatalog(db).list_admin_games()

    services = games[0].services
    assert [service.name for service in services] == ["日常委托", "隐藏服务"]
    assert [child_service.name for child_service in services[0].child_services] == ["11", "12"]
    assert [child_service.name for child_service in services[1].child_services] == ["后台子服务"]


def test_api_read_shape_includes_empty_child_service_lists(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
    game = client.post(
        "/api/admin/games",
        json={
            "name": "测试游戏",
            "slug": "empty-child-service-game",
            "tag": "测试",
            "description": "测试说明",
            "cover_image": "/images/games/原神.jpg",
            "accent_color": "#111111",
            "accent_color_2": "#222222",
            "sort_order": 99,
            "is_active": True,
        },
    ).json()
    service = client.post(
        f"/api/admin/games/{game['id']}/services",
        json={"name": "测试服务", "price": "¥ 1", "description": "说明", "sort_order": 0, "is_active": True},
    ).json()

    public_service = client.get("/api/games").json()[-1]["services"][0]
    admin_service = client.get("/api/admin/games").json()[-1]["services"][0]
    assert public_service["id"] == service["id"]
    assert admin_service["id"] == service["id"]
    assert public_service["child_services"] == []
    assert admin_service["child_services"] == []


def test_catalog_manages_child_services_with_optional_images(db: Session):
    service = db.scalar(select(GameService).where(GameService.name == "日常委托"))
    catalog = GameCatalog(db)

    created = catalog.create_child_service(
        service.id,
        ChildServiceWrite(name="13", price="¥ 66", description="完成扩展目标。", image_path=None, sort_order=3),
    )
    updated = catalog.update_child_service(
        created.id,
        ChildServiceWrite(
            name="13-进阶",
            price="¥ 76",
            description="完成扩展目标与收尾。",
            image_path="/uploads/games/child-service-updated.webp",
            sort_order=0,
        ),
    )

    assert updated.name == "13-进阶"
    assert updated.image_path == "/uploads/games/child-service-updated.webp"

    children = GameCatalog(db).list_admin_games()[0].services[0].child_services
    catalog.reorder_child_services(
        service.id,
        [ReorderItem(id=child.id, sort_order=index) for index, child in enumerate(reversed(children))],
    )

    reordered = GameCatalog(db).list_admin_games()[0].services[0].child_services
    assert [child.sort_order for child in reordered] == [0, 1, 2]

    catalog.delete_child_service(created.id)

    assert db.get(ChildService, created.id) is None


def test_admin_api_manages_child_services_and_public_reads_them(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
    game = client.post(
        "/api/admin/games",
        json={
            "name": "接口子服务测试",
            "slug": "api-child-service-game",
            "tag": "测试",
            "description": "测试说明",
            "cover_image": "/images/games/原神.jpg",
            "accent_color": "#111111",
            "accent_color_2": "#222222",
            "sort_order": 99,
            "is_active": True,
        },
    ).json()
    service = client.post(
        f"/api/admin/games/{game['id']}/services",
        json={"name": "测试服务", "price": "¥ 1", "description": "说明", "sort_order": 0, "is_active": True},
    ).json()

    text_child = client.post(
        f"/api/admin/services/{service['id']}/child-services",
        json={"name": "11", "price": "¥ 30", "description": "完成基础目标与前置内容。", "sort_order": 1},
    )
    image_child = client.post(
        f"/api/admin/services/{service['id']}/child-services",
        json={
            "name": "12",
            "price": "¥ 88",
            "description": "完成进阶目标。",
            "image_path": "/uploads/games/child-service.png",
            "sort_order": 2,
        },
    )
    updated = client.patch(
        f"/api/admin/child-services/{text_child.json()['id']}",
        json={
            "name": "10",
            "price": "¥ 20",
            "description": "完成入门目标。",
            "image_path": None,
            "sort_order": 0,
        },
    )
    reordered = client.patch(
        f"/api/admin/services/{service['id']}/child-services/reorder",
        json=[
            {"id": image_child.json()["id"], "sort_order": 0},
            {"id": text_child.json()["id"], "sort_order": 1},
        ],
    )
    public_game = next(game for game in client.get("/api/games").json() if game["slug"] == "api-child-service-game")
    public_child_services = public_game["services"][0]["child_services"]
    deleted = client.delete(f"/api/admin/child-services/{image_child.json()['id']}")
    public_game_after_delete = next(game for game in client.get("/api/games").json() if game["slug"] == "api-child-service-game")
    after_delete = public_game_after_delete["services"][0]["child_services"]

    assert text_child.status_code == 201
    assert text_child.json()["image_path"] is None
    assert image_child.status_code == 201
    assert updated.status_code == 200
    assert updated.json()["image_path"] is None
    assert reordered.status_code == 200
    assert [child["name"] for child in public_child_services] == ["12", "10"]
    assert public_child_services[0]["image_path"] == "/uploads/games/child-service.png"
    assert public_child_services[1]["image_path"] is None
    assert deleted.status_code == 204
    assert [child["name"] for child in after_delete] == ["10"]
