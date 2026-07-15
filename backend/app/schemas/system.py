from datetime import datetime
from pydantic import BaseModel, Field


class SystemSettingCreate(BaseModel):
    setting_key: str = Field(..., max_length=100, description="配置键")
    setting_value: str | None = None


class SystemSettingUpdate(BaseModel):
    setting_value: str | None = None


class SystemSettingResponse(BaseModel):
    id: str
    family_id: str
    setting_key: str
    setting_value: str | None = None
    updated_at: datetime
    model_config = {"from_attributes": True}


class OCRResultResponse(BaseModel):
    brand: str | None = None
    name: str | None = None
    specification: str | None = None
    matched_product_id: str | None = None
    matched_product_name: str | None = None
    matched_product_brand: str | None = None
    image_url: str
    raw_result: dict | None = None
    model_config = {"from_attributes": True}


class OCRLogResponse(BaseModel):
    id: str
    family_id: str
    user_id: str
    image_url: str
    ocr_result: dict | None = None
    matched_product_id: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}
