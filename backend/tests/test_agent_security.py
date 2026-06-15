import pytest
from fastapi import HTTPException

from app.core.config import Settings
from app.core.security import require_agent_api_key


@pytest.mark.asyncio
async def test_agent_api_key_rejects_invalid_token():
    settings = Settings(environment="production", agent_api_key="secret")

    with pytest.raises(HTTPException) as exc:
        await require_agent_api_key(authorization="Bearer wrong", settings=settings)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_agent_api_key_allows_development_when_key_empty():
    settings = Settings(environment="development", agent_api_key="")

    assert await require_agent_api_key(authorization=None, settings=settings) is True
