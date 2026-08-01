import os

# Set secret before loading from env
# It should be at least 32 chars long to avoid warnings of being too weak
# (although it doesn't matter weakness in the test environment)
os.environ["JWT_SECRET"] = "randomsecret12345678901234567890"

from collections.abc import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.external.database.database import Database
from app.external.database.database_models import Base as DatabaseBaseModel
from app.external.fastapi_app.main import app, env_settings
from app.external.fastapi_app.context import init_context, db_session as set_db_session


# This is a standard way to register pytest plugins.
# It is also possible to do it through the pyproject.toml file
# or commandline flag.
# But this way is the most common way, it keeps the configuration right
# next to the code that uses it.
# Anyio is used to write async test functions. It supports asyncio and trio.
pytest_plugins = ["anyio"]


# Scope="session" means that is run only once in the entire session
# rather that once for every test
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def test_engine():
    db = Database(
        {
            # "url": os.environ["DATABASE_URL"],
            "url": env_settings.DB_CONNECTION_STRING,
            "poolclass": NullPool,
        }
    )
    init_context(db)
    return db.engine


@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(DatabaseBaseModel.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(DatabaseBaseModel.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def db_session(
    test_engine,
    setup_database,
) -> AsyncGenerator[AsyncSession]:
    conn = await test_engine.connect()
    trans = await conn.begin()

    test_async_session = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
            await conn.close()


@pytest.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient]:

    # async def override_get_db():
    #     yield db_session
    # app.dependency_overrides[get_db] = override_get_db
    token = set_db_session.set(db_session)

    async with AsyncClient(
        # ASGI (Asyncronous Server Gateway Interface)
        # Internal communication instead of network based
        transport=ASGITransport(app=app),
        # It doesn't really matter since we aren't using the network at all
        # it just needs a value
        base_url="http://test",
    ) as ac:
        # With this way, lifespan function isn't triggered, so if needed
        # ASGI lifespan package that's lifespan manager
        yield ac

    # app.dependency_overrides.clear()
    set_db_session.reset(token)


# Tests tienen que ser
# - INDEPENDIENTES entre SI
# - INDEPENDIENTES del Contexto
# - AUTOCONTENIDOS
# - IDEMPOTENTES
