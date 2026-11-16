"""Unit tests for config/settings.py and config/languages.py (no browser, no network).

Why these exist: they decide *which shop the suite talks to*. If BASE_URL were
ignored, a run meant for acceptance would hit the live shop instead.
"""

import pytest

from config.languages import LANGUAGES
from config.settings import REGIONS, load_settings


@pytest.fixture(autouse=True)
def no_environment(monkeypatch):
    """Start every test from a clean environment, whatever the developer's shell has set."""
    for name in ("REGION", "SHOP_LANGUAGE", "BASE_URL"):
        monkeypatch.delenv(name, raising=False)


def test_defaults_to_live_eu_shop_in_english():
    settings = load_settings()
    assert settings.region.code == "eu"
    assert settings.language.code == "en"
    assert settings.base_url == "https://www.fairphone.com"


def test_region_from_environment(monkeypatch):
    monkeypatch.setenv("REGION", "US")
    settings = load_settings()
    assert settings.region.code == "us"
    assert settings.base_url == "https://us.fairphone.com"
    assert settings.region.currency == "USD"


def test_base_url_override_points_suite_at_acceptance(monkeypatch):
    monkeypatch.setenv("BASE_URL", "https://acceptance.example.odoo.com/")
    settings = load_settings()
    assert settings.base_url == "https://acceptance.example.odoo.com"  # trailing slash removed
    assert settings.region.currency == "EUR"  # the region's rules still apply


def test_arguments_win_over_environment(monkeypatch):
    monkeypatch.setenv("REGION", "eu")
    monkeypatch.setenv("BASE_URL", "https://from-env.example.com")
    settings = load_settings(region_code="us", base_url="https://from-arg.example.com")
    assert settings.region.code == "us"
    assert settings.base_url == "https://from-arg.example.com"


def test_unknown_region_fails_clearly():
    with pytest.raises(ValueError, match="Unknown region 'uk'"):
        load_settings(region_code="uk")


def test_dutch_on_eu_shop_switches_with_nl_path():
    settings = load_settings(language_code="nl")
    assert settings.language.code == "nl"
    assert settings.language_path == "/nl"
    assert settings.url_prefix == "/nl"
    assert settings.language.text("cart_heading") == "Winkelwagen"


def test_english_pages_have_no_prefix():
    """English is the shop's default: /shop/cart, not /en/shop/cart (which would redirect every time)."""
    settings = load_settings(language_code="en")
    assert settings.language_path == "/en"
    assert settings.url_prefix == ""


def test_language_from_environment(monkeypatch):
    monkeypatch.setenv("SHOP_LANGUAGE", "nl")
    assert load_settings().language.code == "nl"


def test_us_shop_needs_no_language_switch():
    assert load_settings(region_code="us").language_path == ""


def test_language_the_shop_does_not_have_fails_clearly():
    with pytest.raises(ValueError, match="The us shop is tested in: en. Got 'nl'"):
        load_settings(region_code="us", language_code="nl")


def test_every_language_has_the_same_texts():
    """A text added in English but forgotten in Dutch would only fail later, in a Dutch browser run."""
    english = set(LANGUAGES["en"].texts)
    for code, language in LANGUAGES.items():
        assert set(language.texts) == english, f"{code!r} texts differ from 'en'"


def test_missing_text_fails_with_a_clear_message():
    with pytest.raises(LookupError, match="No 'nl' text for 'not_added_yet'"):
        LANGUAGES["nl"].text("not_added_yet")


def test_every_region_is_valid():
    for region in REGIONS.values():
        assert region.base_url.startswith("https://")
        assert not region.base_url.endswith("/")
        assert set(region.languages) <= set(LANGUAGES), f"{region.code}: language without texts"
