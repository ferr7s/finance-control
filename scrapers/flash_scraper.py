"""
Flash Benefícios scraper using CloakBrowser.

First run (no saved session): opens a headed browser so the user can log in manually
and complete 2FA. Session is saved after successful login.

Subsequent runs: loads saved session and runs headless.

Strategy: network interception (captures XHR responses) as primary method;
DOM selector extraction as fallback.

Usage:
  python flash_scraper.py --login   # force headed login
  python flash_scraper.py           # use saved session (headless)
"""
import argparse
import asyncio
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

import httpx

from session_manager import load_session, save_session

FLASH_URL = "https://user.flashapp.com.br"
BACKEND_URL = "http://localhost:8000"
PROVIDER = "flash"

# XHR keywords that identify transaction API responses
_TX_URL_KEYWORDS = ("extrato", "transactions", "statement", "lancamento", "movimentacao")


def _parse_amount(raw: str) -> Decimal | None:
    cleaned = re.sub(r"[^\d,.-]", "", raw).replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _parse_date(raw: str) -> str | None:
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d/%m/%y"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue
    return None


async def _resolve_account_id() -> str | None:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BACKEND_URL}/api/accounts", timeout=5)
            for acc in resp.json():
                if acc.get("provider", "").lower() == PROVIDER:
                    return acc["id"]
        except Exception:
            pass
    return None


async def _post_transaction(payload: dict) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{BACKEND_URL}/api/transactions",
                json=payload,
                timeout=10,
            )
            return resp.status_code in (200, 201, 409)
        except Exception:
            return False


async def _intercept_and_extract(page, account_id: str | None) -> tuple[int, list[str]]:
    """Primary strategy: capture XHR responses containing transaction data."""
    captured_raw: list[dict] = []
    errors: list[str] = []

    async def on_response(response):
        url = response.url.lower()
        if any(kw in url for kw in _TX_URL_KEYWORDS):
            try:
                data = await response.json()
                items = (
                    data.get("items")
                    or data.get("data")
                    or data.get("transactions")
                    or data.get("lancamentos")
                    or []
                )
                if isinstance(items, list):
                    captured_raw.extend(items)
            except Exception:
                pass

    page.on("response", on_response)

    try:
        await page.wait_for_load_state("networkidle", timeout=15_000)
        # Navigate to extrato to trigger transaction API calls
        extrato_link = page.locator("a[href*='extrato'], a[href*='statement'], [data-testid*='extrato']")
        if await extrato_link.count() > 0:
            await extrato_link.first.click()
            await page.wait_for_load_state("networkidle", timeout=10_000)
        # Scroll to trigger lazy-loaded pagination
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
    except Exception as e:
        errors.append(f"Navegação falhou: {e}")

    if not captured_raw:
        return 0, errors

    synced = 0
    for i, tx in enumerate(captured_raw):
        try:
            raw_amount = str(tx.get("amount") or tx.get("valor") or tx.get("value") or "0")
            raw_date = str(tx.get("date") or tx.get("data") or tx.get("createdAt") or "")
            description = str(tx.get("description") or tx.get("descricao") or tx.get("title") or f"Flash tx {i}")
            tx_id = str(tx.get("id") or tx.get("uuid") or f"{date.today().isoformat()}-{i}")

            amount = _parse_amount(raw_amount) or Decimal("0")
            tx_date = _parse_date(raw_date) or datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            payload = {
                "external_id": f"flash-{tx_id}",
                "provider": PROVIDER,
                "account_id": account_id,
                "date": tx_date,
                "description": description,
                "amount": str(-abs(amount)),
                "type": "expense",
                "payment_method": "card",
            }
            ok = await _post_transaction(payload)
            if ok:
                synced += 1
        except Exception as e:
            errors.append(f"Tx {i}: {e}")

    return synced, errors


async def _dom_extract(page, account_id: str | None) -> tuple[int, list[str]]:
    """Fallback strategy: extract transactions from DOM elements."""
    errors: list[str] = []
    synced = 0

    rows = await page.query_selector_all(
        "[data-testid='transaction-item'], .transaction-row, tr.transaction"
    )
    if not rows:
        errors.append(
            "Seletores DOM não encontrados — inspecione o DOM do Flash e atualize _dom_extract() em flash_scraper.py"
        )
        return 0, errors

    for i, row in enumerate(rows):
        try:
            desc_el = await row.query_selector("[data-testid='description'], .description, td:nth-child(2)")
            date_el = await row.query_selector("[data-testid='date'], .date, td:nth-child(1)")
            amount_el = await row.query_selector("[data-testid='amount'], .amount, td:nth-child(3)")

            description = (await desc_el.inner_text()).strip() if desc_el else f"Flash tx {i}"
            raw_date = (await date_el.inner_text()).strip() if date_el else ""
            raw_amount = (await amount_el.inner_text()).strip() if amount_el else "0"

            tx_date = _parse_date(raw_date) or datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            amount = _parse_amount(raw_amount) or Decimal("0")

            payload = {
                "external_id": f"flash-{date.today().isoformat()}-{i}",
                "provider": PROVIDER,
                "account_id": account_id,
                "date": tx_date,
                "description": description,
                "amount": str(-abs(amount)),
                "type": "expense",
                "payment_method": "card",
            }
            ok = await _post_transaction(payload)
            if ok:
                synced += 1
        except Exception as e:
            errors.append(f"Linha {i}: {e}")

    return synced, errors


async def scrape(force_login: bool = False) -> dict:
    """Returns {"synced": int, "errors": list[str]}"""
    try:
        from cloakbrowser import launch_async
    except ImportError:
        return {"synced": 0, "errors": ["cloakbrowser not installed — run: pip install cloakbrowser"]}

    session = load_session(PROVIDER)
    headed = force_login or session is None
    account_id = await _resolve_account_id()

    errors: list[str] = []

    browser = await launch_async(headless=not headed)
    try:
        context = await browser.new_context()
        if session:
            await context.add_cookies(session)
        page = await context.new_page()

        await page.goto(FLASH_URL)

        if headed:
            print("[flash] Browser aberto. Faça login e aguarde carregar o extrato.")
            print("[flash] O script continuará automaticamente após o login.")
            try:
                await page.wait_for_url(re.compile(r"/home|/extrato|/statement|/dashboard"), timeout=180_000)
            except Exception:
                await page.wait_for_function(
                    "() => !window.location.pathname.includes('login')",
                    timeout=180_000,
                )
            save_session(PROVIDER, await context.cookies())
            print("[flash] Sessão salva.")

        synced, intercept_errors = await _intercept_and_extract(page, account_id)
        errors.extend(intercept_errors)

        if synced == 0 and not intercept_errors:
            # XHR interception captured nothing; fall back to DOM scraping
            synced, dom_errors = await _dom_extract(page, account_id)
            errors.extend(dom_errors)
    finally:
        await browser.close()

    return {"synced": synced, "errors": errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", action="store_true", help="Force headed login")
    args = parser.parse_args()

    result = asyncio.run(scrape(force_login=args.login))
    print(f"[flash] Sincronizadas: {result['synced']}")
    if result["errors"]:
        print(f"[flash] Erros: {result['errors']}")
