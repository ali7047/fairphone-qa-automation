"""Where the tests run: region profiles and settings.

A *region* is one storefront (EU or US). Each region knows its address, language,
currency and whether prices include tax. Settings pick a region and allow the
address to be overridden, so the same tests can run against an acceptance copy:

    REGION=us BASE_URL=https://<acceptance-url> uv run python -m pytest -m smoke
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    code: str
    base_url: str
    language_path: str
    """Path prefix that pins the shop to English. Odoo redirects `/en/...` on the EU
    shop to the unprefixed English page and remembers the choice in a cookie."""
    locale: str
    timezone: str
    currency: str
    currency_symbol: str
    prices_include_tax: bool


REGIONS: dict[str, Region] = {
    "eu": Region(
        code="eu",
        base_url="https://www.fairphone.com",
        language_path="/en",
        locale="en-GB",
        timezone="Europe/Amsterdam",
        currency="EUR",
        currency_symbol="€",
        prices_include_tax=True,  # Observed 2026-11-15: NL cart total includes 21% VAT
    ),
    "us": Region(
        code="us",
        base_url="https://us.fairphone.com",
        language_path="",  # English only
        locale="en-US",
        timezone="America/New_York",
        currency="USD",
        currency_symbol="$",
        prices_include_tax=False,  # Assumption: sales tax is added at checkout
    ),
}


@dataclass(frozen=True)
class Settings:
    region: Region
    base_url: str


def load_settings(region_code: str | None = None, base_url: str | None = None) -> Settings:
    """Build settings from arguments, then environment variables, then region defaults.

    Order for each value: explicit argument > environment variable > default.
    REGION defaults to "eu"; BASE_URL defaults to the region's live address.
    """
    code = (region_code or os.getenv("REGION") or "eu").strip().lower()
    if code not in REGIONS:
        raise ValueError(f"Unknown region {code!r}. Choose one of: {', '.join(REGIONS)}")
    region = REGIONS[code]
    url = (base_url or os.getenv("BASE_URL") or region.base_url).strip().rstrip("/")
    return Settings(region=region, base_url=url)
