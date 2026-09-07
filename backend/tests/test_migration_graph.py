import ast
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import sqlalchemy as sa
from sqlalchemy import create_engine, inspect, text


def migration_revisions(versions_dir: Path) -> dict[str, str | tuple[str, ...] | None]:
    revisions: dict[str, str | tuple[str, ...] | None] = {}
    for migration_path in versions_dir.glob("[0-9]*.py"):
        assignments = {
            node.targets[0].id: ast.literal_eval(node.value)
            for node in ast.parse(migration_path.read_text(encoding="utf-8")).body
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
        }
        revisions[assignments["revision"]] = assignments["down_revision"]
    return revisions


def test_migration_history_has_a_single_head_while_preserving_service_prices():
    backend_dir = Path(__file__).parents[1]
    legacy_migration = backend_dir / "alembic" / "versions" / "0004_add_service_cover_images.py"
    revisions = migration_revisions(backend_dir / "alembic" / "versions")
    referenced_revisions = {
        parent
        for down_revision in revisions.values()
        for parent in (down_revision if isinstance(down_revision, tuple) else (down_revision,))
        if parent is not None
    }

    assert legacy_migration.exists()
    assert revisions["0005_service_cover_images"] == (
        "0004_add_service_cover_images",
        "0004_service_items",
    )
    assert revisions["0006_remove_service_prices"] == "0005_service_cover_images"
    assert revisions["0007_cleanup_service_items"] == "0006_remove_service_prices"
    assert revisions["0008_add_child_services"] == "0007_cleanup_service_items"
    assert set(revisions) - referenced_revisions == {"0008_add_child_services"}


def load_child_services_migration(monkeypatch):
    monkeypatch.setitem(sys.modules, "alembic", SimpleNamespace(op=SimpleNamespace(get_bind=lambda: None)))
    migration_path = Path(__file__).parents[1] / "alembic" / "versions" / "0008_add_child_services.py"
    spec = importlib.util.spec_from_file_location("add_child_services", migration_path)
    migration = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(migration)
    return migration


class FakeOperation:
    def __init__(self, connection):
        self.connection = connection

    def create_table(self, table_name, *columns):
        metadata = sa.MetaData()
        sa.Table("game_services", metadata, sa.Column("id", sa.Integer(), primary_key=True))
        table = sa.Table(table_name, metadata, *columns)
        table.create(self.connection)

    def create_index(self, index_name, table_name, columns):
        column_list = ", ".join(columns)
        self.connection.execute(text(f"CREATE INDEX {index_name} ON {table_name} ({column_list})"))

    def get_bind(self):
        return self.connection

    def execute(self, statement):
        self.connection.execute(statement)

    def drop_index(self, index_name, table_name):
        self.connection.execute(text(f"DROP INDEX {index_name}"))

    def drop_table(self, table_name):
        self.connection.execute(text(f"DROP TABLE {table_name}"))


def test_child_services_migration_upgrades_and_copies_active_legacy_items(monkeypatch):
    migration = load_child_services_migration(monkeypatch)
    engine = create_engine("sqlite://")

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE game_services (
                    id INTEGER PRIMARY KEY,
                    game_id INTEGER NOT NULL,
                    name VARCHAR(120) NOT NULL,
                    price VARCHAR(80) NOT NULL,
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
        connection.execute(
            text(
                """
                CREATE TABLE service_items (
                    id INTEGER PRIMARY KEY,
                    service_id INTEGER NOT NULL,
                    name VARCHAR(120) NOT NULL,
                    price VARCHAR(80) NOT NULL,
                    description TEXT NOT NULL,
                    sort_order INTEGER NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO service_items (
                    id,
                    service_id,
                    name,
                    price,
                    description,
                    sort_order,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES
                    (1, 10, '基础方案', '¥ 30', '公开显示', 0, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
                    (2, 10, '隐藏方案', '¥ 99', '不公开显示', 1, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
            )
        )
        migration.op = FakeOperation(connection)

        migration.upgrade()

        inspector = inspect(connection)
        assert "child_services" in inspector.get_table_names()
        child_columns = {column["name"]: column for column in inspector.get_columns("child_services")}
        assert child_columns["game_service_id"]["nullable"] is False
        assert child_columns["name"]["nullable"] is False
        assert child_columns["price"]["nullable"] is False
        assert child_columns["description"]["nullable"] is False
        assert child_columns["image_path"]["nullable"] is True
        assert child_columns["sort_order"]["nullable"] is False
        service_columns = {column["name"] for column in inspector.get_columns("game_services")}
        assert "price" in service_columns
        rows = connection.execute(text("SELECT game_service_id, name, price, description, image_path, sort_order FROM child_services")).all()
        assert rows == [(10, "基础方案", "¥ 30", "公开显示", None, 0)]
        assert "service_items" in inspector.get_table_names()

        migration.downgrade()

        inspector = inspect(connection)
        assert "child_services" not in inspector.get_table_names()
        service_columns = {column["name"] for column in inspector.get_columns("game_services")}
        assert "price" in service_columns
