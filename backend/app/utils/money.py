from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


CENT = Decimal("0.01")


def to_decimal(value: Decimal | int | str | float | None) -> Decimal:
    if value is None:
        return Decimal("0.00")
    if isinstance(value, Decimal):
        return value.quantize(CENT, rounding=ROUND_HALF_UP)
    return parse_money(str(value))


def parse_money(value: str) -> Decimal:
    normalized = value.strip().replace("R$", "").replace(" ", "")
    if not normalized:
        return Decimal("0.00")

    if "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")

    try:
        return Decimal(normalized).quantize(CENT, rounding=ROUND_HALF_UP)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid money value: {value}") from exc


def money_to_json(value: Decimal | None) -> str:
    return str(to_decimal(value))
