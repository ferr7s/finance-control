"""
Gmail IMAP email parsing service.

Connects to Gmail via IMAP (App Password), reads unseen transaction emails
from Nubank, Itaú and Flash, parses them with configurable regex patterns,
and imports the transactions using the existing create_transaction pipeline.

Parser patterns are constants at the top of this file — adjust them after
inspecting real email bodies (logged at DEBUG level on first run).
"""
import imaplib
import json
import logging
import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from email import message_from_bytes
from email.message import Message

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.email_sync_job import EmailSyncJob
from app.schemas.transaction import TransactionCreate
from app.services.import_service import import_bank_csv, import_bank_ofx
from app.services.transactions_service import create_transaction, find_duplicate

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bank sender configuration
# Each entry: (provider_name, sender_email, parser_function)
# ---------------------------------------------------------------------------

BANK_SENDERS = [
    ("nubank", "noreply@nubank.com.br"),
    ("itau", "itaucard@itau.com.br"),
]

# Nubank monthly statement email (contains CSV attachment)
NUBANK_STATEMENT_SENDER = "todomundo@nubank.com.br"
NUBANK_STATEMENT_SUBJECT = "Extrato da sua conta do Nubank"

# ---------------------------------------------------------------------------
# Regex patterns — adjust after inspecting real email bodies
# ---------------------------------------------------------------------------

# Nubank: "Compra de R$ 123,45 aprovada em Mercado Livre"
NUBANK_AMOUNT_RE = re.compile(r"R\$\s*([\d\.]+,\d{2})", re.IGNORECASE)
NUBANK_DESC_RE = re.compile(r"aprovada\s+em\s+(.+?)(?:\.|$)", re.IGNORECASE | re.DOTALL)
NUBANK_DATE_RE = re.compile(r"(\d{2}/\d{2}/\d{4})")

# Itaú: "Compra de R$ 123,45 realizada em 23/06/2026 em POSTO SHELL"
ITAU_AMOUNT_RE = re.compile(r"R\$\s*([\d\.]+,\d{2})", re.IGNORECASE)
ITAU_DESC_RE = re.compile(r"em\s+\d{2}/\d{2}/\d{4}\s+em\s+(.+?)(?:\.|$)", re.IGNORECASE | re.DOTALL)
ITAU_DATE_RE = re.compile(r"(\d{2}/\d{2}/\d{4})")

# Flash: "Você usou R$ 123,45 no estabelecimento Restaurante XYZ"
FLASH_AMOUNT_RE = re.compile(r"R\$\s*([\d\.]+,\d{2})", re.IGNORECASE)
FLASH_DESC_RE = re.compile(r"no\s+estabelecimento\s+(.+?)(?:\.|$)", re.IGNORECASE | re.DOTALL)
FLASH_DATE_RE = re.compile(r"(\d{2}/\d{2}/\d{4})")


def _parse_brl(value: str) -> Decimal | None:
    """Convert Brazilian currency string '1.234,56' to Decimal."""
    try:
        normalized = value.replace(".", "").replace(",", ".")
        return Decimal(normalized)
    except InvalidOperation:
        return None


def _parse_date_br(value: str) -> datetime | None:
    """Parse 'DD/MM/YYYY' to UTC datetime."""
    try:
        return datetime.strptime(value, "%d/%m/%Y").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _get_text_body(msg: Message) -> str:
    """Extract plain text or HTML body from an email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                    break
            elif content_type == "text/html" and not body:
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    return body


def _parse_nubank_email(msg: Message) -> dict | None:
    body = _get_text_body(msg)
    logger.debug("Nubank email body:\n%s", body[:2000])

    amount_m = NUBANK_AMOUNT_RE.search(body)
    desc_m = NUBANK_DESC_RE.search(body)
    date_m = NUBANK_DATE_RE.search(body)

    if not amount_m:
        logger.warning("Could not parse amount from Nubank email")
        return None

    amount = _parse_brl(amount_m.group(1))
    description = desc_m.group(1).strip() if desc_m else "Nubank"
    date = _parse_date_br(date_m.group(1)) if date_m else datetime.now(timezone.utc)

    return {"amount": amount, "description": description, "date": date, "provider": "nubank"}


def _parse_itau_email(msg: Message) -> dict | None:
    body = _get_text_body(msg)
    logger.debug("Itaú email body:\n%s", body[:2000])

    amount_m = ITAU_AMOUNT_RE.search(body)
    desc_m = ITAU_DESC_RE.search(body)
    date_m = ITAU_DATE_RE.search(body)

    if not amount_m:
        logger.warning("Could not parse amount from Itaú email")
        return None

    amount = _parse_brl(amount_m.group(1))
    description = desc_m.group(1).strip() if desc_m else "Itaú"
    date = _parse_date_br(date_m.group(1)) if date_m else datetime.now(timezone.utc)

    return {"amount": amount, "description": description, "date": date, "provider": "itau"}


def _parse_flash_email(msg: Message) -> dict | None:
    body = _get_text_body(msg)
    logger.debug("Flash email body:\n%s", body[:2000])

    amount_m = FLASH_AMOUNT_RE.search(body)
    desc_m = FLASH_DESC_RE.search(body)
    date_m = FLASH_DATE_RE.search(body)

    if not amount_m:
        logger.warning("Could not parse amount from Flash email")
        return None

    amount = _parse_brl(amount_m.group(1))
    description = desc_m.group(1).strip() if desc_m else "Flash"
    date = _parse_date_br(date_m.group(1)) if date_m else datetime.now(timezone.utc)

    return {"amount": amount, "description": description, "date": date, "provider": "flash"}


PARSERS = {
    "nubank": _parse_nubank_email,
    "itau": _parse_itau_email,
    "flash": _parse_flash_email,
}


def connect_imap() -> imaplib.IMAP4_SSL:
    settings = get_settings()
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    imap.login(settings.gmail_address, settings.gmail_app_password)
    return imap


def _fetch_recent_from_sender(imap: imaplib.IMAP4_SSL, sender: str, days: int = 30) -> list[tuple[bytes, Message]]:
    """Return (uid, Message) for emails from `sender` in the last `days` days.

    Does NOT filter by read/unread — deduplication via Message-ID prevents
    re-importing emails the user already opened before the sync ran.
    """
    imap.select("INBOX")
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%d-%b-%Y")
    _, data = imap.uid("search", None, f'(FROM "{sender}" SINCE {since})')
    uids = data[0].split() if data and data[0] else []
    result = []
    for uid in uids:
        _, msg_data = imap.uid("fetch", uid, "(RFC822)")
        if msg_data and msg_data[0]:
            result.append((uid, message_from_bytes(msg_data[0][1])))
    return result


def _mark_seen(imap: imaplib.IMAP4_SSL, uid: bytes) -> None:
    imap.uid("store", uid, "+FLAGS", "\\Seen")


def _make_external_id(provider: str, msg: Message) -> str:
    """Build a stable external_id from Message-ID header + provider."""
    msg_id = msg.get("Message-ID", "").strip()
    return f"email:{provider}:{msg_id}" if msg_id else f"email:{provider}:{msg.get('Date', '')}"


def _get_attachment_by_ext(msg: Message, ext: str) -> bytes | None:
    """Return bytes of the first attachment with the given extension."""
    for part in msg.walk():
        filename = part.get_filename() or ""
        if filename.lower().endswith(ext):
            payload = part.get_payload(decode=True)
            if payload:
                return payload
    return None


def _get_statement_attachment(msg: Message) -> tuple[bytes, str] | tuple[None, None]:
    """
    Return (bytes, format) for the best available statement attachment.
    Prefers OFX over CSV because Nubank's CSV export is often empty or header-only.
    """
    ofx = _get_attachment_by_ext(msg, ".ofx")
    if ofx and len(ofx) > 100:
        return ofx, "ofx"
    csv = _get_attachment_by_ext(msg, ".csv")
    if csv and len(csv) > 50:
        return csv, "csv"
    return None, None


def _fetch_nubank_statements(imap: imaplib.IMAP4_SSL) -> list[tuple[bytes, Message]]:
    """
    Return (uid, Message) for Nubank statement/fatura emails from the last 60 days.
    Searches only by sender — Nubank uses different subjects for account statements
    and credit card bills, so we handle all of them.
    """
    imap.select("INBOX")
    since = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%d-%b-%Y")
    _, data = imap.uid("search", None, f'(FROM "{NUBANK_STATEMENT_SENDER}" SINCE {since})')
    uids = data[0].split() if data and data[0] else []
    result = []
    for uid in uids:
        _, msg_data = imap.uid("fetch", uid, "(RFC822)")
        if msg_data and msg_data[0]:
            result.append((uid, message_from_bytes(msg_data[0][1])))
    return result


def run_email_sync(db: Session) -> dict:
    """
    Main entry point: connect to Gmail, parse transaction emails, import.
    Returns {'imported': N, 'ignored': N, 'errors': [...]}.
    """
    settings = get_settings()

    if not settings.gmail_address or not settings.gmail_app_password:
        return {"imported": 0, "ignored": 0, "errors": ["GMAIL_ADDRESS or GMAIL_APP_PASSWORD not configured"]}

    job = EmailSyncJob(status="running")
    db.add(job)
    db.commit()
    db.refresh(job)

    imported = 0
    ignored = 0
    errors: list[str] = []

    try:
        imap = connect_imap()

        for provider, sender in BANK_SENDERS:
            parser = PARSERS[provider]
            try:
                emails = _fetch_recent_from_sender(imap, sender)
                logger.info("Found %d recent emails from %s (%s)", len(emails), provider, sender)
            except Exception as exc:
                errors.append(f"IMAP fetch error for {provider}: {exc}")
                continue

            for uid, msg in emails:
                try:
                    parsed = parser(msg)
                    if not parsed:
                        ignored += 1
                        continue

                    external_id = _make_external_id(provider, msg)
                    if find_duplicate(db, provider, external_id):
                        ignored += 1
                        continue

                    payload = TransactionCreate(
                        external_id=external_id,
                        provider=parsed["provider"],
                        date=parsed["date"],
                        description=parsed["description"],
                        amount=-abs(parsed["amount"]),  # email notifications are always expenses
                        payment_method="email",
                    )
                    create_transaction(db, payload)
                    imported += 1

                except Exception as exc:
                    errors.append(f"{provider} email error: {exc}")
                    ignored += 1

        # Nubank monthly statement (CSV attachment)
        try:
            statement_emails = _fetch_nubank_statements(imap)
            logger.info("Found %d Nubank statement email(s)", len(statement_emails))
            for uid, msg in statement_emails:
                try:
                    attachment, fmt = _get_statement_attachment(msg)
                    if attachment is None:
                        logger.info("Nubank email '%s' has no OFX/CSV attachment, skipping", msg.get("Subject", ""))
                        continue
                    logger.info("Nubank statement using %s (%d bytes): %s", fmt, len(attachment), msg.get("Subject", ""))
                    result = import_bank_ofx(db, attachment) if fmt == "ofx" else import_bank_csv(db, attachment)
                    imported += result.get("imported", 0)
                    ignored += result.get("ignored", 0)
                    errors.extend(result.get("errors", []))
                    logger.info(
                        "Nubank statement imported: %d new, %d ignored",
                        result.get("imported", 0),
                        result.get("ignored", 0),
                    )
                except Exception as exc:
                    errors.append(f"Nubank statement error: {exc}")
        except Exception as exc:
            errors.append(f"Nubank statement fetch error: {exc}")

        imap.logout()

    except Exception as exc:
        errors.append(f"IMAP connection error: {exc}")
        logger.exception("Email sync failed")

    job.status = "done" if not errors else "failed"
    job.imported = imported
    job.ignored = ignored
    job.errors = json.dumps(errors) if errors else None
    job.completed_at = datetime.now(timezone.utc)
    db.commit()

    logger.info("Email sync complete: imported=%d ignored=%d errors=%d", imported, ignored, len(errors))
    return {"imported": imported, "ignored": ignored, "errors": errors}


def get_last_email_sync(db: Session) -> EmailSyncJob | None:
    from sqlalchemy import select
    stmt = select(EmailSyncJob).order_by(EmailSyncJob.started_at.desc()).limit(1)
    return db.scalar(stmt)
