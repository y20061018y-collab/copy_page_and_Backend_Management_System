from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SiteSetting(Base):
    __tablename__ = "site_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_name: Mapped[str] = mapped_column(String(120), nullable=False)
    site_subtitle: Mapped[str] = mapped_column(String(255), nullable=False)
    studio_image: Mapped[str | None] = mapped_column(String(255))
    contact_wechat: Mapped[str | None] = mapped_column(String(120))
    contact_qq: Mapped[str | None] = mapped_column(String(120))
    contact_phone: Mapped[str | None] = mapped_column(String(80))
    contact_description: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), server_default=func.now(), nullable=False)
