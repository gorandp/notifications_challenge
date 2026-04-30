from fastapi import FastAPI

from app.core.logger import LogWrapper
from .routers import auth, users, notifications, channels, settings


app = FastAPI()

app.include_router(
    auth.router,
    tags=["Auth"],
)
app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)
app.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"],
)
app.include_router(
    channels.router,
    prefix="/channels",
    tags=["Channels"],
)
app.include_router(
    settings.router,
    prefix="/settings",
    tags=["Settings"],
)

logger = LogWrapper("main").logger


@app.get("/hello", tags=["Initial Test"])
async def home():
    return {"msg": "Hello World!"}
