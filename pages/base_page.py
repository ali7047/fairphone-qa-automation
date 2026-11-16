"""Base page object and the cookie dialog."""

from __future__ import annotations

from typing import Self

from playwright.sync_api import Locator, Page, Response

from config.settings import Settings


class BasePage:
    """Shared by all page objects: the browser page, the settings and the header.

    Page objects hold locators and actions. Tests hold the expectations.
    """

    path = "/"  # each page object sets its own address, e.g. CartPage.path = "/shop/cart"

    def __init__(self, page: Page, settings: Settings) -> None:
        self.page = page
        self.settings = settings
        self.response: Response | None = None

    def text(self, key: str) -> str:
        """Visible text in the language under test, e.g. text("menu_about") -> "Over Ons"."""
        return self.settings.language.text(key)

    def open(self, path: str | None = None) -> Self:
        """Go to `path`, or to this page's own `path`, on the address under test.

        Keeps the server's answer in `self.response` and returns the page object,
        so a test can write: home = HomePage(page, settings).open()
        """
        self.response = self.page.goto(path if path is not None else self.path)
        return self

    def header_link(self, key: str) -> Locator:
        """A header menu link by its visible name in the language under test."""
        return self.page.locator("header").get_by_role("link", name=self.text(key), exact=True)

    @property
    def cart_link(self) -> Locator:
        """Header cart icon; its text is the number of items in the cart.

        Found by where it links to, because its only accessible name is that
        number (see knowledge/site-observations.md). `$=` means "ends with",
        so it also matches the Dutch /nl/shop/cart.
        """
        return self.page.locator('header a[href$="/shop/cart"]')


class CookieDialog:
    """Consent dialog shown on the first visit, on the EU and US shop.

    The test setup keeps the browser English, so these texts don't change with --language.
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        self.dialog = page.get_by_role("dialog").filter(
            has=page.get_by_role("heading", name="Cookies Please!")
        )
        self.decline_button = self.dialog.get_by_role("button", name="Decline Optional")

    def handle_automatically(self) -> None:
        """Before every action or check: if the dialog is visible, decline it and wait until it is gone."""
        self.page.add_locator_handler(self.dialog, lambda _: self.decline_button.click())
