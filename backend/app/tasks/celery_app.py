import logging

from celery import Celery
from celery.schedules import crontab

from app.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "hpms",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_max_tasks_per_child=200,
)

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "scrape-prices-every-4-hours": {
        "task": "app.tasks.scheduled.scheduled_price_scrape",
        "schedule": crontab(hour=settings.PRICE_SCRAPE_HOURS, minute=0),
        "args": (),
    },
    "check-low-stock-daily": {
        "task": "app.tasks.scheduled.check_low_stock",
        "schedule": crontab(hour=8, minute=0),
        "args": (),
    },
    "check-expiring-coupons-daily": {
        "task": "app.tasks.scheduled.check_expiring_coupons",
        "schedule": crontab(hour=9, minute=0),
        "args": (),
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])

logger.info("Celery app initialized with beat schedule")
