from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_settings import SystemSetting
from app.models.ocr_log import OCRRecognitionLog


class SystemSettingCRUD:
   async def get(self, db: AsyncSession, family_id: str, key: str) -> str | None:
       result = await db.execute(
           select(SystemSetting).where(
               and_(SystemSetting.family_id == family_id, SystemSetting.setting_key == key)
           )
       )
       setting = result.scalar_one_or_none()
       return setting.setting_value if setting else None

   async def set(self, db: AsyncSession, family_id: str, key: str, value: str) -> SystemSetting:
       result = await db.execute(
           select(SystemSetting).where(
               and_(SystemSetting.family_id == family_id, SystemSetting.setting_key == key)
           )
       )
       setting = result.scalar_one_or_none()
       if setting:
           setting.setting_value = value
       else:
           setting = SystemSetting(family_id=family_id, setting_key=key, setting_value=value)
           db.add(setting)
       await db.flush()
       await db.refresh(setting)
       return setting

   async def get_all(self, db: AsyncSession, family_id: str) -> list[SystemSetting]:
       result = await db.execute(
           select(SystemSetting).where(SystemSetting.family_id == family_id)
       )
       return list(result.scalars().all())

   async def delete(self, db: AsyncSession, family_id: str, key: str) -> bool:
       result = await db.execute(
           select(SystemSetting).where(
               and_(SystemSetting.family_id == family_id, SystemSetting.setting_key == key)
           )
       )
       setting = result.scalar_one_or_none()
       if not setting:
           return False
       await db.delete(setting)
       await db.flush()
       return True


class OCRLogCRUD:
   async def create(self, db: AsyncSession, family_id: str, user_id: str, image_url: str,
                    ocr_result: dict | None = None, matched_product_id: str | None = None) -> OCRRecognitionLog:
       log = OCRRecognitionLog(
           family_id=family_id, user_id=user_id, image_url=image_url,
           ocr_result=ocr_result, matched_product_id=matched_product_id,
       )
       db.add(log)
       await db.flush()
       await db.refresh(log)
       return log

   async def get_family_logs(self, db: AsyncSession, family_id: str, limit: int = 20) -> list[OCRRecognitionLog]:
       result = await db.execute(
           select(OCRRecognitionLog).where(OCRRecognitionLog.family_id == family_id)
           .order_by(OCRRecognitionLog.created_at.desc()).limit(limit)
       )
       return list(result.scalars().all())


system_setting_crud = SystemSettingCRUD()
ocr_log_crud = OCRLogCRUD()
