from fastapi import FastAPI

from app.routes import home, webhook


app = FastAPI()

app.include_router(home.router)
app.include_router(webhook.router)
