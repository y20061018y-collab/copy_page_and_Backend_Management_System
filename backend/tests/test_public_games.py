from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import ChildService, GameService
from app.seed import seed_database


def test_public_games_returns_seeded_enabled_games_in_order(client):
    response = client.get("/api/games")

    assert response.status_code == 200
    games = response.json()
    assert [game["slug"] for game in games] == ["genshin", "star-rail", "zenless-zone-zero", "wuthering-waves"]
    assert all(game["is_active"] for game in games)
    assert games[0]["services"][0]["price"] == "¥ 30"
    assert games[0]["services"][0]["cover_image"] == games[0]["cover_image"]


def test_admin_can_set_a_service_cover_without_changing_the_game_cover(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
    game = client.get("/api/admin/games").json()[0]
    service = game["services"][0]

    updated = client.patch(
        f"/api/admin/services/{service['id']}",
        json={
            "name": service["name"], "description": service["description"],
            "price": service["price"], "cover_image": "/uploads/games/custom-service-cover.jpg", "sort_order": service["sort_order"], "is_active": service["is_active"],
        },
    )
    public_game = client.get("/api/games").json()[0]

    assert updated.status_code == 200
    assert public_game["cover_image"] == game["cover_image"]
    assert public_game["services"][0]["cover_image"] == "/uploads/games/custom-service-cover.jpg"


def test_seeded_games_have_five_enabled_services(client):
    games = client.get("/api/games").json()

    assert len(games) == 4
    assert all(len(game["services"]) == 5 for game in games)
    assert all(service["price"] for game in games for service in game["services"])


def test_seeded_services_have_child_services_with_selective_images(client):
    games = client.get("/api/games").json()
    services = [service for game in games for service in game["services"]]
    child_services = [child_service for service in services for child_service in service["child_services"]]

    assert all(len(service["child_services"]) == 5 for service in services)
    assert len(child_services) == 100
    assert all(child_service["price"] for child_service in child_services)
    assert all(child_service["name"] for child_service in child_services)
    image_paths = [child_service["image_path"] for child_service in child_services if child_service["image_path"]]
    assert image_paths == [
        "/uploads/games/Yb6_WgZ3yKUIniYzu0yPCw.jpg",
        "/uploads/games/tfJPOelVXhZQhumO_D21VQ.png",
        "/uploads/games/LEZEaGEkmC2yqp2rCOpHcQ.png",
    ]
    assert any(child_service["image_path"] is None for child_service in child_services)


def test_seed_database_is_repeatable_for_child_services():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    try:
        with SessionLocal() as session:
            seed_database(session)
            seed_database(session)

            services = list(session.scalars(select(GameService)))
            child_services = list(session.scalars(select(ChildService)))

        assert len(services) == 20
        assert len(child_services) == 100
    finally:
        Base.metadata.drop_all(engine)


def test_public_services_do_not_expose_child_project_contract(client):
    service = client.get("/api/games").json()[0]["services"][0]

    assert "items" not in service


def test_public_settings_returns_contact_fields(client):
    response = client.get("/api/settings")

    assert response.status_code == 200
    assert response.json()["site_name"] == "11号电竞"
    assert response.json()["contact_description"] == "欢迎联系我们咨询服务详情"


def test_admin_login_sets_cookie_and_dashboard_requires_authentication(client):
    denied = client.get("/api/admin/dashboard")
    login = client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
    dashboard = client.get("/api/admin/dashboard")

    assert denied.status_code == 401
    assert login.status_code == 200
    assert "access_token" in login.cookies
    assert dashboard.json()["game_count"] == 4
    assert dashboard.json()["content_health_score"] == 80


def test_admin_can_create_game_and_service_then_disable_service(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
    game = client.post("/api/admin/games", json={"name": "测试游戏", "slug": "test-game", "tag": "测试", "description": "测试简介", "cover_image": "/images/games/原神.jpg", "accent_color": "#111111", "accent_color_2": "#222222", "sort_order": 99, "is_active": True})
    service = client.post(f"/api/admin/games/{game.json()['id']}/services", json={"name": "测试服务", "price": "¥ 1", "description": "说明", "sort_order": 0, "is_active": True})
    disabled = client.post(f"/api/admin/services/{service.json()['id']}/disable")
    public = client.get("/api/games")

    assert game.status_code == 201
    assert service.status_code == 201
    assert disabled.status_code == 200
    created = next(item for item in public.json() if item["slug"] == "test-game")
    assert created["services"] == []


def test_admin_receives_conflict_for_a_sixth_enabled_service(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
    game = client.get("/api/admin/games").json()[0]

    response = client.post(
        f"/api/admin/games/{game['id']}/services",
        json={"name": "第六项", "price": "¥ 1", "description": "测试", "sort_order": 99, "is_active": True},
    )

    assert response.status_code == 409
    assert response.json() == {"code": "SERVICE_LIMIT_REACHED", "message": "每个游戏最多 5 个启用需求", "details": {}}


def test_admin_receives_conflict_when_update_enables_a_sixth_service(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
    game = client.get("/api/admin/games").json()[0]
    disabled = client.post(
        f"/api/admin/games/{game['id']}/services",
        json={"name": "禁用需求", "price": "¥ 1", "description": "测试", "sort_order": 12, "is_active": False},
    ).json()

    response = client.patch(
        f"/api/admin/services/{disabled['id']}",
        json={"name": "禁用需求", "price": "¥ 1", "description": "测试", "sort_order": 12, "is_active": True},
    )

    assert response.status_code == 409
    assert response.json() == {"code": "SERVICE_LIMIT_REACHED", "message": "每个游戏最多 5 个启用需求", "details": {}}


def test_admin_receives_conflict_when_enabling_a_sixth_service(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
    game = client.get("/api/admin/games").json()[0]
    disabled = client.post(
        f"/api/admin/games/{game['id']}/services",
        json={"name": "禁用需求", "price": "¥ 1", "description": "测试", "sort_order": 12, "is_active": False},
    ).json()

    response = client.post(f"/api/admin/services/{disabled['id']}/enable")

    assert response.status_code == 409
    assert response.json() == {"code": "SERVICE_LIMIT_REACHED", "message": "每个游戏最多 5 个启用需求", "details": {}}


def test_admin_can_update_site_settings(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
    updated = client.patch("/api/admin/settings", json={"site_name": "新工作室", "site_subtitle": "新副标题", "studio_image": "/images/studio.jpg", "contact_wechat": "wx-test", "contact_qq": "12345", "contact_phone": "13800000000", "contact_description": "欢迎咨询"})
    public = client.get("/api/settings")

    assert updated.status_code == 200
    assert public.json()["site_name"] == "新工作室"
    assert public.json()["contact_wechat"] == "wx-test"


def test_admin_can_reorder_games(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
    games = client.get("/api/admin/games").json()
    order = [games[1], games[0], *games[2:]]

    response = client.patch(
        "/api/admin/games/reorder",
        json=[{"id": game["id"], "sort_order": position} for position, game in enumerate(order)],
    )
    public = client.get("/api/games")

    assert response.status_code == 200
    assert [game["id"] for game in public.json()] == [game["id"] for game in order]


def test_invalid_login_returns_structured_error_and_logout_clears_cookie(client):
    invalid = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
    logged_out = client.post("/api/auth/logout")
    current = client.get("/api/auth/me")

    assert invalid.status_code == 401
    assert invalid.json()["code"] == "AUTH_INVALID_CREDENTIALS"
    assert logged_out.status_code == 204
    assert current.status_code == 401
    assert current.json() == {"code": "AUTH_REQUIRED", "message": "未登录", "details": {}}


def test_invalid_upload_extension_returns_structured_error(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})

    response = client.post(
        "/api/admin/uploads/game-cover",
        files={"file": ("cover.txt", b"\xff\xd8\xffimage", "image/jpeg")},
    )

    assert response.status_code == 422
    assert response.json() == {"code": "UPLOAD_INVALID_TYPE", "message": "不支持的图片类型", "details": {}}


def test_cover_upload_accepts_a_valid_image_with_a_generic_browser_mime_type(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})

    response = client.post(
        "/api/admin/uploads/game-cover",
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\nimage-data", "application/octet-stream")},
    )

    assert response.status_code == 200
    uploaded_path = response.json()["path"]
    try:
        assert uploaded_path.endswith(".png")
        assert client.get(uploaded_path).status_code == 200
    finally:
        Path(uploaded_path.lstrip("/")).unlink(missing_ok=True)


def test_invalid_request_returns_structured_error(client):
    response = client.post("/api/auth/login", json={"username": "admin"})

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert response.json()["message"] == "请求数据无效"
    assert response.json()["details"]
