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
