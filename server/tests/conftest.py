import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import Base, get_session
from app.main import app


# --- Добавляем заглушку для ARQ ---
class MockARQ:
    async def enqueue_job(self, *args, **kwargs):
        return None  # Просто игнорируем постановку в очередь
# ----------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def override_get_session():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    # Подменяем ARQ на заглушку
    app.state.arq = MockARQ()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac