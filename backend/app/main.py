import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response, UploadFile, File, status
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db, initialize_database
from app.game_catalog import DuplicateGameSlug, EnabledServiceItemLimitReached, EnabledServiceLimitReached, GameCatalog, GameCatalogError, GameNotFound, InvalidCatalogAction, ServiceItemNotFound, ServiceNotFound
from app.models import AdminUser, Game, GameService, ServiceItem, SiteSetting
from app.public_game_catalog import PublicGameCatalog
from app.schemas import AdminPublic, DashboardPublic, GamePublic, GameWrite, LoginRequest, ReorderItem, ServiceItemPublic, ServiceItemWrite, ServicePublic, ServiceWrite, SiteSettingPublic, SiteSettingWrite
from app.security import COOKIE_NAME, create_token, get_current_admin, password_hash
from app.errors import api_error, http_error_handler, validation_error_handler

app = FastAPI(title="11号电竞 API")
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
Path("uploads/games").mkdir(parents=True, exist_ok=True)
Path("uploads/studio").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/api/games", response_model=list[GamePublic])
def list_public_games(db: Session = Depends(get_db)) -> list[GamePublic]:
    return PublicGameCatalog(db).list_games()


@app.get("/api/settings", response_model=SiteSettingPublic)
def get_public_settings(db: Session = Depends(get_db)) -> SiteSetting:
    return db.scalar(select(SiteSetting).where(SiteSetting.id == 1))


@app.patch("/api/admin/settings", response_model=SiteSettingPublic)
def update_settings(payload: SiteSettingWrite, request: Request, db: Session = Depends(get_db)) -> SiteSetting:
    require_admin(request, db)
    setting = db.get(SiteSetting, 1)
    for key, value in payload.model_dump().items():
        setattr(setting, key, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(setting)
    return setting


@app.post("/api/auth/login", response_model=AdminPublic)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AdminUser:
    user = db.scalar(select(AdminUser).where(AdminUser.username == payload.username))
    if not user or not user.is_active or not password_hash.verify(payload.password, user.password_hash):
        from fastapi import HTTPException

        return api_error("AUTH_INVALID_CREDENTIALS", "账号或密码错误", status.HTTP_401_UNAUTHORIZED)
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
    return DashboardPublic(**GameCatalog(db).dashboard_counts().__dict__)


def require_admin(request: Request, db: Session) -> AdminUser:
    return get_current_admin(request, db)


def catalog_http_error(error: GameCatalogError) -> HTTPException:
    if isinstance(error, EnabledServiceLimitReached):
        return HTTPException(
            status_code=409,
            detail={"code": "SERVICE_LIMIT_REACHED", "message": "每个游戏最多 5 个启用需求"},
        )
    if isinstance(error, EnabledServiceItemLimitReached):
        return HTTPException(
            status_code=409,
            detail={"code": "SERVICE_ITEM_LIMIT_REACHED", "message": "每个服务最多 5 个启用子项目"},
        )
    if isinstance(error, DuplicateGameSlug):
        return HTTPException(status_code=409, detail="slug 已存在")
    if isinstance(error, GameNotFound):
        return HTTPException(status_code=404, detail="游戏不存在")
    if isinstance(error, ServiceNotFound):
        return HTTPException(status_code=404, detail="服务不存在")
    if isinstance(error, ServiceItemNotFound):
        return HTTPException(status_code=404, detail="服务子项目不存在")
    if isinstance(error, InvalidCatalogAction):
        return HTTPException(status_code=422, detail="不支持的操作")
    return HTTPException(status_code=400, detail="目录操作失败")


@app.get("/api/admin/games", response_model=list[GamePublic])
def admin_games(request: Request, db: Session = Depends(get_db)) -> list[Game]:
    require_admin(request, db)
    return GameCatalog(db).list_admin_games()


@app.post("/api/admin/games", response_model=GamePublic, status_code=201)
def create_game(payload: GameWrite, request: Request, db: Session = Depends(get_db)) -> Game:
    require_admin(request, db)
    try:
        return GameCatalog(db).create_game(payload)
    except GameCatalogError as exc:
        raise catalog_http_error(exc) from exc


@app.patch("/api/admin/games/reorder")
def reorder_games(items: list[ReorderItem], request: Request, db: Session = Depends(get_db)) -> dict[str, bool]:
    require_admin(request, db)
    try:
        return GameCatalog(db).reorder_games(items)
    except GameCatalogError as exc:
        raise catalog_http_error(exc) from exc


@app.patch("/api/admin/games/{game_id}", response_model=GamePublic)
def update_game(game_id: int, payload: GameWrite, request: Request, db: Session = Depends(get_db)) -> Game:
    require_admin(request, db)
    try:
        return GameCatalog(db).update_game(game_id, payload)
    except GameCatalogError as exc:
        raise catalog_http_error(exc) from exc


@app.post("/api/admin/games/{game_id}/state/{action}", response_model=GamePublic)
def set_game_state(game_id: int, action: str, request: Request, db: Session = Depends(get_db)) -> Game:
    require_admin(request, db)
    if action not in {"enable", "disable"}:
        raise catalog_http_error(InvalidCatalogAction())
    try:
        return GameCatalog(db).set_game_enabled(game_id, action == "enable")
    except GameCatalogError as exc:
        raise catalog_http_error(exc) from exc


@app.post("/api/admin/games/{game_id}/services", response_model=ServicePublic, status_code=201)
def create_service(game_id: int, payload: ServiceWrite, request: Request, db: Session = Depends(get_db)) -> GameService:
    require_admin(request, db)
    try:
        return GameCatalog(db).create_service(game_id, payload)
    except GameCatalogError as exc:
        raise catalog_http_error(exc) from exc


@app.patch("/api/admin/services/{service_id}", response_model=ServicePublic)
def update_service(service_id: int, payload: ServiceWrite, request: Request, db: Session = Depends(get_db)) -> GameService:
    require_admin(request, db)
    try:
        return GameCatalog(db).update_service(service_id, payload)
    except GameCatalogError as exc:
        raise catalog_http_error(exc) from exc


@app.post("/api/admin/services/{service_id}/items", response_model=ServiceItemPublic, status_code=201)
def create_service_item(service_id: int, payload: ServiceItemWrite, request: Request, db: Session = Depends(get_db)) -> ServiceItem:
    require_admin(request, db)
    try:
        return GameCatalog(db).create_service_item(service_id, payload)
    except GameCatalogError as exc:
        raise catalog_http_error(exc) from exc


@app.post("/api/admin/services/{service_id}/{action}", response_model=ServicePublic)
def set_service_state(service_id: int, action: str, request: Request, db: Session = Depends(get_db)) -> GameService:
    require_admin(request, db)
    if action not in {"enable", "disable"}:
        raise catalog_http_error(InvalidCatalogAction())
    try:
        return GameCatalog(db).set_service_enabled(service_id, action == "enable")
    except GameCatalogError as exc:
        raise catalog_http_error(exc) from exc


@app.patch("/api/admin/games/{game_id}/services/reorder")
def reorder_services(game_id: int, items: list[ReorderItem], request: Request, db: Session = Depends(get_db)) -> dict[str, bool]:
    require_admin(request, db)
    try:
        return GameCatalog(db).reorder_services(game_id, items)
    except GameCatalogError as exc:
        raise catalog_http_error(exc) from exc


@app.patch("/api/admin/service-items/{item_id}", response_model=ServiceItemPublic)
def update_service_item(item_id: int, payload: ServiceItemWrite, request: Request, db: Session = Depends(get_db)) -> ServiceItem:
    require_admin(request, db)
    try:
        return GameCatalog(db).update_service_item(item_id, payload)
    except GameCatalogError as exc:
        raise catalog_http_error(exc) from exc


@app.post("/api/admin/service-items/{item_id}/{action}", response_model=ServiceItemPublic)
def set_service_item_state(item_id: int, action: str, request: Request, db: Session = Depends(get_db)) -> ServiceItem:
    require_admin(request, db)
    if action not in {"enable", "disable"}:
        raise catalog_http_error(InvalidCatalogAction())
    try:
        return GameCatalog(db).set_service_item_enabled(item_id, action == "enable")
    except GameCatalogError as exc:
        raise catalog_http_error(exc) from exc


@app.patch("/api/admin/services/{service_id}/items/reorder")
def reorder_service_items(service_id: int, items: list[ReorderItem], request: Request, db: Session = Depends(get_db)) -> dict[str, bool]:
    require_admin(request, db)
    try:
        return GameCatalog(db).reorder_service_items(service_id, items)
    except GameCatalogError as exc:
        raise catalog_http_error(exc) from exc


@app.post("/api/admin/uploads/game-cover")
def upload_game_cover(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, str]:
    require_admin(request, db)
    extension = Path(file.filename or "").suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=422, detail={"code": "UPLOAD_INVALID_TYPE", "message": "不支持的图片类型"})
    data = file.file.read(5 * 1024 * 1024 + 1)
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail={"code": "UPLOAD_TOO_LARGE", "message": "图片不能超过 5MB"})
    detected_extension = ".jpg" if data.startswith(b"\xff\xd8\xff") else ".png" if data.startswith(b"\x89PNG\r\n\x1a\n") else ".webp" if data.startswith(b"RIFF") and data[8:12] == b"WEBP" else None
    if detected_extension is None:
        raise HTTPException(status_code=422, detail={"code": "UPLOAD_INVALID_CONTENT", "message": "图片内容无效"})
    import secrets

    directory = Path("uploads/games")
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{secrets.token_urlsafe(16)}{detected_extension}"
    target.write_bytes(data)
    return {"path": f"/uploads/games/{target.name}"}


@app.post("/api/admin/uploads/studio-image")
def upload_studio_image(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, str]:
    require_admin(request, db)
    allowed = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    extension = Path(file.filename or "").suffix.lower()
    if file.content_type not in allowed or extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=422, detail={"code": "UPLOAD_INVALID_TYPE", "message": "不支持的图片类型"})
    data = file.file.read(5 * 1024 * 1024 + 1)
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail={"code": "UPLOAD_TOO_LARGE", "message": "图片不能超过 5MB"})
    if not data.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n")) and not (data.startswith(b"RIFF") and data[8:12] == b"WEBP"):
        raise HTTPException(status_code=422, detail={"code": "UPLOAD_INVALID_CONTENT", "message": "图片内容无效"})
    import secrets

    directory = Path("uploads/studio")
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{secrets.token_urlsafe(16)}{allowed[file.content_type]}"
    target.write_bytes(data)
    return {"path": f"/uploads/studio/{target.name}"}
