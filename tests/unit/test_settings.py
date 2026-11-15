"""Unit tests for config.settings. No browser, no network."""

import pytest

from config.settings import REGIONS, load_settings


def test_defaults_to_live_eu_shop(monkeypatch):
    monkeypatch.delenv("REGION", raising=False)
    monkeypatch.delenv("BASE_URL", raising=False)
    settings = load_settings()
    assert settings.region.code == "eu"
    assert settings.base_url == "https://www.fairphone.com"


def test_region_from_environment(monkeypatch):
    monkeypatch.setenv("REGION", "US")
    monkeypatch.delenv("BASE_URL", raising=False)
    settings = load_settings()
    assert settings.region.code == "us"
    assert settings.base_url == "https://us.fairphone.com"
    assert settings.region.currency == "USD"


def test_base_url_override_points_suite_at_acceptance(monkeypatch):
    monkeypatch.setenv("REGION", "eu")
    monkeypatch.setenv("BASE_URL", "https://acceptance.example.odoo.com/")
    settings = load_settings()
    assert settings.base_url == "https://acceptance.example.odoo.com"  # trailing slash removed
    assert settings.region.currency == "EUR"  # region rules still apply


def test_arguments_win_over_environment(monkeypatch):
    monkeypatch.setenv("REGION", "eu")
    monkeypatch.setenv("BASE_URL", "https://from-env.example.com")
    settings = load_settings(region_code="us", base_url="https://from-arg.example.com")
    assert settings.region.code == "us"
    assert settings.base_url == "https://from-arg.example.com"


def test_unknown_region_fails_clearly(monkeypatch):
    monkeypatch.delenv("BASE_URL", raising=False)
    with pytest.raises(ValueError, match="Unknown region 'uk'"):
        load_settings(region_code="uk")


def test_every_region_has_a_secure_base_url():
    for region in REGIONS.values():
        assert region.base_url.startswith("https://")
        assert not region.base_url.endswith("/")
