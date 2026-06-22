"""
Nubank scraper using CloakBrowser on app.nubank.com.br.

First run (no saved session): opens a headed browser so the user can log in manually.
Subsequent runs: loads saved session and runs headless.

Strategy: network interception (captures XHR responses) as primary method;
DOM selector extraction as fallback.

Usage:
  python nubank_scraper.py --login   # force headed login
  python nubank_scraper.py           # use saved session (headless)
"""
import argparse
import asyncio
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

import httpx

from session_manager import load_session, save_session

NUBANK_URL = "https://app.nubank.com.br"
BACKEND_URL = "http://localhost:8000"
PROVIDER = "nubank"

# XHR keywords that identify transaction API responses
_TX_URL_KEYWORDS = ("statements", "transactions", "feed", "bills", "events", "charges")


def _parse_amount(raw) -> Decimal | None:
    if isinstance(raw, (int, float)):
        return Decimal(str(raw))
    cleaned = re.sub(r"[^\d,.-]", "", str(raw)).replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _parse_date(raw) -> str | None:
    if not raw:
        return None
    if isinstance(raw, datetime):
        return raw.isoformat()
    raw = str(raw)
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw[:19], fmt).strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue
    return raw[:19] if len(raw) >= 19 else None


async def _resolve_ids() -> tuple[str | None, str | None]:
    """Returns (account_id, credit_card_id) for provider=nubank."""
    account_id = None
    credit_card_id = None
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BACKEND_URL}/api/accounts", timeout=5)
            for acc in resp.json():
                if acc.get("provider", "").lower() == PROVIDER:
                    account_id = acc["id"]
                    break
        except Exception:
            pass
        try:
            resp = await client.get(f"{BACKEND_URL}/api/credit-cards", timeout=5)
            for card in resp.json():
                if card.get("provider", "").lower() == PROVIDER:
                    credit_card_id = card["id"]
                    break
        except Exception:
            pass
    return account_id, credit_card_id


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


def _extract_items(data: dict | list) -> list[dict]:
    if isinstance(data, list):
        return data
    for key in ("items", "data", "transactions", "statements", "events", "charges", "feed"):
        val = data.get(key)
        if isinstance(val, list) and val:
            return val
    return []


async def _intercept_and_extract(page, account_id, credit_card_id) -> tuple[int, list[str]]:
    """Primary strategy: capture XHR responses containing transaction data."""
    captured_card: list[dict] = []
    captured_account: list[dict] = []
    errors: list[str] = []

    async def on_response(response):
        url = response.url.lower()
        if not any(kw in url for kw in _TX_URL_KEYWORDS):
            return
        try:
            data = await response.json()
            items = _extract_items(data)
            if not items:
                return
            # Heuristic: bills/charges are credit card; feed/events are account
            if any(kw in url for kw in ("bills", "charges", "statements")):
                captured_card.extend(items)
            else:
                captured_account.extend(items)
        except Exception:
            pass

    page.on("response", on_response)

    try:
        await page.wait_for_load_state("networkidle", timeout=20_000)
        # Navigate to transactions/feed to trigger API calls
        feed_link = page.locator(
            "a[href*='transacoes'], a[href*='extrato'], a[href*='feed'], "
            "[data-testid*='feed'], [data-testid*='statement']"
        )
        if await feed_link.count() > 0:
            await feed_link.first.click()
            await page.wait_for_load_state("networkidle", timeout=15_000)
        # Scroll to trigger pagination
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
    except Exception as e:
        errors.append(f"Navegação falhou: {e}")

    synced = 0

    for i, tx in enumerate(captured_card):
        try:
            raw_amount = tx.get("amount") or tx.get("valor") or tx.get("value") or 0
            raw_date = tx.get("time") or tx.get("date") or tx.get("postDate") or ""
            description = (
                tx.get("title") or tx.get("description") or tx.get("descricao") or f"Nubank {i}"
            )
            tx_id = str(tx.get("id") or tx.get("uuid") or f"card-{i}")
            amount = _parse_amount(raw_amount) or Decimal("0")
            tx_date = _parse_date(raw_date) or datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            payload = {
                "external_id": f"nubank-card-{tx_id}",
                "provider": PROVIDER,
                "credit_card_id": credit_card_id,
                "date": tx_date,
                "description": str(description),
                "amount": str(abs(amount)),
                "type": "expense" if float(amount) <= 0 else "income",
                "payment_method": "credit_card",
            }
            ok = await _post_transaction(payload)
            if ok:
                synced += 1
        except Exception as e:
            errors.append(f"Card tx {i}: {e}")

    for i, tx in enumerate(captured_account):
        try:
            raw_amount = tx.get("amount") or tx.get("valor") or tx.get("value") or 0
            raw_date = tx.get("postDate") or tx.get("time") or tx.get("date") or ""
            description = (
                tx.get("title") or tx.get("description") or tx.get("descricao") or f"NuConta {i}"
            )
            tx_id = str(tx.get("id") or tx.get("uuid") or f"account-{i}")
            amount = _parse_amount(raw_amount) or Decimal("0")
            tx_date = _parse_date(raw_date) or datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            payload = {
                "external_id": f"nubank-account-{tx_id}",
                "provider": PROVIDER,
                "account_id": account_id,
                "date": tx_date,
                "description": str(description),
                "amount": str(abs(amount)),
                "type": "expense" if float(amount) < 0 else "income",
            }
            ok = await _post_transaction(payload)
            if ok:
                synced += 1
        except Exception as e:
            errors.append(f"Account tx {i}: {e}")

    return synced, errors


async def _dom_extract(page, account_id, credit_card_id) -> tuple[int, list[str]]:
    """Fallback strategy: extract transactions from DOM elements."""
    errors: list[str] = []
    synced = 0

    rows = await page.query_selector_all(
        "[data-testid*='transaction'], [data-testid*='feed-item'], "
        ".transaction-item, li.charge"
    )
    if not rows:
        errors.append(
            "Seletores DOM não encontrados — inspecione o DOM do Nubank e atualize _dom_extract() em nubank_scraper.py"
        )
        return 0, errors

    for i, row in enumerate(rows):
        try:
            desc_el = await row.query_selector("[data-testid*='title'], .title, span:first-child")
            amount_el = await row.query_selector("[data-testid*='amount'], .amount")
            date_el = await row.query_selector("[data-testid*='date'], time, .date")

            description = (await desc_el.inner_text()).strip() if desc_el else f"Nubank {i}"
            raw_amount = (await amount_el.inner_text()).strip() if amount_el else "0"
            raw_date = (await date_el.inner_text()).strip() if date_el else ""

            amount = _parse_amount(raw_amount) or Decimal("0")
            tx_date = _parse_date(raw_date) or datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            payload = {
                "external_id": f"nubank-dom-{datetime.now().date().isoformat()}-{i}",
                "provider": PROVIDER,
                "credit_card_id": credit_card_id,
                "date": tx_date,
                "description": description,
                "amount": str(abs(amount)),
                "type": "expense",
                "payment_method": "credit_card",
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
    account_id, credit_card_id = await _resolve_ids()

    errors: list[str] = []

    browser = await launch_async(headless=not headed)
    try:
        context = await browser.new_context()
        if session:
            await context.add_cookies(session)
        page = await context.new_page()

        await page.goto(NUBANK_URL)

        if headed:
            print("[nubank] Browser aberto. Faça login com CPF e senha.")
            print("[nubank] O script continuará automaticamente após o login.")
            try:
                await page.wait_for_url(
                    re.compile(r"/(home|dashboard|feed|transacoes|extrato)"),
                    timeout=180_000,
                )
            except Exception:
                await page.wait_for_function(
                    "() => !window.location.pathname.includes('login') && !window.location.pathname.includes('identify')",
                    timeout=180_000,
                )
            save_session(PROVIDER, await context.cookies())
            print("[nubank] Sessão salva.")

        synced, intercept_errors = await _intercept_and_extract(page, account_id, credit_card_id)
        errors.extend(intercept_errors)

        if synced == 0 and not intercept_errors:
            synced, dom_errors = await _dom_extract(page, account_id, credit_card_id)
            errors.extend(dom_errors)
    finally:
        await browser.close()

    return {"synced": synced, "errors": errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", action="store_true", help="Force headed login")
    args = parser.parse_args()

    result = asyncio.run(scrape(force_login=args.login))
    print(f"[nubank] Sincronizadas: {result['synced']}")
    if result["errors"]:
        print(f"[nubank] Erros: {result['errors']}")
