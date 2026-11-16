"""Pop-ups that cover the page, and how tests answer them.

Cookie dialog and the US "local site" prompt can appear at any moment, so
Playwright's locator handler answers them before every action or check.

The cart offers are a chain (case, then screen protector, then accessories)
that reuses the same buttons, so they are answered as one step right after a
phone is added: CartOffers.skip_all().
"""

from __future__ import annotations

from contextlib import suppress

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from config.settings import Settings


class CookieDialog:
    """Consent dialog on the first visit (EU and US). Always English: the browser stays English."""

    def __init__(self, page: Page) -> None:
        self.dialog = page.get_by_role("dialog").filter(has=page.get_by_role("heading", name="Cookies Please!"))
        self.decline_button = self.dialog.get_by_role("button", name="Decline Optional")

    def handle_automatically(self, page: Page) -> None:
        page.add_locator_handler(self.dialog, lambda _: self.decline_button.click())


class LocalSitePrompt:
    """US shop only: "Visiting from <country>? Switch to the local site?" for visitors outside the US.

    The test chose the US shop on purpose, so it stays.
    """

    def __init__(self, page: Page) -> None:
        self.stay_button = page.get_by_role("button", name="Stay on us.fairphone.com")

    def handle_automatically(self, page: Page) -> None:
        page.add_locator_handler(self.stay_button, lambda _: self.stay_button.click())


class CartOffers:
    """Offers shown in the cart right after a phone is added, one after another:
    1. "Choose your free … Protective Case"   -> "continue without adding"
    2. "Choose your free … Screen Protector"  -> "continue without adding"
    3. "Accessories for …"                    -> "GO TO CART"

    They are styled pop-ups, not real dialogs (no role="dialog"), so they are
    found by their buttons. Tests skip them so the cart holds only what the
    test added. Which offers appear may change with marketing campaigns, so
    skip_all() answers whatever shows up instead of expecting a fixed list.
    """

    MAX_OFFERS = 5  # safety stop: never loop forever if the shop adds a new kind of pop-up

    def __init__(self, page: Page, settings: Settings) -> None:
        text = settings.language.text
        self.page = page
        self.skip = page.get_by_role("link", name=text("offer_skip"), exact=True).filter(visible=True)
        self.go_to_cart = page.get_by_role("link", name=text("offer_go_to_cart"), exact=True).filter(visible=True)
        self.any_offer = self.skip.or_(self.go_to_cart)

    def skip_all(self, first_offer_timeout_ms: int = 5_000) -> int:
        """Answer every offer until none is left. Returns how many were answered.

        The first offer fades in shortly after the cart loads, so wait for it a
        few seconds; if none comes (e.g. no campaign running), carry on.
        Both offers stay in the page while hidden, and the one that is fading
        out still counts as visible for a moment, so each answer waits until
        that button is really gone before looking for the next offer.
        """
        answered = 0
        timeout = first_offer_timeout_ms
        while answered < self.MAX_OFFERS:
            try:
                self.any_offer.first.wait_for(state="visible", timeout=timeout)
            except PlaywrightError:
                return answered
            button = self.go_to_cart.first if self.go_to_cart.count() else self.skip.first
            handle = button.element_handle()
            handle.click()
            # "Go to cart" reloads the page: the button no longer exists, which also means it is gone.
            with suppress(PlaywrightError):
                handle.wait_for_element_state("hidden")
            answered += 1
            timeout = 3_000  # the next offer follows quickly
        raise AssertionError(f"Expected at most {self.MAX_OFFERS} offers in the cart, more kept appearing")


def handle_automatically(page: Page) -> None:
    """Register the pop-ups that can appear at any time. Called once per test by the shared setup."""
    CookieDialog(page).handle_automatically(page)
    LocalSitePrompt(page).handle_automatically(page)
