import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.fastapi_app.main import app
from src.app.fastapi_app.database import db_session
from src.app.database_models import Base as DatabaseBaseModel


@pytest.fixture
def client():
    try:
        old_session = db_session.get()
        old_session.close()
        db_session.reset()
    except Exception:
        pass
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False},
    )
    DatabaseBaseModel.metadata.drop_all(bind=engine)  # Delete tables if exist
    DatabaseBaseModel.metadata.create_all(bind=engine)  # Create tables if not exist
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    db_session.set(session)
    return TestClient(app)


# Tests tienen que ser
# - INDEPENDIENTES entre SI
# - INDEPENDIENTES del Contexto
# - AUTOCONTENIDOS
# - IDEMPOTENTES
