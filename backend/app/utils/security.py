 import uuid
 from datetime import datetime, timedelta, timezone
 
 import jwt
 from passlib.context import CryptContext
 
 from app.config import settings
 
 pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
 
 def generate_uuid() -> str:
     return str(uuid.uuid4())
 
 
 def hash_password(password: str) -> str:
     return pwd_context.hash(password)
 
 
 def verify_password(plain_password: str, hashed_password: str) -> bool:
     return pwd_context.verify(plain_password, hashed_password)
 
 
 def create_access_token(user_id: str) -> str:
     expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
     payload = {
         "sub": user_id,
         "exp": expire,
         "iat": datetime.now(timezone.utc),
         "type": "access",
     }
     return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
 
 
 def decode_access_token(token: str) -> dict | None:
     try:
         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
         if payload.get("type") != "access":
             return None
         return payload
     except jwt.PyJWTError:
         return None
 
 
 def create_refresh_token(user_id: str) -> str:
     expire = datetime.now(timezone.utc) + timedelta(days=30)
     payload = {
         "sub": user_id,
         "exp": expire,
         "iat": datetime.now(timezone.utc),
         "type": "refresh",
     }
     return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
