from app.core.config import Settings, get_settings


class PluggyNotConfiguredError(RuntimeError):
    pass


class PluggyService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def _ensure_configured(self) -> None:
        if not self.settings.pluggy_client_id or not self.settings.pluggy_client_secret:
            raise PluggyNotConfiguredError("Pluggy não configurado")

    async def get_access_token(self) -> str:
        self._ensure_configured()
        return "stub-access-token"

    async def list_items(self) -> list[dict]:
        self._ensure_configured()
        return []

    async def list_accounts(self, item_id: str) -> list[dict]:
        self._ensure_configured()
        return []

    async def list_credit_cards(self, item_id: str) -> list[dict]:
        self._ensure_configured()
        return []

    async def list_credit_card_bills(self, credit_card_id: str) -> list[dict]:
        self._ensure_configured()
        return []

    async def list_transactions(self, account_id: str, from_date: str, to_date: str) -> list[dict]:
        self._ensure_configured()
        return []

    async def sync_all(self) -> dict:
        self._ensure_configured()
        return {"synced": False, "items": 0}
