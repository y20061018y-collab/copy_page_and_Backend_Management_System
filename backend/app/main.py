import os

from fastapi import Depends, FastAPI, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import Base, engine, get_db, initialize_database
from app.models import AdminUser, Game, GameService, SiteSetting
from app.schemas import AdminPublic, DashboardPublic, GamePublic, LoginRequest, SiteSettingPublic
from app.security import COOKIE_NAME, create_token, get_current_admin, password_hash

app = FastAPI(title="11号电竞 API")


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/api/games", response_model=list[GamePublic])
def list_public_games(db: Session = Depends(get_db)) -> list[Game]:
    statement = (
        select(Game)
        .where(Game.is_active.is_(True))
        .options(selectinload(Game.services))
        .order_by(Game.sort_order, Game.id)
    )
    games = list(db.scalars(statement).unique())
    for game in games:
        game.services = sorted((service for service in game.services if service.is_active), key=lambda service: (service.sort_order, service.id))
    return games


@app.get("/api/settings", response_model=SiteSettingPublic)
def get_public_settings(db: Session = Depends(get_db)) -> SiteSetting:
    return db.scalar(select(SiteSetting).where(SiteSetting.id == 1))


@app.post("/api/auth/login", response_model=AdminPublic)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AdminUser:
    user = db.scalar(select(AdminUser).where(AdminUser.username == payload.username))
    if not user or not user.is_active or not password_hash.verify(payload.password, user.password_hash):
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    response.set_cookie(COOKIE_NAME, create_token(user), httponly=True, secure=os.getenv("COOKIE_SECURE", "false").lower() == "true", samesite=os.getenv("COOKIE_SAMESITE", "lax"), max_age=7 * 24 * 60 * 60)
    return user


@app.post("/api/auth/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME)


@app.get("/api/auth/me", response_model=AdminPublic)
def me(request: Request, db: Session = Depends(get_db)) -> AdminUser:
    return get_current_admin(request, db)


@app.get("/api/admin/dashboard", response_model=DashboardPublic)
def dashboard(request: Request, db: Session = Depends(get_db)) -> DashboardPublic:
    get_current_admin(request, db)
    games = list(db.scalars(select(Game)))
    services = list(db.scalars(select(GameService)))
    latest = max((item.updated_at for item in [*games, *services]), default=None)
    return DashboardPublic(game_count=len(games), active_game_count=sum(game.is_active for game in games), service_count=len(services), active_service_count=sum(service.is_active for service in services), latest_updated_at=latest.isoformat() if latest else None)
