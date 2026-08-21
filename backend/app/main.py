from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import Base, engine, get_db, initialize_database
from app.models import Game, SiteSetting
from app.schemas import GamePublic, SiteSettingPublic

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
