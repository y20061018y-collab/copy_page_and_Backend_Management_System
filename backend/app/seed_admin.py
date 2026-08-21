import os

from app.database import SessionLocal, initialize_database
from app.models import AdminUser
from app.security import password_hash


def seed_admin() -> None:
    initialize_database()
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin-password")
    with SessionLocal() as db:
        if not db.query(AdminUser).filter_by(username=username).first():
            db.add(AdminUser(username=username, password_hash=password_hash.hash(password)))
            db.commit()


if __name__ == "__main__":
    seed_admin()
