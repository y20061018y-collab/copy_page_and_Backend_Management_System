from fastapi.testclient import TestClient

from app.main import app


def test_public_games_returns_seeded_enabled_games_in_order():
    with TestClient(app) as client:
        response = client.get("/api/games")

    assert response.status_code == 200
    games = response.json()
    assert [game["slug"] for game in games] == ["genshin", "star-rail", "zenless-zone-zero", "wuthering-waves"]
    assert all(game["is_active"] for game in games)
    assert games[0]["services"][0]["price"] == "¥ 30"


def test_public_settings_returns_contact_fields():
    with TestClient(app) as client:
        response = client.get("/api/settings")

    assert response.status_code == 200
    assert response.json()["site_name"] == "11号电竞"
    assert response.json()["contact_description"] == "欢迎联系我们咨询服务详情"


def test_admin_login_sets_cookie_and_dashboard_requires_authentication():
    with TestClient(app) as client:
        denied = client.get("/api/admin/dashboard")
        login = client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
        dashboard = client.get("/api/admin/dashboard")

    assert denied.status_code == 401
    assert login.status_code == 200
    assert "access_token" in login.cookies
    assert dashboard.json()["game_count"] == 4


def test_admin_can_create_game_and_service_then_disable_service():
    with TestClient(app) as client:
        client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
        game = client.post("/api/admin/games", json={"name": "测试游戏", "slug": "test-game", "tag": "测试", "description": "测试简介", "cover_image": "/images/games/原神.jpg", "accent_color": "#111111", "accent_color_2": "#222222", "sort_order": 99, "is_active": True})
        service = client.post(f"/api/admin/games/{game.json()['id']}/services", json={"name": "测试服务", "price": "¥ 10", "description": "说明", "sort_order": 0, "is_active": True})
        disabled = client.post(f"/api/admin/services/{service.json()['id']}/disable")
        public = client.get("/api/games")

    assert game.status_code == 201
    assert service.status_code == 201
    assert disabled.status_code == 200
    created = next(item for item in public.json() if item["slug"] == "test-game")
    assert created["services"] == []
