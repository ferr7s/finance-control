from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    postgres_db: str = "finance_control"
    postgres_user: str = "finance_control"
    postgres_password: str = "finance_control"
    database_url: str = "postgresql+psycopg://finance_control:finance_control@localhost:5432/finance_control"

    environment: str = "development"
    backend_cors_origins: str = "http://localhost:3000"

    agent_api_key: str = Field(default="dev-local-key", alias="AGENT_API_KEY")
    finance_control_api_url: str = "http://localhost:8000"

    pluggy_client_id: str = ""
    pluggy_client_secret: str = ""
    pluggy_base_url: str = "https://api.pluggy.ai"

    sync_server_url: str = "http://host.docker.internal:8001"

    gmail_address: str = ""
    gmail_app_password: str = ""
    email_sync_hour: int = 7

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
