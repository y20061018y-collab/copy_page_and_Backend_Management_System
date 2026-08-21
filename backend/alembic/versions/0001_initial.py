from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("games", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("slug", sa.String(120), nullable=False), sa.Column("tag", sa.String(120), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("cover_image", sa.String(255), nullable=False), sa.Column("accent_color", sa.String(20), nullable=False), sa.Column("accent_color_2", sa.String(20), nullable=False), sa.Column("sort_order", sa.Integer(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_games_slug", "games", ["slug"], unique=True)
    op.create_table("game_services", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("game_id", sa.Integer(), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("price", sa.String(80), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("sort_order", sa.Integer(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_game_services_game_id", "game_services", ["game_id"])
    op.create_table("site_settings", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("site_name", sa.String(120), nullable=False), sa.Column("site_subtitle", sa.String(255), nullable=False), sa.Column("studio_image", sa.String(255)), sa.Column("contact_wechat", sa.String(120)), sa.Column("contact_qq", sa.String(120)), sa.Column("contact_phone", sa.String(80)), sa.Column("contact_description", sa.Text()), sa.Column("updated_at", sa.DateTime(), nullable=False))


def downgrade() -> None:
    op.drop_table("site_settings")
    op.drop_index("ix_game_services_game_id", table_name="game_services")
    op.drop_table("game_services")
    op.drop_index("ix_games_slug", table_name="games")
    op.drop_table("games")
