import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import accounts, agent, agent_analyses, credit_cards, dashboard, health, import_routes, insights, transactions
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

settings = get_settings()

app = FastAPI(
    title="Finance Control API",
    description="Local-first personal finance API with read-only agent tooling.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(accounts.router)
app.include_router(credit_cards.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)
app.include_router(import_routes.router)
app.include_router(insights.router)
app.include_router(agent_analyses.router)
app.include_router(agent.router)


@app.get("/agent_tools_manifest.json", include_in_schema=False)
def agent_tools_manifest():
    return FileResponse(Path(__file__).with_name("agent_tools_manifest.json"))


@app.get("/openapi_agent_tools.yaml", include_in_schema=False)
def openapi_agent_tools():
    return FileResponse(Path(__file__).with_name("openapi_agent_tools.yaml"))
