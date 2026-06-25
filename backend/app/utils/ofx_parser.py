"""
OFX parser for Brazilian bank statements.

Handles both the legacy SGML variant (used by Itaú and most Brazilian banks)
and the newer XML variant. The SGML format has no closing tags for leaf elements,
so standard XML parsers fail — we use regex extraction instead.
"""
import hashlib
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation


# Matches <TAG>value with optional whitespace, no closing tag (SGML style)
_TAG_RE = re.compile(r"<([A-Z0-9.]+)>\s*([^\r\n<]+)", re.IGNORECASE)
_STMTTRN_RE = re.compile(r"<STMTTRN>(.*?)</STMTTRN>", re.IGNORECASE | re.DOTALL)
_ACCTID_RE = re.compile(r"<ACCTID>\s*([^\r\n<]+)", re.IGNORECASE)
_BANKID_RE = re.compile(r"<BANKID>\s*([^\r\n<]+)", re.IGNORECASE)


def _parse_ofx_date(value: str) -> datetime:
    """Parse OFX date: YYYYMMDD or YYYYMMDDHHMMSS[tz]."""
    clean = re.sub(r"\[.*?\]", "", value).strip()
    for fmt in ("%Y%m%d%H%M%S", "%Y%m%d"):
        try:
            return datetime.strptime(clean[:len(fmt.replace("%", "XX").replace("X", ""))], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse OFX date: {value!r}")


def _parse_amount(value: str) -> Decimal:
    try:
        return Decimal(value.strip().replace(",", "."))
    except InvalidOperation:
        raise ValueError(f"Cannot parse amount: {value!r}")


def _extract_tags(block: str) -> dict[str, str]:
    return {m.group(1).upper(): m.group(2).strip() for m in _TAG_RE.finditer(block)}


def _provider_from_bankid(bankid: str) -> str:
    mapping = {
        "341": "itau",
        "033": "santander",
        "001": "bancodobrasil",
        "237": "bradesco",
        "104": "caixa",
        "260": "nubank",
        "336": "c6bank",
    }
    return mapping.get(bankid.strip().lstrip("0"), "banco")


def parse_ofx(content: bytes) -> list[dict]:
    """
    Parse OFX file content and return list of transaction dicts ready for import.
    Each dict has: external_id, date, description, amount, type, provider, payment_method.
    """
    try:
        text = content.decode("latin-1")
    except Exception:
        text = content.decode("utf-8", errors="replace")

    # Detect provider from BANKID
    bankid_m = _BANKID_RE.search(text)
    provider = _provider_from_bankid(bankid_m.group(1)) if bankid_m else "banco"

    transactions = []
    for block_m in _STMTTRN_RE.finditer(text):
        block = block_m.group(1)
        tags = _extract_tags(block)

        fitid = tags.get("FITID", "")
        memo = tags.get("MEMO") or tags.get("NAME") or "Transação"
        trnamt = tags.get("TRNAMT", "0")
        dtposted = tags.get("DTPOSTED", "")

        if not dtposted or not trnamt:
            continue

        try:
            date = _parse_ofx_date(dtposted)
            amount = _parse_amount(trnamt)
        except ValueError:
            continue

        # Build stable external_id
        if fitid:
            external_id = f"ofx:{provider}:{fitid}"
        else:
            raw = f"{provider}:{dtposted}:{trnamt}:{memo}"
            external_id = f"ofx:{provider}:{hashlib.sha256(raw.encode()).hexdigest()[:24]}"

        trntype = tags.get("TRNTYPE", "").upper()
        if trntype in ("CREDIT", "DEP", "INT", "DIV"):
            tx_type = "income"
        else:
            tx_type = "expense"
            if amount > 0:
                amount = -amount

        transactions.append({
            "external_id": external_id,
            "date": date,
            "description": memo,
            "amount": amount,
            "type": tx_type,
            "provider": provider,
            "payment_method": "ofx",
        })

    return transactions
