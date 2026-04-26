import pytest
from fastapi.testclient import TestClient

from app.external.fastapi_app.context import init_context, db_session
from app.external.database.database import Database
from app.external.database.database_models import Base as DatabaseBaseModel
from app.external.fastapi_app.main import app
from app.external.fastapi_app.config import JWTConfig


@pytest.fixture
def client():
    try:
        old_session = db_session.get()
        old_session.close()
    except Exception:
        pass
    db = Database({"url": "sqlite:///./test.db"})
    DatabaseBaseModel.metadata.drop_all(bind=db.engine)  # Delete tables if exist
    DatabaseBaseModel.metadata.create_all(bind=db.engine)  # Create tables if not exist
    init_context(db)
    db_session.set(db.session_local())
    JWTConfig.set_secret("secret123456789012345678901234567890")
    return TestClient(app)


# Tests tienen que ser
# - INDEPENDIENTES entre SI
# - INDEPENDIENTES del Contexto
# - AUTOCONTENIDOS
# - IDEMPOTENTES
