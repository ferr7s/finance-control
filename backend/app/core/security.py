import logging

from fastapi import Depends, Header, HTTPException, status

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


async def require_agent_api_key(
    authorization: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> bool:
    if not settings.agent_api_key and settings.environment == "development":
        logger.warning("AGENT_API_KEY is empty; allowing local development agent access.")
        return True

    expected = f"Bearer {settings.agent_api_key}"
    if not authorization or authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing agent API key",
        )
    return True
