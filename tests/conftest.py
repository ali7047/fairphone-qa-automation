"""Shared setup (fixtures) for all tests.

Every browser test gets:
- a fresh browser context: own cookies, own empty cart;
- the shop, language and address from config/settings.py;
- the shop switched to the chosen language before the test starts;
- the cookie dialog declined automatically.
"""

from __future__ import annotations

import html
import inspect

import pytest
from playwright.sync_api import Page

from config.settings import Region, Settings, load_settings
from pages.base_page import CookieDialog


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("fairphone", "Fairphone shop under test")
    group.addoption("--region", default=None, help="Shop: eu or us (env REGION, default eu).")
    group.addoption(
        "--language",
        default=None,
        help="Shop language: en or nl on eu, en on us (env SHOP_LANGUAGE, default en).",
    )


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    return load_settings(
        region_code=pytestconfig.getoption("--region"),
        language_code=pytestconfig.getoption("--language"),
        base_url=pytestconfig.getoption("--base-url"),
    )


@pytest.fixture(scope="session")
def region(settings: Settings) -> Region:
    return settings.region


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    """Replaces pytest-playwright's base_url, so page.goto("/shop/cart") uses our settings."""
    return settings.base_url


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, settings: Settings) -> dict:
    """Adds the region's browser language and time zone to pytest-playwright's options."""
    return {
        **browser_context_args,
        "base_url": settings.base_url,
        "locale": settings.region.locale,
        "timezone_id": settings.region.timezone,
        "viewport": {"width": 1366, "height": 900},
    }


@pytest.fixture
def page(page: Page, settings: Settings) -> Page:
    """pytest-playwright's page, plus the cookie handler and the chosen shop language."""
    page.set_default_timeout(15_000)
    CookieDialog(page).handle_automatically()
    if settings.language_path:
        # Why this is needed: knowledge/site-observations.md, "Language selection".
        # The server sets the language cookie in its first answer, so there is
        # no need to wait for the whole page (images, scripts) to load.
        page.goto(settings.language_path + "/", wait_until="commit")
    return page


# --- HTML report: show each test's Data / Steps / Expected next to its result ---


def pytest_html_results_table_header(cells: list) -> None:
    cells.insert(2, "<th>Description</th>")


def pytest_html_results_table_row(report: pytest.TestReport, cells: list) -> None:
    description = getattr(report, "description", "")
    cells.insert(2, f'<td style="white-space: pre-line">{html.escape(description)}</td>')


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    report.description = inspect.cleandoc(getattr(item.function, "__doc__", None) or "")
