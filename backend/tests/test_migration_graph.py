import ast
from pathlib import Path


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


def test_migration_history_has_a_single_head_after_removing_service_prices():
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
    assert set(revisions) - referenced_revisions == {"0006_remove_service_prices"}
