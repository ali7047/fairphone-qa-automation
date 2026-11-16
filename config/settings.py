"""Where the tests run: which shop (region), which language, which address.

    uv run python -m pytest -m smoke --region us
    uv run python -m pytest -m smoke --language nl
    uv run python -m pytest -m smoke --base-url https://<acceptance-url>

Order for each value: command-line option > environment variable > default.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from config.languages import LANGUAGES, Language

ENV_REGION = "REGION"
ENV_LANGUAGE = "SHOP_LANGUAGE"  # not LANGUAGE: Linux already uses that name for its own messages
ENV_BASE_URL = "BASE_URL"


@dataclass(frozen=True)
class Region:
    """One storefront and the business rules that come with it."""

    code: str
    base_url: str
    languages: dict[str, str]
    """Languages tested on this shop, mapped to the path that switches the shop to it."""
    locale: str
    """Browser language. Stays English whatever the shop language, so the cookie dialog is predictable."""
    timezone: str
    currency: str
    currency_symbol: str
    prices_include_tax: bool


REGIONS: dict[str, Region] = {
    "eu": Region(
        code="eu",
        base_url="https://www.fairphone.com",
        languages={"en": "/en", "nl": "/nl"},
        locale="en-GB",
        timezone="Europe/Amsterdam",
        currency="EUR",
        currency_symbol="€",
        prices_include_tax=True,
    ),
    "us": Region(
        code="us",
        base_url="https://us.fairphone.com",
        languages={"en": ""},  # English only: no switch needed
        locale="en-US",
        timezone="America/New_York",
        currency="USD",
        currency_symbol="$",
        prices_include_tax=False,
    ),
}


@dataclass(frozen=True)
class Settings:
    region: Region
    language: Language
    base_url: str

    @property
    def url_prefix(self) -> str:
        """Prefix for page addresses in the chosen language: "" for English (the shop's default), "/nl" for Dutch."""
        return "" if self.language.code == "en" else self.language_path

    @property
    def language_path(self) -> str:
        """Path that switches the shop to the chosen language ("/nl"), or "" if none is needed."""
        return self.region.languages[self.language.code]


def load_settings(
    region_code: str | None = None,
    language_code: str | None = None,
    base_url: str | None = None,
) -> Settings:
    code = _pick(region_code, ENV_REGION, "eu").lower()
    if code not in REGIONS:
        raise ValueError(f"Unknown region {code!r}. Choose one of: {', '.join(REGIONS)}")
    region = REGIONS[code]

    lang = _pick(language_code, ENV_LANGUAGE, "en").lower()
    if lang not in region.languages:
        raise ValueError(
            f"The {region.code} shop is tested in: {', '.join(region.languages)}. Got {lang!r}."
        )

    url = _pick(base_url, ENV_BASE_URL, region.base_url).rstrip("/")
    return Settings(region=region, language=LANGUAGES[lang], base_url=url)


def _pick(argument: str | None, env_var: str, default: str) -> str:
    return (argument or os.getenv(env_var) or default).strip()
