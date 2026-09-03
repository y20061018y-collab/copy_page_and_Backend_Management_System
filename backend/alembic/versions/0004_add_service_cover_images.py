from alembic import op
import sqlalchemy as sa


revision = "0004_add_service_cover_images"
down_revision = "0003_backfill_seed_services"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("game_services", sa.Column("cover_image", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("game_services", "cover_image")
