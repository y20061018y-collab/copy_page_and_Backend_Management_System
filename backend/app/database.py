from collections.abc import Generator
from pathlib import Path
import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./esports.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database() -> None:
    from app.models import AdminUser, Game, GameService, SiteSetting
    from app.security import password_hash

    required_tables = {"games", "game_services", "site_settings", "admin_users"}
    existing_tables = set(inspect(engine).get_table_names())
    missing_tables = required_tables - existing_tables
    if missing_tables:
        missing = ", ".join(sorted(missing_tables))
        raise RuntimeError(
            f"数据库尚未完成 Alembic 迁移，缺少表：{missing}。"
            "请先在 backend 目录执行：alembic upgrade head"
        )

    with SessionLocal() as db:
        if not db.query(Game).count():
            from app.seed import seed_database

            seed_database(db)
        if not db.query(AdminUser).count():
            db.add(AdminUser(username=os.getenv("ADMIN_USERNAME", "admin"), password_hash=password_hash.hash(os.getenv("ADMIN_PASSWORD", "admin-password"))))
            db.commit()
