"""Checkout: choose guest checkout and reach the address form.

Safety: the address form must never reach the live shop. Typing into a field
is only allowed after block_form_submits() is active, which stops every
non-GET request to checkout, address, payment and sign-up addresses before it
leaves the browser (knowledge/production-rules.md).
"""

from __future__ import annotations

import re

from playwright.sync_api import Locator, Route

from pages.base_page import BasePage

# Addresses that would create or change something in the shop when posted to.
_SUBMIT_TARGETS = re.compile(
    r"/(shop/(address|checkout|confirm_order|payment)|payment/|web/signup|web/login|website/form)"
)


class CheckoutPage(BasePage):
    """The "How would you like to complete your order?" panel and the address page behind it."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.blocked_submits: list[str] = []
        self._submits_blocked = False

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

    def field_is_flagged(self, key: str) -> Locator:
        """The field, but only if the shop has marked it as wrong.

        Odoo marks a wrong field with aria-invalid="true" or the CSS state class
        "is-invalid" (Bootstrap's standard for form errors, not a styling choice).
        The locator matches nothing while the field is accepted.
        """
        return self.field(key).and_(self.page.locator("[aria-invalid=true], .is-invalid"))

    # --- Typing safely ---------------------------------------------------------

    def block_form_submits(self) -> None:
        """Stop any form post to checkout/payment/sign-up before it leaves the browser.

        Reading pages (GET) still works. Every blocked attempt is recorded in
        `blocked_submits`, so a test can prove nothing was sent.
        """

        def stop(route: Route) -> None:
            if route.request.method == "GET":
                route.continue_()
            else:
                self.blocked_submits.append(f"{route.request.method} {route.request.url}")
                route.abort()

        self.page.route(_SUBMIT_TARGETS, stop)
        self._submits_blocked = True

    def type_into(self, key: str, value: str) -> None:
        """Type `value` into a field and leave it (Tab), as a customer would. Never submits.

        Refuses to type unless block_form_submits() is active, so a pressed
        Enter or an auto-submit can never reach the live shop.
        """
        if not self._submits_blocked:
            raise RuntimeError("Call block_form_submits() before typing into the checkout form")
        field = self.field(key)
        field.fill(value)
        field.press("Tab")
