import json
from pathlib import Path

SESSIONS_DIR = Path(__file__).parent / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)


def save_session(bank: str, cookies: list[dict]) -> None:
    path = SESSIONS_DIR / f"{bank}.json"
    path.write_text(json.dumps(cookies, indent=2))


def load_session(bank: str) -> list[dict] | None:
    path = SESSIONS_DIR / f"{bank}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def clear_session(bank: str) -> None:
    path = SESSIONS_DIR / f"{bank}.json"
    if path.exists():
        path.unlink()
