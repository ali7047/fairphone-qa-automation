"""Shared test setup (fixtures) for every test in this folder and below.

What every browser test gets automatically:
- the region and base URL from config/settings.py (REGION, BASE_URL),
- a fresh browser context per test (own cookies, own empty cart),
- the browser language and time zone of the region,
- the cookie dialog declined automatically whenever it appears.

Options:
    --region eu|us      storefront to test (default: REGION env var, else eu)
    --base-url URL      address to test (default: BASE_URL env var, else the region's live shop)
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from config.settings import Region, Settings, load_settings
from pages.base_page import CookieDialog


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--region",
        action="store",
        default=None,
        help="Storefront to test: eu or us (default: REGION env var, else eu).",
    )


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    return load_settings(
        region_code=pytestconfig.getoption("--region"),
        base_url=pytestconfig.getoption("--base-url"),
    )


@pytest.fixture(scope="session")
def region(settings: Settings) -> Region:
    return settings.region


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    """Overrides pytest-playwright's base_url so page.goto("/cart") uses our settings."""
    return settings.base_url


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, settings: Settings) -> dict:
    """Extend pytest-playwright's context options with the region's locale and time zone."""
    return {
        **browser_context_args,
        "base_url": settings.base_url,
        "locale": settings.region.locale,
        "timezone_id": settings.region.timezone,
        "viewport": {"width": 1366, "height": 900},
    }


@pytest.fixture
def page(page: Page, settings: Settings) -> Page:
    """pytest-playwright's page, plus: cookie dialog handled and shop pinned to English.

    The EU shop picks its language from the visitor's location and remembers it
    in a cookie. Opening the English path once pins the session to English, so
    selectors that use visible English text stay valid on every runner.
    """
    page.set_default_timeout(15_000)
    CookieDialog(page).handle_automatically()
    if settings.region.language_path:
        page.goto(settings.region.language_path + "/")
    return page
