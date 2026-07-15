from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import CHAR

from app.database import Base
from app.utils.security import generate_uuid


class OCRRecognitionLog(Base):
    __tablename__ = "ocr_recognition_logs"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=generate_uuid)
    family_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("families.id"), nullable=False, comment="所属家庭")
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False, comment="上传人")
    image_url: Mapped[str] = mapped_column(String(500), nullable=False, comment="图片OSS地址")
    ocr_result: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="OCR识别结果JSON")
    matched_product_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("products.id"), nullable=True, comment="匹配到的商品")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
