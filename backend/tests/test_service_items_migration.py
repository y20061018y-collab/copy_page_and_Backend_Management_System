import importlib.util
import sys
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace


class MigrationConnection:
    def __init__(self) -> None:
        self.batches: list[list[dict[str, object]]] = []

    def execute(self, statement, parameters=None):
        if parameters is None:
            return SimpleNamespace(scalars=lambda: [1, 2])
        self.batches.append(parameters)


def test_service_items_migration_inserts_five_utc_dated_defaults_per_existing_service(monkeypatch):
    alembic_stub = SimpleNamespace(op=SimpleNamespace())
    monkeypatch.setitem(sys.modules, "alembic", alembic_stub)
    migration_path = Path(__file__).parents[1] / "alembic" / "versions" / "0004_service_items.py"
    spec = importlib.util.spec_from_file_location("service_items_migration", migration_path)
    migration = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(migration)

    connection = MigrationConnection()
    monkeypatch.setattr(migration.op, "create_table", lambda *args: None, raising=False)
    monkeypatch.setattr(migration.op, "create_index", lambda *args: None, raising=False)
    monkeypatch.setattr(migration.op, "get_bind", lambda: connection, raising=False)

    migration.upgrade()

    inserted_items = [item for batch in connection.batches for item in batch]
    assert len(inserted_items) == 10
    assert {item["service_id"] for item in inserted_items} == {1, 2}
    assert all(isinstance(item["created_at"], datetime) for item in inserted_items)
    assert all(item["created_at"].utcoffset() == timedelta(0) for item in inserted_items)
    assert all(item["created_at"] == item["updated_at"] for item in inserted_items)
