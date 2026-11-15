"""Turn price text from the shop into numbers that can be compared.

The shop shows the same price in different ways:
"€599" (product page), "€ 599" (configurator), "€ 599.00" (cart), "$649.99" (US).
Comparing these as text would fail, so tests always compare Decimal values.
"""

from __future__ import annotations

import re
from decimal import Decimal

# One well-formed amount. Grouped forms are tried before plain ones, so
# "1,234.56" is read as one number and not as "1" followed by noise.
_AMOUNT = re.compile(
    r"(?<![\d.,'])"
    r"(?:"
    r"\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?"                    # 1,234.56  (English)
    r"|\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?"                   # 1.234,56  (Dutch/German)
    r"|\d{1,3}(?:[   ']\d{3})+(?:[.,]\d{1,2})?"  # 1 234,56 / 1'234.50
    r"|\d+(?:[.,]\d{1,2})?"                                # 599 / 599.00 / 599,00
    r")"
    r"(?!\d|[.,]\d)"
)
_DECIMALS = re.compile(r"[.,](\d{1,2})$")


def parse_price(text: str | None) -> Decimal:
    """Return the first amount in `text` as a Decimal with two decimals.

    Reads both separator styles ("1,234.56" and "1.234,56"). A single comma or
    dot followed by exactly three digits is a thousands separator ("1,234");
    followed by one or two digits it is the decimal mark ("599,00", "27.95").

    Raises ValueError when no well-formed amount is found, so a broken page
    fails loudly instead of quietly comparing wrong numbers.
    """
    if not text:
        raise ValueError(f"No price found in {text!r}")
    match = _AMOUNT.search(text)
    if not match:
        raise ValueError(f"No price found in {text!r}")

    amount = match.group()
    decimals = _DECIMALS.search(amount)
    whole = amount[: decimals.start()] if decimals else amount
    whole_digits = re.sub(r"\D", "", whole)
    cents = (decimals.group(1) if decimals else "0").ljust(2, "0")
    return Decimal(f"{whole_digits}.{cents}")
