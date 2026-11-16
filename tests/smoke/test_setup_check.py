"""Checks the shared setup against the real shop before any customer journey runs.

If this test fails, every journey would fail for the same reason, so it tells
you straight away whether the problem is the setup or the journey.
"""

import re

import pytest
from playwright.sync_api import Page, expect

from config.settings import Settings
from pages.base_page import CookieDialog
from pages.home_page import HomePage


@pytest.mark.smoke
def test_home_page_opens_in_chosen_language(page: Page, settings: Settings):
    """
    Data:     shop, language and address from the settings
              (default: EU shop in English at https://www.fairphone.com).
    Steps:    open the home page in a fresh browser; the test setup declines
              the cookie dialog; read status, page language, menu, cart and prices.
    Expected: status below 400; page language is the chosen one; cookie dialog
              gone; "About" menu link in the chosen language ("Over Ons" in Dutch);
              cart shows 0 items; prices in the shop's currency.
    """
    home = HomePage(page, settings).open()

    assert home.response is not None, "Expected an answer from the home page, got none"
    assert home.response.status < 400, (
        f"Expected status below 400, actual {home.response.status} for {page.url}"
    )
    expect(page.locator("html"), f"Expected page language {settings.language.code!r}").to_have_attribute(
        "lang", re.compile(rf"^{settings.language.code}\b")
    )
    expect(CookieDialog(page).dialog, "Expected the cookie dialog to be declined").to_be_hidden()
    expect(
        home.header_link("menu_about"), f"Expected menu link {home.text('menu_about')!r}"
    ).to_be_visible()
    expect(home.cart_link, "Expected an empty cart in a fresh browser").to_have_text("0")

    price = re.compile(re.escape(settings.region.currency_symbol) + r"\s?\d")
    expect(
        page.get_by_text(price).filter(visible=True).first,
        f"Expected prices in {settings.region.currency}",
    ).to_be_visible()
