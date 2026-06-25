import logging
from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import accounts, agent, agent_analyses, credit_cards, dashboard, health, import_routes, insights, sync, transactions
from app.api.routes import email_sync
from app.core.config import get_settings
from app.core.database import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

settings = get_settings()


def _run_daily_email_sync() -> None:
    from app.services.email_service import run_email_sync
    db = SessionLocal()
    try:
        result = run_email_sync(db)
        logging.getLogger(__name__).info("Scheduled email sync: %s", result)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    if settings.gmail_address and settings.gmail_app_password:
        scheduler.add_job(
            _run_daily_email_sync,
            "cron",
            hour=settings.email_sync_hour,
            minute=0,
            id="daily_email_sync",
        )
        scheduler.start()
        logging.getLogger(__name__).info(
            "Email sync scheduled daily at %02d:00", settings.email_sync_hour
        )
    else:
        logging.getLogger(__name__).info(
            "Email sync not scheduled — GMAIL_ADDRESS/GMAIL_APP_PASSWORD not set"
        )
    yield
    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(
    title="Finance Control API",
    description="Local-first personal finance API with read-only agent tooling.",
    version="0.1.0",
    lifespan=lifespan,
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
app.include_router(import_routes.router)
app.include_router(email_sync.router)
app.include_router(dashboard.router)
app.include_router(insights.router)
app.include_router(sync.router)
app.include_router(agent_analyses.router)
app.include_router(agent.router)


@app.get("/agent_tools_manifest.json", include_in_schema=False)
def agent_tools_manifest():
    return FileResponse(Path(__file__).with_name("agent_tools_manifest.json"))


@app.get("/openapi_agent_tools.yaml", include_in_schema=False)
def openapi_agent_tools():
    return FileResponse(Path(__file__).with_name("openapi_agent_tools.yaml"))
