from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import CHAR

from app.database import Base
from app.utils.security import generate_uuid


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=generate_uuid)
    family_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("families.id"), nullable=False, comment="所属家庭")
    setting_key: Mapped[str] = mapped_column(String(100), nullable=False, comment="配置键")
    setting_value: Mapped[str | None] = mapped_column(Text, nullable=True, comment="配置值")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("family_id", "setting_key", name="uq_setting_family_key"),
    )
