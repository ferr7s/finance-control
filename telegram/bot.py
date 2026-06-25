"""
Finance Control Telegram Bot

Commands:
  /start    — welcome message
  /resumo   — monthly financial summary
  /saldo    — account balances
  /gastos   — top expense categories
  /sync     — trigger email sync

Free text → AI assistant powered by Claude with financial context.
CSV file → imports via /api/import/bank-csv.
"""
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

API_URL = os.environ["FINANCE_CONTROL_API_URL"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
AGENT_API_KEY = os.environ.get("AGENT_API_KEY", "dev-local-key")
DAILY_SUMMARY_HOUR = int(os.environ.get("DAILY_SUMMARY_HOUR", "8"))
MONTHLY_BUDGET = float(os.environ.get("MONTHLY_BUDGET", "0"))  # 0 = desativado

CHAT_ID_FILE = Path("/app/data/chat_id.txt")
_chat_id: str | None = os.environ.get("TELEGRAM_CHAT_ID") or None


def _load_chat_id() -> None:
    global _chat_id
    if _chat_id:
        return
    if CHAT_ID_FILE.exists():
        _chat_id = CHAT_ID_FILE.read_text().strip() or None


def _save_chat_id(chat_id: str) -> None:
    global _chat_id
    _chat_id = chat_id
    try:
        CHAT_ID_FILE.parent.mkdir(parents=True, exist_ok=True)
        CHAT_ID_FILE.write_text(chat_id)
    except Exception as exc:
        logger.warning("Could not persist chat_id: %s", exc)

_anthropic = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _api(path: str, method: str = "GET", **kwargs) -> dict | list:
    headers = {"Authorization": f"Bearer {AGENT_API_KEY}"}
    with httpx.Client(base_url=API_URL, timeout=30) as client:
        resp = client.request(method, path, headers=headers, **kwargs)
        resp.raise_for_status()
        return resp.json()


def _fmt_brl(value: str | float) -> str:
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(value)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _save_chat_id(str(update.effective_chat.id))
    await update.message.reply_text(
        "👋 Olá! Sou seu assistente financeiro.\n\n"
        "Comandos disponíveis:\n"
        "/resumo — sumário do mês\n"
        "/saldo — saldo das contas\n"
        "/gastos — maiores categorias de gasto\n"
        "/sync — sincronizar emails do banco\n\n"
        "Você também pode me enviar um arquivo CSV para importar transações "
        "ou fazer qualquer pergunta sobre suas finanças.\n\n"
        f"✅ Notificações diárias ativadas às {DAILY_SUMMARY_HOUR:02d}:00."
    )


def _summary_by_provider(transactions: list) -> dict:
    """Aggregate income/expenses per provider from transaction list."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    result: dict[str, dict] = {}
    for t in transactions:
        try:
            date = datetime.fromisoformat(t["date"].replace("Z", "+00:00"))
        except Exception:
            continue
        if date.year != now.year or date.month != now.month:
            continue
        provider = t.get("provider", "outros")
        amount = float(t.get("amount", 0))
        if provider not in result:
            result[provider] = {"income": 0.0, "expenses": 0.0}
        if amount >= 0:
            result[provider]["income"] += amount
        else:
            result[provider]["expenses"] += abs(amount)
    return result


async def cmd_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        lines = _build_resumo_lines()
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as exc:
        await update.message.reply_text(f"Erro ao buscar resumo: {exc}")


async def cmd_gastos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = _api("/api/dashboard/category-breakdown")
        if not data:
            await update.message.reply_text("Nenhum dado de categoria disponível.")
            return
        lines = ["📂 *Gastos por categoria*\n"]
        for item in data[:8]:
            pct = item.get("percentage", 0)
            lines.append(f"• {item['category']}: {_fmt_brl(item['amount'])} ({pct:.1f}%)")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as exc:
        await update.message.reply_text(f"Erro ao buscar categorias: {exc}")


async def cmd_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        accounts = _api("/api/accounts")
        if not accounts:
            await update.message.reply_text("Nenhuma conta cadastrada.")
            return

        provider_labels = {
            "nubank": "🟣 Nubank",
            "itau": "🔵 Itaú",
            "flash": "🟠 Flash",
        }

        lines = ["🏦 *Saldo das contas*\n"]
        total = 0.0
        for acc in accounts:
            balance = float(acc.get("current_balance", 0))
            total += balance
            provider = acc.get("provider", "").lower()
            label = provider_labels.get(provider, f"🏦 {acc.get('provider', 'Outro')}")
            name = acc.get("name", "")
            sign = "+" if balance >= 0 else ""
            lines.append(f"{label} — {name}: {sign}{_fmt_brl(balance)}")

        lines.append(f"\n*Total: {_fmt_brl(total)}*")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as exc:
        await update.message.reply_text(f"Erro ao buscar saldo: {exc}")


def _build_resumo_lines() -> list[str]:
    """Build resumo lines reused by cmd_resumo and daily notification."""
    data = _api("/api/dashboard/summary")
    lines = [
        "📊 *Resumo do mês*\n",
        f"💰 Receitas: {_fmt_brl(data.get('monthly_income', 0))}",
        f"💸 Despesas: {_fmt_brl(data.get('monthly_expenses', 0))}",
        f"📈 Resultado: {_fmt_brl(data.get('monthly_result', 0))}",
        f"🏦 Patrimônio líquido: {_fmt_brl(data.get('net_worth', 0))}",
    ]
    if data.get("warnings"):
        lines.append("\n⚠️ " + "\n⚠️ ".join(data["warnings"]))

    # Per-provider breakdown
    try:
        transactions = _api("/api/transactions?limit=500")
        by_provider = _summary_by_provider(transactions)
        provider_labels = {
            "nubank": "🟣 Nubank",
            "itau": "🔵 Itaú",
            "flash": "🟠 Flash",
        }
        known = {k: v for k, v in by_provider.items() if k in provider_labels}
        if known:
            lines.append("\n─── Por banco ───")
            for provider, label in provider_labels.items():
                if provider not in known:
                    continue
                vals = known[provider]
                lines.append(f"\n{label}")
                if vals["income"]:
                    lines.append(f"  💰 Receitas: {_fmt_brl(vals['income'])}")
                lines.append(f"  💸 Despesas: {_fmt_brl(vals['expenses'])}")
    except Exception:
        pass

    # Credit card bills due soon
    try:
        cards = _api("/api/dashboard/credit-card-summary")
        today = datetime.now(timezone.utc)
        due_alerts = []
        for card in cards:
            due_day = card.get("due_day")
            amount = float(card.get("open_bill_amount", 0))
            if not due_day or amount <= 0:
                continue
            due_date = today.replace(day=due_day)
            if due_date < today:
                # already past this month, check next month
                import calendar
                last_day = calendar.monthrange(today.year, today.month)[1]
                if today.day > due_day:
                    next_month = today.month % 12 + 1
                    next_year = today.year + (1 if today.month == 12 else 0)
                    due_date = today.replace(year=next_year, month=next_month, day=due_day)
            days_left = (due_date.date() - today.date()).days
            if 0 <= days_left <= 5:
                name = card.get("name", card.get("provider", "Cartão"))
                due_alerts.append((days_left, name, amount))

        if due_alerts:
            lines.append("\n─── Faturas vencendo ───")
            for days_left, name, amount in sorted(due_alerts):
                if days_left == 0:
                    when = "hoje"
                elif days_left == 1:
                    when = "amanhã"
                else:
                    when = f"em {days_left} dias"
                lines.append(f"💳 {name}: {_fmt_brl(amount)} vence {when}")
    except Exception:
        pass

    # Monthly budget progress
    if MONTHLY_BUDGET > 0:
        try:
            expenses = float(data.get("monthly_expenses", 0))
            pct = (expenses / MONTHLY_BUDGET) * 100
            bar_filled = int(pct / 10)
            bar = "█" * bar_filled + "░" * (10 - bar_filled)
            icon = "🔴" if pct >= 100 else "🟡" if pct >= 80 else "🟢"
            lines.append(
                f"\n{icon} *Meta do mês*\n"
                f"`[{bar}]` {pct:.0f}%\n"
                f"{_fmt_brl(expenses)} de {_fmt_brl(MONTHLY_BUDGET)}"
            )
        except Exception:
            pass

    return lines


async def send_weekly_summary(app: Application) -> None:
    """Send weekly summary every Monday with last 7 days breakdown."""
    if not _chat_id:
        return
    try:
        from datetime import timedelta
        today = datetime.now(timezone.utc)
        week_start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        week_end = today.strftime("%Y-%m-%d")

        transactions = _api(f"/api/transactions?start_date={week_start}&end_date={week_end}&limit=500")

        expenses = 0.0
        income = 0.0
        category_totals: dict[str, float] = {}
        for t in transactions:
            amount = float(t.get("amount", 0))
            if amount < 0:
                expenses += abs(amount)
                cat = t.get("category") or "outros"
                category_totals[cat] = category_totals.get(cat, 0) + abs(amount)
            else:
                income += amount

        top3 = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:3]

        lines = [
            "📅 *Resumo da semana*\n",
            f"💸 Gasto total: {_fmt_brl(expenses)}",
        ]
        if income:
            lines.append(f"💰 Receitas: {_fmt_brl(income)}")
        if top3:
            lines.append("\nTop categorias:")
            for cat, val in top3:
                lines.append(f"  • {cat}: {_fmt_brl(val)}")

        await app.bot.send_message(chat_id=_chat_id, text="\n".join(lines), parse_mode="Markdown")
        logger.info("Weekly summary sent")
    except Exception as exc:
        logger.exception("Failed to send weekly summary: %s", exc)


async def send_monthly_summary(app: Application) -> None:
    """Send monthly closing summary on the last day of the month."""
    if not _chat_id:
        return
    try:
        import calendar
        today = datetime.now(timezone.utc)

        # Current month
        current = _api("/api/dashboard/summary")
        curr_expenses = float(current.get("monthly_expenses", 0))
        curr_income = float(current.get("monthly_income", 0))
        curr_result = float(current.get("monthly_result", 0))

        # Previous month totals via transactions
        first_of_month = today.replace(day=1)
        prev_month_end = first_of_month - __import__("datetime").timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)
        prev_txns = _api(
            f"/api/transactions"
            f"?start_date={prev_month_start.strftime('%Y-%m-%d')}"
            f"&end_date={prev_month_end.strftime('%Y-%m-%d')}"
            f"&limit=500"
        )
        prev_expenses = sum(abs(float(t["amount"])) for t in prev_txns if float(t["amount"]) < 0)

        diff = curr_expenses - prev_expenses
        diff_pct = (diff / prev_expenses * 100) if prev_expenses else 0
        trend = "📈" if diff > 0 else "📉"
        month_name = today.strftime("%B/%Y")

        lines = [
            f"📆 *Fechamento de {month_name}*\n",
            f"💰 Receitas: {_fmt_brl(curr_income)}",
            f"💸 Despesas: {_fmt_brl(curr_expenses)}",
            f"📊 Resultado: {_fmt_brl(curr_result)}",
            f"\n{trend} Despesas vs mês anterior: {'+' if diff >= 0 else ''}{_fmt_brl(diff)} ({diff_pct:+.1f}%)",
        ]

        if MONTHLY_BUDGET > 0:
            pct = (curr_expenses / MONTHLY_BUDGET) * 100
            icon = "🔴" if pct >= 100 else "🟡" if pct >= 80 else "🟢"
            lines.append(f"{icon} Meta atingida: {pct:.0f}% ({_fmt_brl(curr_expenses)} de {_fmt_brl(MONTHLY_BUDGET)})")

        lines.append("\n📎 Lembre-se de exportar e enviar o CSV do mês dos seus bancos.")

        await app.bot.send_message(chat_id=_chat_id, text="\n".join(lines), parse_mode="Markdown")
        logger.info("Monthly summary sent")
    except Exception as exc:
        logger.exception("Failed to send monthly summary: %s", exc)


async def send_daily_summary(app: Application) -> None:
    """Send daily summary notification to saved chat_id."""
    if not _chat_id:
        logger.warning("Daily summary skipped — no chat_id saved. Send /start to the bot first.")
        return
    try:
        lines = _build_resumo_lines()
        await app.bot.send_message(
            chat_id=_chat_id,
            text="\n".join(lines),
            parse_mode="Markdown",
        )
        logger.info("Daily summary sent to chat_id %s", _chat_id)
    except Exception as exc:
        logger.exception("Failed to send daily summary: %s", exc)


async def cmd_sync(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🔄 Sincronizando emails do banco...")
    try:
        result = _api("/api/email-sync", method="POST")
        imported = result.get("imported", 0)
        ignored = result.get("ignored", 0)
        errors = result.get("errors", [])
        msg = f"✅ Sincronização concluída!\n• Importadas: {imported}\n• Ignoradas: {ignored}"
        if errors:
            msg += f"\n⚠️ Erros: {len(errors)}\n" + "\n".join(f"  - {e}" for e in errors[:3])
        await update.message.reply_text(msg)
    except Exception as exc:
        await update.message.reply_text(f"Erro ao sincronizar: {exc}")


# ---------------------------------------------------------------------------
# CSV file handler
# ---------------------------------------------------------------------------

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    doc = update.message.document
    fname = doc.file_name.lower()
    is_csv = fname.endswith(".csv")
    is_ofx = fname.endswith(".ofx")

    if not is_csv and not is_ofx:
        await update.message.reply_text("Por favor, envie um arquivo .csv ou .ofx para importar transações.")
        return

    fmt = "OFX" if is_ofx else "CSV"
    await update.message.reply_text(f"📥 Recebendo arquivo {fmt}...")
    try:
        file = await context.bot.get_file(doc.file_id)
        file_bytes = await file.download_as_bytearray()

        endpoint = "/api/import/bank-ofx" if is_ofx else "/api/import/bank-csv"
        mime = "application/octet-stream" if is_ofx else "text/csv"

        with httpx.Client(base_url=API_URL, timeout=60) as client:
            resp = client.post(
                endpoint,
                files={"file": (doc.file_name, bytes(file_bytes), mime)},
            )
            resp.raise_for_status()
            result = resp.json()

        imported = result.get("imported", 0)
        ignored = result.get("ignored", 0)
        errors = result.get("errors", [])
        msg = f"✅ {fmt} importado!\n• Novas transações: {imported}\n• Ignoradas (duplicatas): {ignored}"
        if errors:
            msg += f"\n⚠️ Erros em {len(errors)} linhas"
        await update.message.reply_text(msg)

    except Exception as exc:
        await update.message.reply_text(f"Erro ao importar {fmt}: {exc}")


# ---------------------------------------------------------------------------
# Free-text AI handler
# ---------------------------------------------------------------------------

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _anthropic:
        await update.message.reply_text(
            "Use os comandos disponíveis:\n"
            "/resumo — sumário financeiro do mês\n"
            "/gastos — gastos por categoria\n"
            "/sync — sincronizar emails do banco\n\n"
            "Você também pode enviar um arquivo .csv para importar transações."
        )
        return

    user_msg = update.message.text
    await update.message.reply_chat_action("typing")

    # Fetch financial context
    financial_context = ""
    try:
        summary = _api("/api/dashboard/summary")
        categories = _api("/api/dashboard/category-breakdown")
        financial_context = (
            f"Resumo financeiro do usuário:\n"
            f"- Receitas do mês: {_fmt_brl(summary.get('monthly_income', 0))}\n"
            f"- Despesas do mês: {_fmt_brl(summary.get('monthly_expenses', 0))}\n"
            f"- Resultado do mês: {_fmt_brl(summary.get('monthly_result', 0))}\n"
            f"- Patrimônio líquido: {_fmt_brl(summary.get('net_worth', 0))}\n"
            f"\nTop categorias de gasto:\n"
            + "\n".join(
                f"  - {c['category']}: {_fmt_brl(c['amount'])} ({c.get('percentage', 0):.1f}%)"
                for c in categories[:5]
            )
        )
    except Exception:
        financial_context = "Dados financeiros indisponíveis no momento."

    system_prompt = (
        "Você é um assistente financeiro pessoal inteligente. "
        "Responda sempre em português brasileiro, de forma clara e objetiva. "
        "Use os dados financeiros abaixo como contexto para suas respostas.\n\n"
        f"{financial_context}"
    )

    try:
        response = _anthropic.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_msg}],
        )
        reply = response.content[0].text
        await update.message.reply_text(reply)
    except Exception as exc:
        logger.exception("Claude API error")
        await update.message.reply_text(f"Erro ao consultar IA: {exc}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _load_chat_id()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("resumo", cmd_resumo))
    app.add_handler(CommandHandler("saldo", cmd_saldo))
    app.add_handler(CommandHandler("gastos", cmd_gastos))
    app.add_handler(CommandHandler("sync", cmd_sync))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_daily_summary,
        "cron",
        hour=DAILY_SUMMARY_HOUR,
        minute=0,
        kwargs={"app": app},
        id="daily_summary",
    )
    scheduler.add_job(
        send_weekly_summary,
        "cron",
        day_of_week="mon",
        hour=DAILY_SUMMARY_HOUR,
        minute=5,
        kwargs={"app": app},
        id="weekly_summary",
    )
    scheduler.add_job(
        send_monthly_summary,
        "cron",
        day="last",
        hour=20,
        minute=0,
        kwargs={"app": app},
        id="monthly_summary",
    )
    scheduler.start()
    logger.info(
        "Agendado: diário %02d:00 | semanal segunda %02d:05 | mensal último dia 20:00",
        DAILY_SUMMARY_HOUR, DAILY_SUMMARY_HOUR,
    )

    logger.info("Bot iniciado. Aguardando mensagens...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
