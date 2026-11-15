"""Base class for page objects: shared navigation and the cookie dialog."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.settings import Region


class BasePage:
    """Every page object gets the Playwright page and the region under test.

    Rule: locators and actions live in page objects; assertions about business
    rules live in the tests.
    """

    path: str = "/"

    def __init__(self, page: Page, region: Region) -> None:
        self.page = page
        self.region = region

    def open(self, path: str | None = None) -> "BasePage":
        """Go to `path` (or the page's own path) on the base URL under test."""
        self.page.goto(path if path is not None else self.path)
        return self

    # --- Shared header elements ------------------------------------------------

    @property
    def cart_link(self) -> Locator:
        """Header cart icon; its text is the number of items in the cart."""
        return self.page.locator('header a[href$="/shop/cart"]').first


class CookieDialog:
    """The consent dialog ("Cookies Please!", DataGrail). Same on EU and US.

    Observed 2026-11-15: buttons "Accept All", "Decline Optional",
    "Customize Settings". We decline optional cookies: it is the privacy-friendly
    choice and it keeps third-party scripts (and their console noise) out of tests.
    """

    HEADING = "Cookies Please!"
    DECLINE_BUTTON = "Decline Optional"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.dialog = page.get_by_role("dialog").filter(
            has=page.get_by_role("heading", name=self.HEADING)
        )
        self.decline_button = self.dialog.get_by_role("button", name=self.DECLINE_BUTTON)

    def handle_automatically(self) -> None:
        """Decline whenever the dialog appears, at any moment in any test.

        Playwright checks for the dialog before every action and auto-waiting
        assertion, runs the handler if it is visible, then waits until it is gone.
        Tests never wait for the dialog or race against it.
        """
        self.page.add_locator_handler(self.dialog, lambda _: self.decline_button.click())
