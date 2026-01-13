import pytest
import httpx
import jwt
from datetime import datetime, timezone, timedelta

from src.schemas.config import settings


@pytest.mark.order(after="tests/test_api/test_token.py::test_token_with_unauthorized_username")
@pytest.mark.asyncio
async def test_refresh(async_client: httpx.AsyncClient):
    response = await async_client.post(
        "/api/refresh", 
        headers={
            "Cookie": f"refresh_token={async_client.cookies.get("refresh_token")}"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"


@pytest.mark.order(after="test_refresh")
@pytest.mark.asyncio
async def test_refresh_with_invalid_token(async_client: httpx.AsyncClient):
    response = await async_client.post(
        "/api/refresh", 
        headers={
            "Cookie": "refresh_token=invalid_token"
        }
    )

    assert response.status_code == 401


@pytest.mark.order(after="test_refresh_with_invalid_token")
@pytest.mark.asyncio
async def test_refresh_without_token(async_client: httpx.AsyncClient):
    response = await async_client.post("/api/refresh")

    assert response.status_code == 401


async def create_expired_refresh_token(data: dict, secret_key: str):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) - timedelta(days=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)


@pytest.mark.order(after="test_refresh_without_token")
@pytest.mark.asyncio
async def test_refresh_with_expired_token(async_client: httpx.AsyncClient):
    expired_token = await create_expired_refresh_token({"sub": "testname"}, settings.SECRET_KEY)

    response = await async_client.post(
        "/api/refresh",
        headers={
            "Cookie": f"refresh_token={expired_token}"
        }
    )

    assert response.status_code == 401