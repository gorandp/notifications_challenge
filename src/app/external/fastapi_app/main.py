from fastapi import FastAPI

from app.core.logger import LogWrapper
from .routers import auth, users, notifications, channels


app = FastAPI()

app.include_router(
    auth.router,
    tags=["auth"],
)
app.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)
app.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["notifications"],
)
# app.include_router(
#     channels.router,
#     prefix="/channels",
#     tags=["channels"],
# )

logger = LogWrapper("main").logger


@app.get("/")
async def home():
    return {"msg": "Hello World!"}
