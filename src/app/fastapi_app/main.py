import os
from typing import Annotated
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

# # from database_models import Base as DbBase
# from .. import database_models as models
from ..logger import LogWrapper
# from .schemas import NewsResponse, NewsShortResponse, NewsSearchResponse
from .database import get_db


app = FastAPI()

logger = LogWrapper("main").logger


@app.get("/")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    return {"msg": "Hello World!"}
