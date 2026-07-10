 import json
 import logging
 from abc import ABC, abstractmethod
 
 from app.config import settings
 
 logger = logging.getLogger(__name__)
 
 
 class OCRService(ABC):
     @abstractmethod
     async def recognize(self, image_url: str) -> dict:
         pass
 
 
 class MockOCRService(OCRService):
     async def recognize(self, image_url: str) -> dict:
         logger.info(f"[MockOCR] Recognizing image: {image_url}")
         return {
             "brand": "示例品牌",
             "name": "示例商品（OCR模拟结果）",
             "specification": "500ml",
             "raw": {"confidence": 0.95, "recognized_text": "示例品牌 示例商品 500ml"},
         }
 
 
 class AliyunOCRService(OCRService):
     def __init__(self):
         from aliyunsdkcore.client import AcsClient
         import re
         region = getattr(settings, 'OCR_REGION', 'cn-hangzhou')
         self._client = AcsClient(
             settings.OCR_ACCESS_KEY_ID,
             settings.OCR_ACCESS_KEY_SECRET,
             region,
         )
         logger.info("Aliyun OCR service initialized")
 
     async def recognize(self, image_url: str) -> dict:
         from aliyunsdkcore.request import CommonRequest
         request = CommonRequest()
         request.set_domain('ocr.cn-hangzhou.aliyuncs.com')
         request.set_version('2019-12-30')
         request.set_action_name('RecognizeAdvanced')
         request.set_method('POST')
         request.set_protocol_type('https')
         request.add_body_params('ImageURL', image_url)
         request.add_body_params('OutputCharInfo', False)
         request.add_body_params('NeedSort', True)
         try:
             response = self._client.do_action_with_exception(request)
             result = json.loads(response)
             text = ""
             if "Data" in result and "Content" in result["Data"]:
                 text = result["Data"]["Content"]
             lines = text.split("\n") if text else []
             parsed = self._parse_product_text(lines)
             parsed["raw"] = result
             return parsed
         except Exception as e:
             logger.error(f"Aliyun OCR failed: {e}")
             return {"brand": "", "name": "", "specification": "", "raw": {"error": str(e)}}
 
     def _parse_product_text(self, lines: list[str]) -> dict:
         brand = ""
         name = ""
         spec = ""
         for line in lines:
             line = line.strip()
             if not line:
                 continue
             if not brand and len(line) < 10:
                 brand = line
             elif not name and len(line) > 2:
                 name = line
             elif any(u in line.lower() for u in ["ml", "g", "l", "斤", "克", "毫升"]):
                 spec = line
         return {"brand": brand, "name": name, "specification": spec}
 
 
 def get_ocr_service() -> OCRService:
     if settings.OCR_ACCESS_KEY_ID and settings.OCR_ACCESS_KEY_SECRET:
         return AliyunOCRService()
     logger.warning("OCR credentials not configured, using MockOCRService")
     return MockOCRService()
 
 
 ocr_service = get_ocr_service()
