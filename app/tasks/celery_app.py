from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=[
        "app.tasks.tasks",
        "app.tasks.scheduled",
    ]
)


celery_app.conf.beat_schedule = {
    "some_periodic_task": {
        "task": "periodic_task",
        "schedule": 5,  # seconds
        # "schedule": crontab(minute="30", hour="15")
    }
}
