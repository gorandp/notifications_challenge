from fastapi import Request

from app.external.fastapi_app.main import app
from app.external.fastapi_app.context import db_session, database_ctx


@app.middleware("http")
async def set_db_session(request: Request, call_next):
    db = database_ctx.get()
    async with db.async_session_local() as session:
        token = db_session.set(session)
        response = await call_next(request)
        db_session.reset(token)
    return response
