import sys

sys.path.append(".")
from core.conf import celery_settings

from celery import Celery

BROKER = celery_settings.broker_url
BACKEND = celery_settings.backend_url

app = Celery(
    "pokeapi",
    broker=BROKER,
    backend=BACKEND,
    include=["pokeapi.celery_tasks"],
)

app.conf.update(result_expires=3600, result_max=100000)

if __name__ == "__main__":
    app.start()
