"""Journey 1: the home page loads and the main navigation works."""

import re

import allure
import pytest
from playwright.sync_api import Page, expect

from config.settings import Settings
from pages.base_page import BasePage
from pages.popups import CookieDialog
from test_data.products import MenuTarget
from utils.evidence import attach_check, attach_data, attach_screenshot, step


@allure.feature("Smoke journeys")
@allure.story("1. Home page and navigation")
@pytest.mark.smoke
def test_home_page_loads_and_shop_menu_opens_a_product_page(page: Page, settings: Settings, menu_target: MenuTarget):
    """
    Data:     shop, language and address from the settings (default: EU shop, English);
              the Shop-menu link to follow from test_data/products.py (EU: "Smartphones").
    Steps:    1. Open the home page in a fresh browser (the cookie dialog is declined).
              2. Read status, page language, header menu, cart icon and prices.
              3. Open the Shop menu and follow the link.
    Expected: status below 400; page in the chosen language; cookie dialog gone;
              "About" menu link in that language; cart icon shows 0; prices in the
              shop's currency; the link opens its page with the expected heading.
    """
    attach_data("Test data: menu link", menu_target)

    with step("1. Open the home page"):
        home = BasePage(page, settings).open("/")
        status = home.response.status if home.response else None
        attach_check("Home page status (expected below 400)", "< 400", status)
        assert status is not None, "Expected an answer from the home page, got none"
        assert status < 400, f"Expected home page status below 400, actual {status}"
        attach_screenshot(page, "Home page")

    with step("2. Check language, cookie dialog, menu, cart icon and prices"):
        expect(page.locator("html"), f"Expected page language {settings.language.code!r}").to_have_attribute(
            "lang", re.compile(rf"^{settings.language.code}\b")
        )
        expect(CookieDialog(page).dialog, "Expected the cookie dialog to be declined").to_be_hidden()
        expect(home.header_link("menu_about"), f"Expected menu link {home.text('menu_about')!r}").to_be_visible()
        expect(home.cart_link, "Expected an empty cart in a fresh browser").to_have_text("0")
        price = re.compile(re.escape(settings.region.currency_symbol) + r"\s?\d")
        expect(
            page.get_by_text(price).filter(visible=True).first, f"Expected prices in {settings.region.currency}"
        ).to_be_visible()

    with step(f"3. Open the Shop menu and follow {menu_target.link!r}"):
        home.header.get_by_role("link", name="Shop", exact=True).hover()
        attach_screenshot(page, "Shop menu open")
        link = home.header.get_by_role("link", name=menu_target.link, exact=True)
        # Keyboard: works for every menu layout and proves the menu is usable without a mouse.
        link.focus()
        link.press("Enter")
        expect(page, f"Expected the page {menu_target.path}").to_have_url(re.compile(re.escape(menu_target.path) + "$"))
        expect(
            page.get_by_role("heading", name=menu_target.heading, level=1).first,
            f"Expected heading {menu_target.heading!r}",
        ).to_be_visible()
        attach_screenshot(page, f"{menu_target.heading} page")
