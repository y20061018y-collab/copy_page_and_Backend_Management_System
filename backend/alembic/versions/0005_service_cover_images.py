from alembic import op
import sqlalchemy as sa


revision = "0005_service_cover_images"
down_revision = ("0004_add_service_cover_images", "0004_service_items")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "UPDATE game_services SET cover_image = "
        "(SELECT cover_image FROM games WHERE games.id = game_services.game_id)"
    )
    op.alter_column(
        "game_services",
        "cover_image",
        existing_type=sa.String(length=255),
        nullable=False,
        server_default="",
    )


def downgrade() -> None:
    op.alter_column(
        "game_services",
        "cover_image",
        existing_type=sa.String(length=255),
        nullable=True,
        server_default=None,
    )
