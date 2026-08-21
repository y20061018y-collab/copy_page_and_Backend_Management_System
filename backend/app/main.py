import os

from fastapi import Depends, FastAPI, HTTPException, Request, Response, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import Base, engine, get_db, initialize_database
from app.models import AdminUser, Game, GameService, SiteSetting
from app.schemas import AdminPublic, DashboardPublic, GamePublic, GameWrite, LoginRequest, ServicePublic, ServiceWrite, SiteSettingPublic
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


def require_admin(request: Request, db: Session) -> AdminUser:
    return get_current_admin(request, db)


@app.get("/api/admin/games", response_model=list[GamePublic])
def admin_games(request: Request, db: Session = Depends(get_db)) -> list[Game]:
    require_admin(request, db)
    return list(db.scalars(select(Game).options(selectinload(Game.services)).order_by(Game.sort_order, Game.id)).unique())


@app.post("/api/admin/games", response_model=GamePublic, status_code=201)
def create_game(payload: GameWrite, request: Request, db: Session = Depends(get_db)) -> Game:
    require_admin(request, db)
    if db.scalar(select(Game).where(Game.slug == payload.slug)):
        raise HTTPException(status_code=409, detail="slug 已存在")
    game = Game(**payload.model_dump())
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


@app.patch("/api/admin/games/{game_id}", response_model=GamePublic)
def update_game(game_id: int, payload: GameWrite, request: Request, db: Session = Depends(get_db)) -> Game:
    require_admin(request, db)
    game = db.get(Game, game_id)
    if not game or not game.is_active:
        raise HTTPException(status_code=404, detail="游戏不存在")
    for key, value in payload.model_dump().items():
        setattr(game, key, value)
    db.commit()
    db.refresh(game)
    return game


@app.post("/api/admin/games/{game_id}/state/{action}", response_model=GamePublic)
def set_game_state(game_id: int, action: str, request: Request, db: Session = Depends(get_db)) -> Game:
    require_admin(request, db)
    game = db.get(Game, game_id)
    if not game or action not in {"enable", "disable"}:
        raise HTTPException(status_code=404, detail="游戏不存在")
    game.is_active = action == "enable"
    db.commit()
    db.refresh(game)
    return game


@app.post("/api/admin/games/{game_id}/services", response_model=ServicePublic, status_code=201)
def create_service(game_id: int, payload: ServiceWrite, request: Request, db: Session = Depends(get_db)) -> GameService:
    require_admin(request, db)
    game = db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    game.services.append(GameService(**payload.model_dump()))
    db.commit()
    db.refresh(game)
    db.refresh(game)
    return game.services[-1]


@app.patch("/api/admin/services/{service_id}", response_model=ServicePublic)
def update_service(service_id: int, payload: ServiceWrite, request: Request, db: Session = Depends(get_db)) -> GameService:
    require_admin(request, db)
    service = db.get(GameService, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")
    for key, value in payload.model_dump().items():
        setattr(service, key, value)
    db.commit()
    db.refresh(service)
    return service


@app.post("/api/admin/services/{service_id}/{action}", response_model=ServicePublic)
def set_service_state(service_id: int, action: str, request: Request, db: Session = Depends(get_db)) -> GameService:
    require_admin(request, db)
    service = db.get(GameService, service_id)
    if not service or action not in {"enable", "disable"}:
        raise HTTPException(status_code=404, detail="服务不存在")
    service.is_active = action == "enable"
    db.commit()
    db.refresh(service)
    return service


@app.post("/api/admin/uploads/game-cover")
def upload_game_cover(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, str]:
    require_admin(request, db)
    allowed = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=422, detail="不支持的图片类型")
    data = file.file.read(5 * 1024 * 1024 + 1)
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="图片不能超过 5MB")
    import secrets
    from pathlib import Path

    directory = Path("uploads/games")
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{secrets.token_urlsafe(16)}{allowed[file.content_type]}"
    target.write_bytes(data)
    return {"path": f"/uploads/games/{target.name}"}
