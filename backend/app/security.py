from datetime import datetime, timedelta, timezone
import os

import jwt
from fastapi import HTTPException, Request, status
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.models import AdminUser

password_hash = PasswordHash.recommended()
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "development-only-change-me")
COOKIE_NAME = "access_token"


def create_token(user: AdminUser) -> str:
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode({"sub": str(user.id), "exp": expires}, SECRET_KEY, algorithm="HS256")


def get_current_admin(request: Request, db: Session) -> AdminUser:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    try:
        user_id = int(jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录") from None
    user = db.get(AdminUser, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    return user
