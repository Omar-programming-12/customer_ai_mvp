import logging

from fastapi import FastAPI

from app.config import LOG_LEVEL
from app import storage
from app.routes import home, webhook


logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

storage.init_db()

app = FastAPI()

app.include_router(home.router)
app.include_router(webhook.router)
