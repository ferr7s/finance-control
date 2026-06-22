"""
Sync server — runs on the host machine (outside Docker) at port 8001.
The backend calls http://host.docker.internal:8001/sync to trigger scrapers.
"""
import asyncio
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Finance Control Sync Server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory status store
_status: dict[str, dict] = {
    "flash": {"status": "idle", "synced": 0, "error": None, "synced_at": None},
    "itau": {"status": "idle", "synced": 0, "error": None, "synced_at": None},
    "nubank": {"status": "idle", "synced": 0, "error": None, "synced_at": None},
}
_lock = asyncio.Lock()

KNOWN_BANKS = ("flash", "itau", "nubank")


async def _run_scraper(bank: str) -> None:
    async with _lock:
        _status[bank]["status"] = "running"
        _status[bank]["error"] = None

    try:
        if bank == "flash":
            from flash_scraper import scrape
        elif bank == "itau":
            from itau_scraper import scrape
        elif bank == "nubank":
            from nubank_scraper import scrape
        else:
            raise ValueError(f"Unknown bank: {bank}")

        result = await scrape()

        async with _lock:
            _status[bank]["status"] = "done" if not result["errors"] else "failed"
            _status[bank]["synced"] = result["synced"]
            _status[bank]["error"] = "; ".join(result["errors"]) if result["errors"] else None
            _status[bank]["synced_at"] = datetime.now(timezone.utc).isoformat()

    except Exception as e:
        async with _lock:
            _status[bank]["status"] = "failed"
            _status[bank]["error"] = str(e)
            _status[bank]["synced_at"] = datetime.now(timezone.utc).isoformat()


@app.post("/sync")
async def sync_all():
    for bank in KNOWN_BANKS:
        asyncio.create_task(_run_scraper(bank))
    return {"message": "Sync started for all banks"}


@app.post("/sync/{bank}")
async def sync_bank(bank: str):
    if bank not in KNOWN_BANKS:
        return {"error": f"Unknown bank: {bank}. Valid: {', '.join(KNOWN_BANKS)}"}, 400
    asyncio.create_task(_run_scraper(bank))
    return {"message": f"Sync started for {bank}"}


@app.get("/status")
async def get_status():
    return _status


@app.get("/health")
async def health():
    return {"status": "ok"}
