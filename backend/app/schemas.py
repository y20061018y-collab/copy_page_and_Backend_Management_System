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


class SiteSettingPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    site_name: str
    site_subtitle: str
    studio_image: str | None
    contact_wechat: str | None
    contact_qq: str | None
    contact_phone: str | None
    contact_description: str | None
