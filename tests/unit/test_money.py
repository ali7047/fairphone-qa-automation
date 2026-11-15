"""Unit tests for utils.money.parse_price. No browser, run in milliseconds."""

from decimal import Decimal

import pytest

from utils.money import parse_price


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Formats observed on the live shop (2026-11-15)
        ("€599", "599.00"),            # product page
        ("€ 599", "599.00"),           # configurator
        ("€ 599.00", "599.00"),        # cart line and total
        ("€27.95", "27.95"),           # accessory card
        ("$649.99", "649.99"),         # US home page
        ("Delivery: from €3.95", "3.95"),  # currency inside a sentence
        # Thousands and decimal separators in both styles
        ("€1,198.00", "1198.00"),
        ("€ 1.198,00", "1198.00"),
        ("1.234,56 €", "1234.56"),
        ("$1,234.56", "1234.56"),
        ("€1,234", "1234.00"),
        ("€1.234", "1234.00"),
        ("599,00 €", "599.00"),
        # Spacing variants (non-breaking and narrow spaces appear in Odoo output)
        ("€ 599.00", "599.00"),
        ("1 234,56 €", "1234.56"),
        ("CHF 1'234.50", "1234.50"),
        ("  € 0.00  ", "0.00"),
    ],
)
def test_parse_price_reads_shop_formats(text, expected):
    assert parse_price(text) == Decimal(expected)


def test_same_price_in_different_formats_is_equal():
    """The core reason this helper exists: one price, many places."""
    product_page, configurator, cart = "€599", "€ 599", "€ 599.00"
    assert parse_price(product_page) == parse_price(configurator) == parse_price(cart)


def test_result_supports_arithmetic():
    unit = parse_price("€ 599.00")
    assert unit * 2 == parse_price("€ 1,198.00")


def test_two_prices_in_one_text_are_not_glued_together():
    """Guards against reading "€ 599.00 € 103.96" as one big number."""
    assert parse_price("€ 599.00 € 103.96") == Decimal("599.00")


@pytest.mark.parametrize(
    "text",
    ["", "Not yet calculated", "€", "free", None, "€1.2345", "€ 12,3456"],
)
def test_parse_price_rejects_text_without_a_clear_amount(text):
    with pytest.raises(ValueError):
        parse_price(text)
