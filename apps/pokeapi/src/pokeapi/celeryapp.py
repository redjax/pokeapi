import sys

sys.path.append(".")
from pokeapi.core.conf import celery_settings

from celery import Celery

app = Celery(
    "pokeapi",
    broker=f"pyamqp://{celery_settings.rabbitmq_user}:{celery_settings.rabbitmq_password}@{celery_settings.rabbitmq_host}//",
    backend=f"redis://{celery_settings.redis_host}:{celery_settings.redis_port}",
    include=["pokeapi.celery_tasks"],
)

app.conf.update(result_expires=3600, result_max=100000)

if __name__ == "__main__":
    app.start()
