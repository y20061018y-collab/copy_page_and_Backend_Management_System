from pydantic import BaseModel, ConfigDict


class ServicePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price: str
    description: str
    sort_order: int
    is_active: bool


class GamePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    tag: str
    description: str
    cover_image: str
    accent_color: str
    accent_color_2: str
    sort_order: int
    is_active: bool
    services: list[ServicePublic]
