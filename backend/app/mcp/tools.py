import os
from typing import Any

import httpx


API_URL = os.getenv("FINANCE_CONTROL_API_URL", "http://localhost:8000").rstrip("/")
AGENT_API_KEY = os.getenv("AGENT_API_KEY", "dev-local-key")


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {AGENT_API_KEY}"}


async def agent_get(path: str) -> Any:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"{API_URL}{path}", headers=_headers())
        response.raise_for_status()
        return response.json()


async def agent_post(path: str, payload: dict | None = None) -> Any:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{API_URL}{path}", headers=_headers(), json=payload or {})
        response.raise_for_status()
        return response.json()


async def get_dashboard_summary() -> Any:
    return await agent_get("/api/agent/dashboard-summary")


async def search_transactions(
    query: str | None = None,
    category: str | None = None,
    provider: str | None = None,
    type: str | None = None,
    limit: int = 50,
) -> Any:
    return await agent_post(
        "/api/agent/transactions/search",
        {"query": query, "category": category, "provider": provider, "type": type, "limit": limit},
    )


async def get_category_breakdown() -> Any:
    return await agent_get("/api/agent/category-breakdown")


async def get_monthly_cashflow() -> Any:
    return await agent_get("/api/agent/monthly-cashflow")


async def get_recurring_expenses() -> Any:
    return await agent_get("/api/agent/recurring-expenses")


async def get_credit_card_summary() -> Any:
    return await agent_get("/api/agent/credit-card-summary")


async def get_net_worth() -> Any:
    return await agent_get("/api/agent/net-worth")


async def generate_financial_context() -> Any:
    return await agent_post("/api/agent/context/generate")


async def save_agent_analysis(source: str, title: str, content: str, metadata: dict | None = None) -> Any:
    return await agent_post(
        "/api/agent/analyses",
        {"source": source, "title": title, "content": content, "metadata": metadata},
    )
