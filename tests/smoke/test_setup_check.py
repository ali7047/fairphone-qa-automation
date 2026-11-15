"""A quick browser check that the shared setup works: no customer journey yet.

Opens the home page of the configured region and checks what every other
browser test relies on: the shop is reachable, it is in English, prices are in
the region's currency, and the cookie dialog gets out of the way.
"""

import re

import pytest
from playwright.sync_api import Page, expect

from config.settings import Region
from pages.base_page import CookieDialog


@pytest.mark.smoke
def test_setup_home_page_is_english_and_cookie_dialog_is_handled(page: Page, region: Region):
    response = page.goto("/")

    assert response is not None and response.status < 400, (
        f"Home page returned {response.status if response else 'no response'}"
    )
    expect(page.locator("html")).to_have_attribute("lang", re.compile(r"^en"))

    # Playwright runs the cookie handler before every action and assertion,
    # so this check both triggers it and proves the dialog is gone.
    expect(CookieDialog(page).dialog).to_be_hidden()

    price = re.compile(re.escape(region.currency_symbol) + r"\s?\d")
    expect(page.get_by_text(price).filter(visible=True).first).to_be_visible()
