 import io
 import logging
 from abc import ABC, abstractmethod
 
 from app.config import settings
 
 logger = logging.getLogger(__name__)
 
 
 class OSSService(ABC):
     """Abstract base class for OSS file storage."""
 
     @abstractmethod
     async def upload_file(self, file_data: bytes, file_name: str, content_type: str = "application/octet-stream") -> str:
         pass
 
     @abstractmethod
     async def delete_file(self, file_url: str) -> bool:
         pass
 
     @abstractmethod
     async def get_file_url(self, file_name: str) -> str:
         pass
 
 
 class MockOSSService(OSSService):
     """Mock OSS service for local development. Stores files in memory/temp."""
 
     def __init__(self):
         self._files: dict[str, bytes] = {}
         self._base_url = "http://localhost:8080/files"
 
     async def upload_file(self, file_data: bytes, file_name: str, content_type: str = "application/octet-stream") -> str:
         self._files[file_name] = file_data
         url = f"{self._base_url}/{file_name}"
         logger.info(f"[MockOSS] Uploaded {file_name} -> {url}")
         return url
 
     async def delete_file(self, file_url: str) -> bool:
         file_name = file_url.split("/")[-1]
         if file_name in self._files:
             del self._files[file_name]
             return True
         return False
 
     async def get_file_url(self, file_name: str) -> str:
         return f"{self._base_url}/{file_name}"
 
 
 class AliyunOSSService(OSSService):
     """Real Alibaba Cloud OSS implementation."""
 
     def __init__(self):
         import oss2
         self._auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
         self._bucket = oss2.Bucket(self._auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
         logger.info("Aliyun OSS service initialized")
 
     async def upload_file(self, file_data: bytes, file_name: str, content_type: str = "application/octet-stream") -> str:
         import oss2
         self._bucket.put_object(file_name, file_data, headers={"Content-Type": content_type})
         url = f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{file_name}"
         logger.info(f"[AliyunOSS] Uploaded {file_name} -> {url}")
         return url
 
     async def delete_file(self, file_url: str) -> bool:
         import oss2
         file_name = file_url.split("/")[-1]
         try:
             self._bucket.delete_object(file_name)
             return True
         except oss2.exceptions.OssError as e:
             logger.error(f"Failed to delete OSS file {file_name}: {e}")
             return False
 
     async def get_file_url(self, file_name: str) -> str:
         return f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{file_name}"
 
 
 def get_oss_service() -> OSSService:
     if settings.OSS_ACCESS_KEY_ID and settings.OSS_ACCESS_KEY_SECRET:
         return AliyunOSSService()
     logger.warning("OSS credentials not configured, using MockOSSService")
     return MockOSSService()
 
 
 oss_service = get_oss_service()
