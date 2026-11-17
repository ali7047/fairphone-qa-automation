"""Base page object: shared by every page."""

from __future__ import annotations

from typing import Self

from playwright.sync_api import Locator, Page, Response

from config.settings import Settings


class BasePage:
    """Holds the browser page, the settings and the header.

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
        so a test can write: cart = CartPage(page, settings).open()
        """
        self.response = self.page.goto(self.settings.url_prefix + (path if path is not None else self.path))
        return self

    @property
    def header(self) -> Locator:
        return self.page.locator("header")

    def header_link(self, key: str) -> Locator:
        """A header menu link by its visible name in the language under test."""
        return self.header.get_by_role("link", name=self.text(key), exact=True)

    @property
    def cart_link(self) -> Locator:
        """Header cart icon; its text is the number of items in the cart.

        Found by where it links to, because its only accessible name is that
        number (see knowledge/site-observations.md). `$=` means "ends with",
        so it also matches the Dutch /nl/shop/cart.
        """
        return self.header.locator('a[href$="/shop/cart"]')
