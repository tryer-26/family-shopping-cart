import logging
import sys
from app.config import settings


def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    handlers = [logging.StreamHandler(sys.stdout)]
    if settings.LOG_FILE:
        handlers.append(logging.FileHandler(settings.LOG_FILE))
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("aiomysql").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING if not settings.DEBUG else logging.INFO)
