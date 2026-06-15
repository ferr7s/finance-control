from decimal import Decimal

from app.utils.money import parse_money


def test_parse_money_accepts_brazilian_decimal_format():
    assert parse_money("1.234,56") == Decimal("1234.56")
    assert parse_money("-89,90") == Decimal("-89.90")


def test_parse_money_accepts_standard_decimal_format():
    assert parse_money("1234.56") == Decimal("1234.56")
