"""Checkout: choose guest checkout and reach the address form. Never fills it in."""

from __future__ import annotations

from playwright.sync_api import Locator

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """The "How would you like to complete your order?" panel and the address page behind it.

    Safety: this page object has no method that types or submits anything.
    The journey must stop at the address form (knowledge/production-rules.md).
    """

    @property
    def guest_checkout_link(self) -> Locator:
        return self.page.get_by_role("link", name=self.text("checkout_as_guest"))

    def continue_as_guest(self) -> None:
        self.guest_checkout_link.click()
        self.page.wait_for_url("**/shop/address**")

    @property
    def heading(self) -> Locator:
        return self.page.get_by_role("heading", name=self.text("checkout_heading"), exact=True)

    @property
    def address_heading(self) -> Locator:
        return self.page.get_by_role("heading", name=self.text("address_heading"), exact=True)

    def field(self, key: str) -> Locator:
        """An address field by its visible label, e.g. field("first_name")."""
        return self.page.get_by_role("textbox", name=self.text(key), exact=True)
