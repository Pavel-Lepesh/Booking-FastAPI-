from app.tasks.celery_app import celery_app


@celery_app.task(name="periodic_task")
def periodic_task():
    print(12345)
