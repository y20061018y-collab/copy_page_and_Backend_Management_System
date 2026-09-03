from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Game, GameService
from app.schemas import GamePublic, ServiceItemPublic, ServicePublic


class PublicGameCatalog:
    def __init__(self, db: Session):
        self.db = db

    def list_games(self) -> list[GamePublic]:
        games = self.db.scalars(
            select(Game)
            .where(Game.is_active.is_(True))
            .options(selectinload(Game.services).selectinload(GameService.items))
            .order_by(Game.sort_order, Game.id)
        ).unique()
        return [self._game_snapshot(game) for game in games]

    @staticmethod
    def _game_snapshot(game: Game) -> GamePublic:
        return GamePublic(
            id=game.id,
            name=game.name,
            slug=game.slug,
            tag=game.tag,
            description=game.description,
            cover_image=game.cover_image,
            accent_color=game.accent_color,
            accent_color_2=game.accent_color_2,
            sort_order=game.sort_order,
            is_active=game.is_active,
            services=[
                ServicePublic(
                    id=service.id,
                    name=service.name,
                    description=service.description,
                    cover_image=service.cover_image,
                    sort_order=service.sort_order,
                    is_active=service.is_active,
                    items=[
                        ServiceItemPublic(
                            id=item.id,
                            name=item.name,
                            price=item.price,
                            description=item.description,
                            sort_order=item.sort_order,
                            is_active=item.is_active,
                        )
                        for item in sorted(
                            (item for item in service.items if item.is_active),
                            key=lambda item: (item.sort_order, item.id),
                        )
                    ],
                )
                for service in sorted(
                    (service for service in game.services if service.is_active),
                    key=lambda service: (service.sort_order, service.id),
                )
            ],
        )
