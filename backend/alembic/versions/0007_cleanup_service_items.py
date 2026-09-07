from alembic import op
import sqlalchemy as sa


revision = "0007_cleanup_service_items"
down_revision = "0006_remove_service_prices"
branch_labels = None
depends_on = None


def _table_names(connection) -> set[str]:
    return set(sa.inspect(connection).get_table_names())


def _column_names(connection, table_name: str) -> set[str]:
    return {column["name"] for column in sa.inspect(connection).get_columns(table_name)}


def _restore_price_column_if_missing(connection) -> None:
    if "game_services" not in _table_names(connection):
        return
    if "price" in _column_names(connection, "game_services"):
        return

    with op.batch_alter_table("game_services") as batch_op:
        batch_op.add_column(sa.Column("price", sa.String(length=80), nullable=False, server_default=""))
    with op.batch_alter_table("game_services") as batch_op:
        batch_op.alter_column(
            "price",
            existing_type=sa.String(length=80),
            nullable=False,
            server_default=None,
        )


def upgrade() -> None:
    connection = op.get_bind()
    _restore_price_column_if_missing(connection)


def downgrade() -> None:
    pass
