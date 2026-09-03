from alembic import op
import sqlalchemy as sa


revision = "0006_remove_service_prices"
down_revision = "0005_service_cover_images"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("game_services", "price")


def downgrade() -> None:
    op.add_column(
        "game_services",
        sa.Column("price", sa.String(length=80), nullable=False, server_default=""),
    )
    op.alter_column("game_services", "price", server_default=None)
