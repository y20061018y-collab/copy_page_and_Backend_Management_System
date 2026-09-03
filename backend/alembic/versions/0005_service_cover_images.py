from alembic import op
import sqlalchemy as sa


revision = "0005_service_cover_images"
down_revision = "0004_service_items"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "game_services",
        sa.Column("cover_image", sa.String(length=255), nullable=False, server_default=""),
    )
    op.execute(
        "UPDATE game_services SET cover_image = "
        "(SELECT cover_image FROM games WHERE games.id = game_services.game_id)"
    )


def downgrade() -> None:
    op.drop_column("game_services", "cover_image")
