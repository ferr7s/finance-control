from datetime import date, datetime, timezone


DATE_FORMATS = ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y")


def parse_date(value: str) -> datetime:
    text = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return datetime.fromisoformat(text)


def month_bounds(reference: date | None = None) -> tuple[datetime, datetime]:
    ref = reference or datetime.now(timezone.utc).date()
    start = datetime(ref.year, ref.month, 1, tzinfo=timezone.utc)
    if ref.month == 12:
        end = datetime(ref.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(ref.year, ref.month + 1, 1, tzinfo=timezone.utc)
    return start, end
