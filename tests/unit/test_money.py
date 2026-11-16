"""Unit tests for utils.money.parse_price (no browser, no network).

Why these exist: every price check in the browser tests goes through
parse_price. If it misread a price, a browser test would report a shop bug that
isn't there, or miss one that is. These tests prove the reader is right for
every format, before any browser test relies on it.
"""

from decimal import Decimal

import pytest

from utils.money import parse_price

NBSP = "\u00a0"         # non-breaking space: Odoo can put one between symbol and amount
NARROW_NBSP = "\u202f"  # narrow non-breaking space: used as thousands separator in some formats


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Formats shown on the live shop
        ("€599", "599.00"),                # product page
        ("€ 599", "599.00"),               # configurator
        ("€ 599.00", "599.00"),            # cart line and total
        (f"€{NBSP}599.00", "599.00"),      # same, with a non-breaking space
        ("€27.95", "27.95"),               # accessory card
        ("$649.99", "649.99"),             # US shop
        ("Delivery: from €3.95", "3.95"),  # amount inside a sentence
        # Thousands and decimal separators, both styles
        ("€1,198.00", "1198.00"),
        ("€ 1.198,00", "1198.00"),
        ("1.234,56 €", "1234.56"),
        ("$1,234.56", "1234.56"),
        ("€1,234", "1234.00"),
        ("€1.234", "1234.00"),
        ("599,00 €", "599.00"),
        (f"1{NARROW_NBSP}234,56 €", "1234.56"),
        ("CHF 1'234.50", "1234.50"),
        ("  € 0.00  ", "0.00"),
    ],
)
def test_parse_price_reads_shop_formats(text, expected):
    assert parse_price(text) == Decimal(expected)


def test_same_price_in_different_formats_is_equal():
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
