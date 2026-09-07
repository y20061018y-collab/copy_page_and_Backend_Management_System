import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

from sqlalchemy import create_engine, inspect, text


def load_migration(monkeypatch):
    monkeypatch.setitem(sys.modules, "alembic", SimpleNamespace(op=SimpleNamespace(get_bind=lambda: None)))
    migration_path = Path(__file__).parents[1] / "alembic" / "versions" / "0007_cleanup_service_items.py"
    spec = importlib.util.spec_from_file_location("cleanup_service_items", migration_path)
    migration = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(migration)
    return migration


class FakeBatchOperation:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def add_column(self, column):
        self.connection.execute(text("ALTER TABLE game_services ADD COLUMN price VARCHAR(80) NOT NULL DEFAULT ''"))

    def alter_column(self, *args, **kwargs):
        return None


class FakeOperation:
    def __init__(self, connection):
        self.connection = connection

    def get_bind(self):
        return self.connection

    def batch_alter_table(self, table_name):
        assert table_name == "game_services"
        return FakeBatchOperation(self.connection)

def test_cleanup_migration_preserves_legacy_service_items_and_restores_price_column(monkeypatch):
    migration = load_migration(monkeypatch)
    engine = create_engine("sqlite://")

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE game_services (
                    id INTEGER PRIMARY KEY,
                    game_id INTEGER NOT NULL,
                    name VARCHAR(120) NOT NULL,
                    description TEXT NOT NULL,
                    cover_image VARCHAR(255) NOT NULL,
                    sort_order INTEGER NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
                """
            )
        )
        connection.execute(text("CREATE TABLE service_items (id INTEGER PRIMARY KEY)"))

        migration.op = FakeOperation(connection)
        migration.upgrade()

        inspector = inspect(connection)
        assert "service_items" in inspector.get_table_names()
        service_columns = {column["name"]: column for column in inspector.get_columns("game_services")}
        assert service_columns["price"]["nullable"] is False
