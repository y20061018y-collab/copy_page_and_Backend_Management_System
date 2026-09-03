from pydantic import BaseModel, ConfigDict


class ServiceItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price: str
    description: str
    sort_order: int
    is_active: bool


class ServicePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price: str
    description: str
    cover_image: str
    sort_order: int
    is_active: bool
    items: list[ServiceItemPublic]


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


class LoginRequest(BaseModel):
    username: str
    password: str


class AdminPublic(BaseModel):
    id: int
    username: str


class DashboardPublic(BaseModel):
    game_count: int
    active_game_count: int
    service_count: int
    active_service_count: int
    latest_updated_at: str | None


class GameWrite(BaseModel):
    name: str
    slug: str
    tag: str = ""
    description: str = ""
    cover_image: str
    accent_color: str = "#7c3aed"
    accent_color_2: str = "#06b6d4"
    sort_order: int = 0
    is_active: bool = True


class ServiceWrite(BaseModel):
    name: str
    price: str
    description: str = ""
    cover_image: str | None = None
    sort_order: int = 0
    is_active: bool = True


class ServiceItemWrite(BaseModel):
    name: str
    price: str
    description: str = ""
    sort_order: int = 0
    is_active: bool = True


class SiteSettingWrite(BaseModel):
    site_name: str
    site_subtitle: str
    studio_image: str | None = None
    contact_wechat: str | None = None
    contact_qq: str | None = None
    contact_phone: str | None = None
    contact_description: str | None = None


class ReorderItem(BaseModel):
    id: int
    sort_order: int
