"""Shared setup (fixtures) for all tests.

Every browser test gets:
- a fresh browser context: own cookies, own empty cart;
- the shop, language and address from config/settings.py;
- the shop switched to the chosen language before the test starts;
- the cookie dialog (and the US "local site" prompt) answered automatically;
- report evidence in Allure: run parameters, a final screenshot, and on failure
  the Playwright trace, video and screenshot.
"""

from __future__ import annotations

from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page

from config.settings import Region, Settings, load_settings
from pages import popups
from test_data.products import MenuTarget, ProductChoice, menu_target_for, phone_for
from utils.evidence import attach_screenshot


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
def phone(settings: Settings) -> ProductChoice:
    """The phone the journeys buy in this shop and language (test_data/products.py)."""
    return phone_for(settings.region.code, settings.language.code)


@pytest.fixture(scope="session")
def menu_target(settings: Settings) -> MenuTarget:
    """The Shop-menu link journey 1 follows in this shop and language (test_data/products.py)."""
    return menu_target_for(settings.region.code, settings.language.code)


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
def page(page: Page, settings: Settings, request: pytest.FixtureRequest):
    """pytest-playwright's page, plus pop-up answers, the chosen shop language and report evidence."""
    page.set_default_timeout(15_000)
    popups.handle_automatically(page)

    allure.dynamic.parameter("shop", settings.region.code.upper())
    allure.dynamic.parameter("language", settings.language.code)
    allure.dynamic.parameter("address", settings.base_url)
    allure.dynamic.tag(f"shop:{settings.region.code}", f"language:{settings.language.code}")

    if settings.language_path:
        # Why this is needed: knowledge/site-observations.md, "Language selection".
        # The server sets the language cookie in its first answer, so there is
        # no need to wait for the whole page (images, scripts) to load.
        page.goto(settings.language_path + "/", wait_until="commit")

    yield page

    # What the customer saw when the test ended, pass or fail.
    try:
        attach_screenshot(page, "Screen at the end of the test", full_page=True)
    except Exception:  # noqa: BLE001 - a closed page must not hide the test result
        pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Use each test's Data / Steps / Expected docstring as its description in the report."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "setup" and item.function.__doc__:
        allure.dynamic.description(item.function.__doc__)


_ARTIFACT_NAMES = {
    "trace": ("Playwright trace (open at trace.playwright.dev)", "application/zip", "zip"),
    "video": ("Video of the test", allure.attachment_type.WEBM, None),
    "screenshot": ("Screenshot at failure", allure.attachment_type.PNG, None),
}


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Attach the Playwright trace, video and screenshot of a failed test to its Allure result.

    pytest-playwright keeps them only for failed tests (see pyproject.toml) and
    lists them on the teardown report as playwright_<kind> properties.
    """
    if report.when != "teardown":
        return
    for key, path in report.user_properties:
        kind = key.removeprefix("playwright_")
        if kind in _ARTIFACT_NAMES and Path(path).is_file():
            name, attachment_type, extension = _ARTIFACT_NAMES[kind]
            allure.attach.file(path, name=name, attachment_type=attachment_type, extension=extension)
