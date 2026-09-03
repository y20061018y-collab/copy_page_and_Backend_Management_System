from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models import Game, GameService, ServiceItem
from app.schemas import GameWrite, ReorderItem, ServiceItemWrite, ServiceWrite


class GameCatalogError(Exception):
    pass


class GameNotFound(GameCatalogError):
    pass


class ServiceNotFound(GameCatalogError):
    pass


class ServiceItemNotFound(GameCatalogError):
    pass


class DuplicateGameSlug(GameCatalogError):
    pass


class InvalidCatalogAction(GameCatalogError):
    pass


class EnabledServiceLimitReached(GameCatalogError):
    pass


class EnabledServiceItemLimitReached(GameCatalogError):
    pass


@dataclass(frozen=True)
class DashboardCounts:
    game_count: int
    active_game_count: int
    service_count: int
    active_service_count: int
    latest_updated_at: str | None


class GameCatalog:
    def __init__(self, db: Session):
        self.db = db

    def list_admin_games(self) -> list[Game]:
        games = list(
            self.db.scalars(
                select(Game)
                .options(selectinload(Game.services).selectinload(GameService.items))
                .order_by(Game.sort_order, Game.id)
            ).unique()
        )
        for game in games:
            game.services = self._sort_services(game.services)
            for service in game.services:
                service.items = self._sort_service_items(service.items)
        return games

    def create_game(self, payload: GameWrite) -> Game:
        if self.db.scalar(select(Game).where(Game.slug == payload.slug)):
            raise DuplicateGameSlug()
        game = Game(**payload.model_dump())
        self.db.add(game)
        self._commit()
        self.db.refresh(game)
        return game

    def update_game(self, game_id: int, payload: GameWrite) -> Game:
        game = self.db.get(Game, game_id)
        if not game:
            raise GameNotFound()
        duplicate = self.db.scalar(select(Game).where(Game.slug == payload.slug, Game.id != game_id))
        if duplicate:
            raise DuplicateGameSlug()
        for key, value in payload.model_dump().items():
            setattr(game, key, value)
        self._commit()
        self.db.refresh(game)
        return game

    def reorder_games(self, items: list[ReorderItem]) -> dict[str, bool]:
        games = {game.id: game for game in self.db.scalars(select(Game).where(Game.id.in_([item.id for item in items])))}
        if len(games) != len(items):
            raise GameNotFound()
        for item in items:
            games[item.id].sort_order = item.sort_order
        self._commit()
        return {"ok": True}

    def set_game_enabled(self, game_id: int, enabled: bool) -> Game:
        game = self.db.get(Game, game_id)
        if not game:
            raise GameNotFound()
        game.is_active = enabled
        self._commit()
        self.db.refresh(game)
        return game

    def create_service(self, game_id: int, payload: ServiceWrite) -> GameService:
        game = self._lock_game(game_id)
        if payload.is_active and self._enabled_service_count(game_id) >= 5:
            raise EnabledServiceLimitReached()
        values = payload.model_dump()
        values["cover_image"] = values["cover_image"] or game.cover_image
        service = GameService(**values)
        game.services.append(service)
        self._commit()
        self.db.refresh(service)
        return service

    def update_service(self, service_id: int, payload: ServiceWrite) -> GameService:
        service = self.db.get(GameService, service_id)
        if not service:
            raise ServiceNotFound()
        self._lock_game(service.game_id)
        if payload.is_active and not service.is_active and self._enabled_service_count(service.game_id) >= 5:
            raise EnabledServiceLimitReached()
        for key, value in payload.model_dump(exclude_none=True).items():
            setattr(service, key, value)
        self._commit()
        self.db.refresh(service)
        return service

    def set_service_enabled(self, service_id: int, enabled: bool) -> GameService:
        service = self.db.get(GameService, service_id)
        if not service:
            raise ServiceNotFound()
        self._lock_game(service.game_id)
        if enabled and not service.is_active and self._enabled_service_count(service.game_id) >= 5:
            raise EnabledServiceLimitReached()
        service.is_active = enabled
        self._commit()
        self.db.refresh(service)
        return service

    def reorder_services(self, game_id: int, items: list[ReorderItem]) -> dict[str, bool]:
        game = self.db.get(Game, game_id)
        if not game:
            raise GameNotFound()
        services = {
            service.id: service
            for service in self.db.scalars(
                select(GameService).where(GameService.game_id == game_id, GameService.id.in_([item.id for item in items]))
            )
        }
        if len(services) != len(items):
            raise ServiceNotFound()
        for item in items:
            services[item.id].sort_order = item.sort_order
        self._commit()
        return {"ok": True}

    def create_service_item(self, service_id: int, payload: ServiceItemWrite) -> ServiceItem:
        service = self._lock_service(service_id)
        if payload.is_active and self._enabled_service_item_count(service_id) >= 5:
            raise EnabledServiceItemLimitReached()
        item = ServiceItem(**payload.model_dump())
        service.items.append(item)
        self._commit()
        self.db.refresh(item)
        return item

    def update_service_item(self, item_id: int, payload: ServiceItemWrite) -> ServiceItem:
        item = self.db.get(ServiceItem, item_id)
        if not item:
            raise ServiceItemNotFound()
        self._lock_service(item.service_id)
        if payload.is_active and not item.is_active and self._enabled_service_item_count(item.service_id) >= 5:
            raise EnabledServiceItemLimitReached()
        for key, value in payload.model_dump().items():
            setattr(item, key, value)
        self._commit()
        self.db.refresh(item)
        return item

    def set_service_item_enabled(self, item_id: int, enabled: bool) -> ServiceItem:
        item = self.db.get(ServiceItem, item_id)
        if not item:
            raise ServiceItemNotFound()
        self._lock_service(item.service_id)
        if enabled and not item.is_active and self._enabled_service_item_count(item.service_id) >= 5:
            raise EnabledServiceItemLimitReached()
        item.is_active = enabled
        self._commit()
        self.db.refresh(item)
        return item

    def reorder_service_items(self, service_id: int, items: list[ReorderItem]) -> dict[str, bool]:
        self._lock_service(service_id)
        service_items = {
            item.id: item
            for item in self.db.scalars(
                select(ServiceItem).where(ServiceItem.service_id == service_id, ServiceItem.id.in_([item.id for item in items]))
            )
        }
        if len(service_items) != len(items):
            raise ServiceItemNotFound()
        for item in items:
            service_items[item.id].sort_order = item.sort_order
        self._commit()
        return {"ok": True}

    def dashboard_counts(self) -> DashboardCounts:
        games = list(self.db.scalars(select(Game)))
        services = list(self.db.scalars(select(GameService)))
        latest = self._latest_updated_at([*games, *services])
        return DashboardCounts(
            game_count=len(games),
            active_game_count=sum(game.is_active for game in games),
            service_count=len(services),
            active_service_count=sum(service.is_active for service in services),
            latest_updated_at=latest.isoformat() if latest else None,
        )

    def _commit(self) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateGameSlug() from exc

    def _enabled_service_count(self, game_id: int) -> int:
        return self.db.scalar(
            select(func.count()).select_from(GameService).where(
                GameService.game_id == game_id,
                GameService.is_active.is_(True),
            )
        ) or 0

    def _lock_game(self, game_id: int) -> Game:
        game = self.db.scalar(select(Game).where(Game.id == game_id).with_for_update())
        if not game:
            raise GameNotFound()
        return game

    def _lock_service(self, service_id: int) -> GameService:
        service = self.db.scalar(select(GameService).where(GameService.id == service_id).with_for_update())
        if not service:
            raise ServiceNotFound()
        return service

    def _enabled_service_item_count(self, service_id: int) -> int:
        return self.db.scalar(
            select(func.count()).select_from(ServiceItem).where(
                ServiceItem.service_id == service_id,
                ServiceItem.is_active.is_(True),
            )
        ) or 0

    @staticmethod
    def _sort_services(services) -> list[GameService]:
        return sorted(services, key=lambda service: (service.sort_order, service.id))

    @staticmethod
    def _sort_service_items(items) -> list[ServiceItem]:
        return sorted(items, key=lambda item: (item.sort_order, item.id))

    @staticmethod
    def _latest_updated_at(items) -> datetime | None:
        dates = [item.updated_at for item in items if item.updated_at is not None]
        if not dates:
            return None
        return max(dates, key=lambda value: value.replace(tzinfo=None))
